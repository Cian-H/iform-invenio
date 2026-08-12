import typer
from loguru import logger
from plumbum import FG, local
from plumbum.cmd import docker, git, uv

from cli.config import config
from cli.utils import docker_compose, get_project_root, get_repo_dir

app = typer.Typer(help="Deployment Management Tool")

ROOT_DIR = get_project_root()
REPO_DIR = get_repo_dir()
VERSIONS_DIR = ROOT_DIR / "versions"


import time

import requests


def healthcheck():
    """Poll the localhost health endpoint to verify the stack is up."""
    logger.info("Running healthcheck...")
    for _ in range(3):
        try:
            response = requests.get("http://localhost/health", timeout=5)
            if response.status_code == 200:
                logger.success("Healthcheck passed.")
                return
        except requests.RequestException:
            pass
        logger.info("Waiting 5 seconds before retrying...")
        time.sleep(5)

    logger.error("Healthcheck failed.")
    raise typer.Exit(1)


@app.command()
def tag_version():
    """Tag current version using bumpver and save docker images state."""
    VERSIONS_DIR.mkdir(exist_ok=True)

    logger.info("Bumping version with bumpver...")
    try:
        uv("run", "bumpver", "update")
    except Exception as e:
        logger.error(f"Bumpver failed: {e}")

    current_tag = git("describe", "--tags", "--abbrev=0").strip()
    logger.info(f"Current tag is {current_tag}")

    with local.cwd(REPO_DIR):
        images_output = docker_compose("images")

    version_file = VERSIONS_DIR / f"{current_tag}.txt"

    with open(version_file, "w") as f:
        for line in images_output.splitlines():
            if "REPOSITORY" not in line:
                f.write(line + "\n")

    logger.success(f"Saved image states to {version_file}")


@app.command()
def rollback(version: str = typer.Option(None, help="Specific tag to rollback to")):
    """Rollback to a specific version or latest."""
    current_branch = git("branch", "--show-current").strip()

    if not version:
        tags = git("tag", "--sort=-v:refname").splitlines()
        if not tags:
            logger.error("No tags found.")
            raise typer.Exit(1)
        version = tags[0]

    version_file = VERSIONS_DIR / f"{version}.txt"

    if not version_file.exists():
        logger.error(f"No version file found for {version} at {version_file}")
        raise typer.Exit(1)

    logger.info(f"Pulling old images for {version}...")
    with open(version_file, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                repo, tag = parts[0], parts[1]
                logger.info(f"Pulling {repo}:{tag}")
                docker("pull", f"{repo}:{tag}")

    logger.info(f"Rolling back to {version}...")
    git("checkout", version)

    try:
        with local.cwd(REPO_DIR):
            docker_compose("down")
            docker_compose("build")
            docker_compose("up", "-d")
    finally:
        if current_branch:
            git("switch", current_branch)
            logger.success(
                f"Rollback to {version} complete. Returned git to {current_branch}."
            )
        else:
            logger.success(
                f"Rollback to {version} complete. Remained in detached HEAD."
            )


@app.command()
def cleanup_versions():
    """Keep only the latest 5 version tags and delete older ones."""
    tags = git("tag", "--sort=-v:refname").splitlines()
    tags_to_delete = tags[5:]

    for tag in tags_to_delete:
        if not tag:
            continue
        git("tag", "-d", tag)
        version_file = VERSIONS_DIR / f"{tag}.txt"
        if version_file.exists():
            version_file.unlink()
        logger.info(f"Cleaned up {tag}")


@app.command()
def prod_deploy():
    """First-time deployment to production."""

    logger.info("Deploying to production (first-time)...")
    git["switch", "prod"] & FG
    git["pull", "origin", "prod"] & FG

    with local.env(INVENIO_THEME_IFORM_PRODUCTION="true"), local.cwd(REPO_DIR):
        docker[
            "build",
            "-t",
            config.docker_image_name,
            "--build-arg",
            "INSTALL_LOCAL_WHEELS=false",
            ".",
        ] & FG
        docker_compose("up", "-d", "--wait")

        setup_cmd = "invenio db init && invenio db create && invenio alembic upgrade heads && invenio collect -v && invenio index init"
        docker_compose("exec", "worker", "bash", "-c", setup_cmd)

    logger.success("Production deployment complete!")


@app.command()
def prod_update(
    auto_rollback: bool = typer.Option(
        False, help="Automatically rollback if healthcheck fails"
    ),
):
    """Update the application stack, with optional auto-rollback."""
    lock_file = ROOT_DIR / "update.lock"

    if lock_file.exists():
        logger.error("Update already in progress (update.lock exists).")
        raise typer.Exit(1)

    logger.info("Updating production deployment...")

    try:
        lock_file.touch()

        logger.info("Tagging current version for potential rollback...")
        tag_version()

        git["switch", "prod"] & FG
        git["pull", "origin", "prod"] & FG
        with local.env(INVENIO_THEME_IFORM_PRODUCTION="true"), local.cwd(REPO_DIR):
            docker_compose("pull")
            docker[
                "build",
                "-t",
                config.docker_image_name,
                "--build-arg",
                "INSTALL_LOCAL_WHEELS=false",
                ".",
            ] & FG
            docker_compose("up", "-d", "--wait")

            update_cmd = "invenio alembic upgrade heads && invenio collect -v"
            docker_compose("exec", "worker", "bash", "-c", update_cmd)

        try:
            healthcheck()
        except typer.Exit:
            if auto_rollback:
                logger.warning("Healthcheck failed, triggering auto-rollback...")
                rollback(None)
            else:
                logger.error(
                    "Healthcheck failed. Consider running 'uv run cli deploy rollback' manually."
                )
                raise

        cleanup_versions()
        logger.success("Production update complete!")

    finally:
        if lock_file.exists():
            lock_file.unlink()


@app.command()
def merge_and_push_prod():
    """Merge main into prod and push all branches."""
    logger.info("Merging main into prod...")
    current = git("branch", "--show-current").strip()

    try:
        git["switch", "prod"] & FG
        git["merge", "main"] & FG
        git["switch", "main"] & FG
        logger.info("Pushing all branches...")
        git["push", "--all"] & FG
        logger.success("Merged and pushed to production.")
    finally:
        if current:
            git("switch", current)


@app.command()
def prod_clean():
    """Clean all production build artifacts."""
    logger.info("Cleaning production build artifacts...")
    from plumbum.cmd import find, rm

    root = get_project_root()
    with local.cwd(root):
        rm("-rf", ".venv", "build", "dist")
        for egg in local.path(".") // "*.egg-info":
            rm("-rf", egg)

        try:
            find(
                ".",
                "-type",
                "d",
                "-name",
                "__pycache__",
                "-exec",
                "rm",
                "-r",
                "{}",
                "+",
            )
        except Exception:
            pass

        rm("-rf", "static", "node_modules")

    logger.success("Clean complete. Re-create environment before next deploy.")


@app.command()
def init_ssl(
    email: str = typer.Argument(
        ..., help="Email address for Let's Encrypt registration"
    ),
    domain: str = typer.Argument(..., help="Domain name to fetch certificate for"),
):
    """Initialize Let's Encrypt SSL certificates for the first time."""
    logger.info(f"Initializing Let's Encrypt SSL for {domain}...")

    with local.cwd(REPO_DIR):
        logger.info("Requesting certificate via certbot webroot...")
        cmd = f"certbot certonly --webroot -w /var/www/certbot -d {domain} --email {email} --agree-tos --no-eff-email --force-renewal"
        docker_compose("exec", "certbot", "sh", "-c", cmd)

        logger.info("Restarting frontend to apply new certificates...")
        docker_compose("restart", "frontend")

    logger.success("SSL initialization complete!")


@app.command()
def renew_ssl():
    """Manually force a renewal check for Let's Encrypt and reload Nginx."""
    logger.info("Triggering manual SSL renewal check...")
    with local.cwd(REPO_DIR):
        docker_compose("exec", "certbot", "certbot", "renew")
        logger.info("Reloading Nginx...")
        docker_compose("exec", "frontend", "nginx", "-s", "reload")
    logger.success("SSL renewal check complete!")

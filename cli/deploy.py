import typer
from loguru import logger
from plumbum import local
from plumbum.cmd import docker, git, uv

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
            docker_compose("build", "--no-cache")
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
    git("switch", "prod")
    git("pull", "origin", "prod")

    with local.cwd(REPO_DIR):
        docker(
            "build",
            "-t",
            "i-form-data-repository:latest",
            "--no-cache",
            "--build-arg",
            "INSTALL_LOCAL_WHEELS=false",
            ".",
        )
        docker_compose("up", "-d", "--wait")

        setup_cmd = "invenio db init && invenio db create && invenio alembic upgrade head && invenio collect -v && invenio index init"
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

        git("switch", "prod")
        git("pull", "origin", "prod")
        with local.cwd(REPO_DIR):
            docker_compose("pull")
            docker(
                "build",
                "-t",
                "i-form-data-repository:latest",
                "--no-cache",
                "--build-arg",
                "INSTALL_LOCAL_WHEELS=false",
                ".",
            )
            docker_compose("up", "-d", "--wait")

            update_cmd = "invenio alembic upgrade head && invenio collect -v"
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
        git("switch", "prod")
        git("merge", "main")
        git("switch", "main")
        logger.info("Pushing all branches...")
        git("push", "--all")
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

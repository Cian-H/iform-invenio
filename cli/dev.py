import trustme
import typer
from loguru import logger

from cli.config import config
from cli.utils import docker_compose, get_project_root, get_repo_dir

app = typer.Typer(help="Tool for generating development SSL certificates.")


@app.command()
def generate():
    """Generates a self-signed localhost certificate using trustme."""
    repo_dir = get_repo_dir()
    nginx_dir = repo_dir / "docker" / "nginx"

    cert_path = repo_dir / config.ssl_cert_name
    key_path = repo_dir / config.ssl_key_name

    if cert_path.exists() and key_path.exists():
        logger.info(f"Certificates already exist at {nginx_dir}. Skipping generation.")
        return

    logger.info("Generating self-signed dev certificates using trustme...")

    ca = trustme.CA()
    server_cert = ca.issue_cert("localhost", "127.0.0.1", "::1")

    server_cert.private_key_pem.write_to_path(key_path)
    server_cert.cert_chain_pems[0].write_to_path(cert_path)

    logger.success(f"Successfully generated {cert_path.name} and {key_path.name}.")


@app.command()
def fmt():
    """Format codebase using prettier via npx."""
    logger.info("Running prettier via npx...")
    from plumbum.cmd import npx

    try:
        npx(
            "prettier",
            "--write",
            "**/*.{js,jsx,ts,tsx,html,css,scss,sass,svelte,yaml,json,markdown}",
        )
        logger.success("Formatting complete.")
    except Exception as e:
        logger.error(f"Formatting failed: {e}")
        raise typer.Exit(1)


@app.command()
def build_wheels():
    """Build and copy wheels for local packages (theme and config)."""
    from plumbum import local
    from plumbum.cmd import cp, direnv, rm

    root = get_project_root()
    theme_dir = root.parent / config.theme_dir_name
    config_dir = root.parent / config.config_dir_name
    repo_dir = get_repo_dir()

    logger.info("Building theme wheel...")
    with local.cwd(theme_dir):
        rm("-rf", "dist")
        direnv("exec", ".", "uv", "build", "--package", config.theme_dir_name)

    logger.info("Building config wheel...")
    with local.cwd(config_dir):
        rm("-rf", "dist")
        direnv("exec", ".", "uv", "build", "--package", config.config_dir_name)

    logger.info("Copying wheels to repository...")
    wheels_dir = repo_dir / config.local_wheels_dir
    wheels_dir.mkdir(exist_ok=True)
    rm("-f", local.path(str(wheels_dir)) // "*.whl")

    for whl in local.path(str(theme_dir / "dist")) // "*.whl":
        cp(whl, wheels_dir)
    for whl in local.path(str(config_dir / "dist")) // "*.whl":
        cp(whl, wheels_dir)

    logger.success("Successfully built and copied fresh wheels.")


@app.command()
def test_local():
    """Rebuild and restart local docker stack with fresh wheels."""
    from plumbum import local
    from plumbum.cmd import curl, docker

    build_wheels()

    logger.info("Rebuilding and restarting local docker stack...")
    repo_dir = get_repo_dir()

    with local.cwd(repo_dir):
        from plumbum import FG

        docker_compose("down") & FG
        docker[
            "build",
            "-t",
            config.docker_image_name,
            "--network",
            "host",
            "--no-cache",
            "--build-arg",
            "INSTALL_LOCAL_WHEELS=true",
            ".",
        ] & FG
        docker_compose("up", "-d", "--wait") & FG

        setup_cmd = "invenio db init || true; invenio db create || true; invenio alembic upgrade || true; invenio index init || true; invenio roles create iform_authenticated -d 'Allows uploading research data' || true"
        docker_compose("exec", "worker", "bash", "-c", setup_cmd) & FG

        logger.info(
            "Running webpack buildall inside web-ui to update persistent static volume..."
        )
        docker_compose(
            "exec", "web-ui", "bash", "-c", "uv run invenio webpack buildall"
        ) & FG

        logger.info("Restarting frontend proxy to pick up new container IPs...")
        docker_compose("restart", "frontend") & FG

    try:
        curl("-skI", "https://127.0.0.1:8443/")
        logger.success("HTTPS verification successful.")
    except Exception:
        logger.warning("HTTPS verification failed.")

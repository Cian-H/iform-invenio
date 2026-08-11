import typer
from loguru import logger
from plumbum.cmd import docker

app = typer.Typer(help="Server Bootstrap Tool")


@app.command()
def server():
    """Bootstrap a fresh production server environment."""
    logger.info("Starting fresh server bootstrap process...")

    try:
        docker_version = docker["--version"]().strip()
        logger.success(f"Found {docker_version}")
    except Exception:
        logger.error("Docker is not installed or not in PATH!")
        raise typer.Exit(1)

    try:
        docker("compose", "version")
        logger.success("Found docker compose plugin")
    except Exception:
        logger.error("Docker Compose plugin is not installed!")
        raise typer.Exit(1)

    from cli.env import template as env_template

    logger.info("Generating .env template for configuration...")
    env_template()

    logger.success("Bootstrap successful!")
    logger.warning(
        "Please fill out the generated .env.template and rename it to .env before running `uv run cli deploy prod-deploy`."
    )

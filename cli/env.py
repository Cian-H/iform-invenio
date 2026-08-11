import typer
from loguru import logger

from cli.utils import get_project_root

app = typer.Typer(help="Environment validation and templating.")

import shutil


@app.command()
def template():
    """Generate a .env.template file."""
    logger.info("Generating .env.template...")

    source = get_project_root() / "cli" / "data" / "env.template"
    target = get_project_root() / ".env.template"

    if not source.exists():
        logger.error(f"Template file not found at {source}")
        raise typer.Exit(1)

    shutil.copy2(source, target)
    logger.success(f"Generated {target.name}")

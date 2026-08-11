import typer
from loguru import logger
from plumbum import FG, local
from plumbum.cmd import docker as docker_cmd

from cli.bitwarden import app as bw_app
from cli.bootstrap import app as bootstrap_app
from cli.config import config
from cli.deploy import app as deploy_app
from cli.dev import app as dev_app
from cli.env import app as env_app
from cli.s3 import app as s3_app
from cli.utils import docker_compose, get_repo_dir

app = typer.Typer(help="Unified Repository Automation CLI")

app.add_typer(dev_app, name="dev")
app.add_typer(bw_app, name="bw")
app.add_typer(s3_app, name="s3")
app.add_typer(deploy_app, name="deploy")

app.add_typer(env_app, name="env")
app.add_typer(bootstrap_app, name="bootstrap")


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def compose(ctx: typer.Context):
    """Passthrough to docker-compose inside the repository directory."""
    with local.cwd(get_repo_dir()):
        docker_compose(*ctx.args) & FG


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def invenio(ctx: typer.Context):
    """Passthrough to invenio inside the running worker container."""
    with local.cwd(get_repo_dir()):
        docker_compose("exec", "worker", "invenio", *ctx.args) & FG


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def docker(ctx: typer.Context):
    """Passthrough to docker inside the repository directory."""
    with local.cwd(get_repo_dir()):
        docker_cmd[*ctx.args] & FG


@app.command(
    name="invenio-cli",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def invenio_cli_cmd(ctx: typer.Context):
    """Passthrough to invenio-cli inside the repository directory."""
    from plumbum.cmd import invenio_cli

    with local.cwd(get_repo_dir()):
        invenio_cli[*ctx.args] & FG


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def aws(ctx: typer.Context):
    """Passthrough to aws-cli with configured endpoint-url and credentials."""
    try:
        from plumbum.cmd import aws as aws_cmd
    except ImportError:
        logger.error("AWS CLI not found in PATH.")
        raise typer.Exit(1)

    aws_cmd["--endpoint-url", str(config.s3_endpoint_url), *ctx.args] & FG


if __name__ == "__main__":
    app()

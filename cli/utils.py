import subprocess
from pathlib import Path

from loguru import logger


def get_project_root() -> Path:
    """Dynamically determine the project root using git."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        logger.warning(
            "Not inside a git repository, falling back to script path resolution."
        )
        return Path(__file__).resolve().parent.parent


def get_repo_dir() -> Path:
    """Return the repository directory path."""
    from cli.config import config

    return get_project_root() / config.repo_dir_name


def get_dynamic_s3_credentials() -> dict:
    import atexit

    import boto3

    from cli.bitwarden import lock as bw_lock
    from cli.bitwarden import login as bw_login
    from cli.bitwarden import pull as bw_pull

    logger.info("Checking for native AWS credentials...")
    session = boto3.Session()
    creds = session.get_credentials()
    if creds and creds.access_key and creds.secret_key:
        logger.success("Found existing AWS credentials natively. Skipping Bitwarden.")
        return {
            "INVENIO_S3_ACCESS_KEY_ID": creds.access_key,
            "INVENIO_S3_SECRET_ACCESS_KEY": creds.secret_key,
        }

    logger.info("No native AWS credentials found. Falling back to Bitwarden...")
    if bw_login():
        atexit.register(bw_lock)

    return bw_pull()


_deploy_env_vars = None


def docker_compose(*args):
    global _deploy_env_vars
    import typer
    from plumbum import local
    from plumbum.cmd import docker

    from cli.config import config

    env_file = get_project_root() / ".env"

    if not env_file.exists():
        logger.error(
            "The .env file does not exist! Please run `uv run cli bootstrap server` first to generate and configure it."
        )
        raise typer.Exit(1)

    if _deploy_env_vars is None:
        use_s3 = True
        with open(env_file) as f:
            for line in f:
                if line.startswith("INVENIO_USE_S3"):
                    val = line.split("=")[1].strip().lower()
                    use_s3 = val == "true"

        if use_s3:
            _deploy_env_vars = get_dynamic_s3_credentials()
        else:
            logger.info(
                "INVENIO_USE_S3 is false. Using dummy S3 credentials to prevent production database corruption."
            )
            _deploy_env_vars = {
                "INVENIO_S3_ACCESS_KEY_ID": "CHANGE_ME",
                "INVENIO_S3_SECRET_ACCESS_KEY": "CHANGE_ME",
            }

    compose = docker[
        "compose", "-f", config.docker_compose_file, "--env-file", str(env_file)
    ]
    with local.env(**_deploy_env_vars):
        return compose[*args]

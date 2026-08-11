import json

import typer
from loguru import logger
from plumbum import FG, ProcessExecutionError, local

from cli.config import config
from cli.utils import get_project_root

app = typer.Typer(help="Bitwarden integration workflows.")

BW_SESSION_FILE = get_project_root() / ".bw_session"
ENV_FILE = get_project_root() / ".env"


def _get_bw():
    try:
        from plumbum.cmd import bw

        return bw
    except ImportError:
        logger.error(
            "Bitwarden CLI ('bw') not found. Please ensure it is installed or "
            "run 'direnv allow' if you just updated devenv.nix."
        )
        raise typer.Exit(1)


@app.command()
def login() -> bool:
    """Log in to Bitwarden and cache the session token. Returns True if a new session was created."""
    bw = _get_bw()

    if config.bitwarden_server_url:
        logger.info(f"Configuring Bitwarden server: {config.bitwarden_server_url}")
        bw("config", "server", config.bitwarden_server_url)

    logger.info("Checking login status...")
    try:
        status_json = bw("status")
        status = json.loads(status_json)
        if status.get("status") == "unlocked":
            logger.info("Vault is already unlocked. Using existing session.")
            return False

        if status.get("status") == "unauthenticated":
            logger.info("Not logged in. Initiating login...")
            bw["login"] & FG
        elif status.get("status") == "locked":
            logger.info("Vault is locked. Initiating unlock...")
    except ProcessExecutionError:
        logger.warning("Failed to check status. Initiating login...")
        bw["login"] & FG

    logger.info("Unlocking vault and saving session...")
    try:
        # Prompt for master password and output just the raw session key
        session_key = bw("unlock", "--raw").strip()
        BW_SESSION_FILE.write_text(session_key)
        BW_SESSION_FILE.chmod(0o600)
        logger.success("Session unlocked and cached securely in .bw_session")
        return True
    except ProcessExecutionError as e:
        logger.error(f"Failed to unlock vault: {e}")
        raise typer.Exit(1)


@app.command()
def pull():
    """Pull secrets from Bitwarden Secure Note and inject into .env"""
    bw = _get_bw()

    if not BW_SESSION_FILE.exists():
        logger.error(
            "No active Bitwarden session found. Please run `uv run cli bw login` first."
        )
        raise typer.Exit(1)

    session_key = BW_SESSION_FILE.read_text().strip()
    with local.env(BW_SESSION=session_key):
        logger.info("Syncing vault...")
        try:
            bw("sync")
        except ProcessExecutionError as e:
            logger.warning(f"Failed to sync vault (continuing anyway): {e}")

        logger.info(f"Fetching item: {config.bitwarden_item_name}...")
        try:
            item_json = bw("get", "item", config.bitwarden_item_name)
            item = json.loads(item_json)
        except ProcessExecutionError as e:
            logger.error(
                f"Failed to fetch item '{config.bitwarden_item_name}'. Make sure the name is exact."
            )
            logger.debug(f"Details: {e}")
            raise typer.Exit(1)

        notes = item.get("notes")
        if not notes:
            logger.error(
                f"The item '{config.bitwarden_item_name}' does not contain any notes."
            )
            raise typer.Exit(1)

        try:
            secrets = json.loads(notes)
        except json.JSONDecodeError:
            logger.error(
                f"The notes in '{config.bitwarden_item_name}' are not valid JSON."
            )
            raise typer.Exit(1)

        logger.info(f"Successfully fetched {len(secrets)} secrets from secure note.")
        return secrets


@app.command()
def lock():
    """Lock the Bitwarden vault and remove the local session token."""
    bw = _get_bw()

    if BW_SESSION_FILE.exists():
        session_key = BW_SESSION_FILE.read_text().strip()
        with local.env(BW_SESSION=session_key):
            try:
                bw("lock")
                logger.success("Bitwarden vault locked successfully.")
            except ProcessExecutionError as e:
                logger.warning(f"Failed to lock vault cleanly: {e}")

        BW_SESSION_FILE.unlink()
        logger.success("Local session token removed.")
    else:
        logger.info("No local session token found.")

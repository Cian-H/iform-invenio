import json
from pathlib import Path

import boto3
import typer
from botocore.client import Config
from loguru import logger

from cli.config import config
from cli.utils import get_project_root

app = typer.Typer(help="Impossible Cloud S3 Management Tool")


def get_s3_client():
    if not config.s3_access_key_id or not config.s3_secret_access_key:
        logger.warning(
            "S3_ACCESS_KEY_ID or S3_SECRET_ACCESS_KEY not found in environment. Boto3 will attempt to use default credential provider chain."
        )

    kwargs = {
        "service_name": "s3",
        "endpoint_url": str(config.s3_endpoint_url),
        "region_name": config.s3_region,
        "config": Config(signature_version="s3v4"),
    }

    if config.s3_access_key_id and config.s3_secret_access_key:
        kwargs["aws_access_key_id"] = config.s3_access_key_id
        kwargs["aws_secret_access_key"] = config.s3_secret_access_key.get_secret_value()
    else:
        logger.info("Using default AWS credential provider chain...")

    return boto3.client(**kwargs)


@app.command()
def list_buckets():
    """List all buckets in the S3 account."""
    client = get_s3_client()
    response = client.list_buckets()
    logger.info("Buckets:")
    for bucket in response.get("Buckets", []):
        logger.info(f"  - {bucket['Name']}")


@app.command()
def create_bucket(bucket_name: str):
    """Create a new bucket."""
    client = get_s3_client()
    try:
        if config.s3_region == "us-east-1":
            client.create_bucket(Bucket=bucket_name)
        else:
            client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": config.s3_region},
            )
        logger.success(f"Successfully created bucket: {bucket_name}")
    except Exception as e:
        logger.error(f"Error creating bucket {bucket_name}: {e}")
        raise typer.Exit(1)


@app.command()
def upload_file(
    file_path: Path = typer.Argument(..., help="Path to local file"),
    bucket_name: str = typer.Argument(..., help="Target bucket name"),
    object_name: str | None = typer.Option(
        None, "--object-name", help="S3 object name (defaults to file name)"
    ),
):
    """Upload a local file to a bucket."""
    client = get_s3_client()
    if object_name is None:
        object_name = file_path.name
    try:
        client.upload_file(str(file_path), bucket_name, object_name)
        logger.success(f"Uploaded {file_path} to {bucket_name}/{object_name}")
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise typer.Exit(1)


@app.command()
def apply_cors(
    bucket_name: str = typer.Argument(config.s3_bucket_name, help="Target bucket name"),
    cors_file: Path = typer.Option(
        get_project_root() / "cli" / "data" / "s3_cors.json",
        help="Path to CORS JSON file",
    ),
):
    """Apply a CORS configuration from a JSON file to a bucket."""
    client = get_s3_client()

    if not cors_file.exists():
        logger.error(f"CORS file not found: {cors_file}")
        raise typer.Exit(1)

    try:
        with open(cors_file, "r") as f:
            cors_rules = json.load(f)

        client.put_bucket_cors(
            Bucket=bucket_name, CORSConfiguration={"CORSRules": cors_rules}
        )
        logger.success(f"Successfully applied CORS configuration to {bucket_name}")
    except Exception as e:
        logger.error(f"Failed to apply CORS config: {e}")
        raise typer.Exit(1)

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from cli.utils import get_project_root


class Config(BaseSettings):
    """Centralized configuration values for the scripts."""

    model_config = SettingsConfigDict(
        env_file=get_project_root() / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    s3_endpoint_url: str = Field(
        default="https://eu-west-1.storage.impossibleapi.net",
        validation_alias=AliasChoices(
            "invenio_s3_endpoint_url", "s3_endpoint_url", "aws_endpoint_url"
        ),
    )
    s3_access_key_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "invenio_s3_access_key_id", "s3_access_key_id", "aws_access_key_id"
        ),
    )
    s3_secret_access_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "invenio_s3_secret_access_key",
            "s3_secret_access_key",
            "aws_secret_access_key",
        ),
    )
    s3_region: str = Field(
        default="eu-west-1",
        validation_alias=AliasChoices(
            "invenio_s3_region_name",
            "invenio_s3_region",
            "s3_region",
            "aws_default_region",
        ),
    )
    s3_bucket_name: str = Field(
        default="iform-invenio",
        validation_alias=AliasChoices(
            "invenio_s3_bucket_name", "s3_bucket_name", "aws_s3_bucket"
        ),
    )

    # Project Settings
    repo_dir_name: str = Field(default="i-form-data-repository")
    docker_compose_file: str = Field(default="docker-compose.full.yml")
    docker_image_name: str = Field(default="i-form-data-repository:latest")

    # Dev Settings
    theme_dir_name: str = Field(default="invenio-theme-iform")
    config_dir_name: str = Field(default="invenio-config-iform")
    local_wheels_dir: str = Field(default="local_wheels")
    ssl_cert_name: str = Field(default="nginx.crt")
    ssl_key_name: str = Field(default="nginx.key")

    # Bitwarden Settings
    bitwarden_item_name: str = Field(default="I-Form Invenio S3 Keys")
    bitwarden_server_url: str | None = Field(default=None)


config = Config()

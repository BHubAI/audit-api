import functools
import json
import os
from abc import ABC
from typing import Any

import boto3
from botocore.config import Config as BotoConfig
from pydantic import ConfigDict, SecretStr
from pydantic_settings import BaseSettings


class AbstractSettings(BaseSettings, ABC):
    """Base configuration."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __hash__(self):
        return 0

    open_search_domain: str = os.getenv("OPENSEARCH_DOMAIN", "localhost")
    opensearch_port: int = int(os.getenv("OPENSEARCH_PORT", "80"))


class Settings(AbstractSettings):
    """Defines application-related settings attributes"""

    AUTH0_SECRET_ARN: SecretStr
    DATABASE_SECRET_ARN: SecretStr

    @property
    @functools.lru_cache
    def auth0_tenants(self) -> dict:
        secret_value = _secret_value_from_arn(self.AUTH0_SECRET_ARN.get_secret_value())

        return secret_value

    @property
    @functools.lru_cache
    def database_uri(self) -> str:
        secret_value = _secret_value_from_arn(
            self.DATABASE_SECRET_ARN.get_secret_value()
        )

        user = secret_value["username"]
        password = secret_value["password"]
        database_name = secret_value["dbname"]
        database_host = secret_value["host"]

        return f"mysql+pymysql://{user}:{password}@{database_host}/{database_name}"


class LocalSettings(AbstractSettings):
    """
    Mirrors the main Settings class in order to define specific
    Local values attributes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def _secret_value_from_arn(secret_arn: str) -> dict[str, Any]:
    """Returns the secret value from the given secret ARN.

    Parameters
    ----------
    secret_arn_variable : str
        The name of the environment variable containing the secret ARN.

    Returns
    -------
    Dict[str, Any]
        The secret value.
    """
    client = boto3.client(
        "secretsmanager",
        config=BotoConfig(
            connect_timeout=3,
            read_timeout=3,
        ),
    )

    secret = client.get_secret_value(SecretId=secret_arn)
    secret_value = json.loads(secret["SecretString"])

    return secret_value


@functools.lru_cache
def _load_settings(env: str) -> Settings:
    """Loads the settings based on the given environment.

    Parameters
    ----------
    env : str
        The environment to load the settings from.

    Returns
    -------
    Config
        Application settings.
    """
    if env == "local":
        return LocalSettings()

    return Settings()


environment = os.getenv("APP_ENV", "local")
settings: Settings = _load_settings(environment)

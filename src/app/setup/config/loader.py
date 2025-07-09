import logging
import os
from collections.abc import Mapping
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final

import rtoml

ENV_VAR_NAME: Final[str] = "APP_ENV"


class ValidEnvs(StrEnum):
    """
    Values should reflect actual directory names.
    """

    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


class DirContents(StrEnum):
    """
    Values should reflect actual file names.
    """

    CONFIG_NAME = "config.toml"
    SECRETS_NAME = ".secrets.toml"
    EXPORT_NAME = "export.toml"
    DOTENV_NAME = ".env"


BASE_DIR_PATH: Final[Path] = Path(__file__).resolve().parent.parent.parent.parent.parent
CONFIG_PATH: Final[Path] = BASE_DIR_PATH / "config"


ENV_TO_DIR_PATHS: Final[Mapping[ValidEnvs, Path]] = MappingProxyType({
    ValidEnvs.LOCAL: CONFIG_PATH / ValidEnvs.LOCAL,
    ValidEnvs.DEV: CONFIG_PATH / ValidEnvs.DEV,
    ValidEnvs.PROD: CONFIG_PATH / ValidEnvs.PROD,
})

log = logging.getLogger(__name__)


def validate_env(*, env: str | None) -> ValidEnvs:
    if env is None:
        raise ValueError(f"{ENV_VAR_NAME} is not set.")
    try:
        return ValidEnvs(env)
    except ValueError as e:
        valid_values = ", ".join(f"'{e}'" for e in ValidEnvs)
        raise ValueError(
            f"Invalid {ENV_VAR_NAME}: '{env}'. Must be one of: {valid_values}.",
        ) from e


def get_current_env() -> ValidEnvs:
    env_value = os.getenv(ENV_VAR_NAME)
    return validate_env(env=env_value)


def read_config(
    *,
    env: ValidEnvs,
    config: DirContents = DirContents.CONFIG_NAME,
) -> dict[str, Any]:
    dir_path = ENV_TO_DIR_PATHS.get(env)
    if dir_path is None:
        raise FileNotFoundError(f"No directory path configured for environment: {env}")
    file_path = dir_path / config
    if not file_path.is_file():
        raise FileNotFoundError(
            f"The file does not exist at the specified path: {file_path}",
        )
    with open(file=file_path, mode="r", encoding="utf-8") as file:
        return rtoml.load(file)


def merge_dicts(*, dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(dict1=result[key], dict2=value)
        else:
            result[key] = value
    return result


def load_full_config(*, env: ValidEnvs) -> dict[str, Any]:
    log.info("Reading config for environment: '%s'", env)
    config = read_config(env=env)
    try:
        secrets = read_config(env=env, config=DirContents.SECRETS_NAME)
    except FileNotFoundError:
        log.warning("Secrets file not found. Full config will not contain secrets.")
    else:
        config = merge_dicts(dict1=config, dict2=secrets)
    return config

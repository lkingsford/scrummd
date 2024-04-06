"""Code for loading the config from the filesystem"""

import sys
import os
from scrummd import const
from scrummd.config import ScrumConfig

# Need to do this because tomllib wasn't included until Python 3.11
if sys.version_info[1] < 11:
    import tomli

    LEGACY_TOML = True
else:
    import tomllib

    LEGACY_TOML = False


def _load_fs_config_legacy() -> ScrumConfig:
    """Load the config from the filesystem into a ScrumConfig in
    Python 3.10"""
    for filename in const.CONFIG_FILE_NAME:
        if os.path.exists(filename):
            config_file = open(filename, "rb")
            config_settings = tomli.load(config_file)
            relevant_settings = config_settings.get("tool", {}).get("scrummd")
            if relevant_settings:
                return ScrumConfig(**relevant_settings)

    return ScrumConfig()


def _load_fs_config() -> ScrumConfig:
    """Load the config from the filesystem into a ScrumConfig"""
    for filename in const.CONFIG_FILE_NAME:
        if os.path.exists(filename):
            config_file = open(filename, "rb")
            config_settings = tomllib.load(config_file)
            relevant_settings = config_settings.get("tool", {}).get("scrummd")
            if relevant_settings:
                return ScrumConfig(**relevant_settings)

    return ScrumConfig()


load_fs_config = _load_fs_config if not LEGACY_TOML else _load_fs_config_legacy

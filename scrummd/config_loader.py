"""Code for loading the config from the filesystem"""

import os
import tomllib
from scrummd import const
from scrummd.config import ScrumConfig


def load_fs_config() -> ScrumConfig:
    """Load the config from the filesystem into a ScrumConfig"""
    for filename in const.CONFIG_FILE_NAME:
        if os.path.exists(filename):
            config_file = open(filename, "rb")
            config_settings = tomllib.load(config_file)
            relevant_settings = config_settings.get("tool", {}).get("scrummd")
            if relevant_settings:
                return ScrumConfig(**relevant_settings)

    return ScrumConfig()

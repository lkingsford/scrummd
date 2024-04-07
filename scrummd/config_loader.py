"""Code for loading the config from the filesystem"""

import sys
import os
from scrummd import const
from scrummd.config import ScrumConfig

# Need to do this because tomllib wasn't included until Python 3.11
if sys.version_info >= (3, 11):
    import tomllib

    LOAD = tomllib.load
else:
    import tomli

    LOAD = tomli.load


def load_fs_config() -> ScrumConfig:
    """Load the config from the filesystem into a ScrumConfig"""
    for filename in const.CONFIG_FILE_NAME:
        if os.path.exists(filename):
            config_file = open(filename, "rb")
            config_settings = LOAD(config_file)
            relevant_settings = config_settings.get("tool", {}).get("scrummd")
            if relevant_settings:
                return ScrumConfig(**relevant_settings)

    return ScrumConfig()

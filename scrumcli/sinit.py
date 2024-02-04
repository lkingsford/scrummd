"""Initialises a scrumcli workspace in the current directory with recommended folders and configuration.
"""

import argparse
import os
import tomli_w
from .const import *


def entry():
    parser = argparse.ArgumentParser()
    parser.description = __doc__
    parser.parse_args()
    init_workspace.init_workspace()


def init_workspace():
    os.makedirs(SCRUM_FOLDER_NAME)
    init_config()


def init_config():
    tomli_w.dump(CONFIG_FILE_NAME)

"""Display a collection of scrum cards"""

import os
import argparse
import tomllib
from scrummd import const

from scrummd.collection import get_collection
from scrummd.config import ScrumConfig


def load_fs_config() -> ScrumConfig:
    for filename in const.CONFIG_FILE_NAME:
        if os.path.exists(filename):
            config_file = open(filename, "rb")
            config_settings = tomllib.load(config_file)
            relevant_settings = config_settings.get("tool", {}).get("scrummd")
            if relevant_settings:
                return ScrumConfig(**relevant_settings)

    return ScrumConfig()


def entry():
    parser = argparse.ArgumentParser()
    parser.add_argument("collection")
    parser.description = __doc__
    args = parser.parse_args()

    config = load_fs_config()

    collection = get_collection(config, args.collection)

    print("index, summary")
    for index, card in collection.items():
        print(f"{index}, {card['summary']}")


if __name__ == "__main__":
    entry()

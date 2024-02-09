"""Display a collection of scrum cards"""

import argparse

from scrummd.collection import get_collection
from scrummd.config import ScrumConfig
from scrummd.config_loader import load_fs_config


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

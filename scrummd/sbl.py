"""Display a collection of scrum cards"""

import argparse

from scrummd.collection import get_collection
from scrummd.config import ScrumConfig

config = ScrumConfig()


def entry():
    parser = argparse.ArgumentParser()
    parser.add_argument("collection")
    parser.description = __doc__
    args = parser.parse_args()

    collection = get_collection(config, args.collection)

    print("index, summary")
    for index, card in collection.items():
        print(f"{index}, {card['summary']}")


if __name__ == "__main__":
    entry()

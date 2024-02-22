"""Display a collection of scrum cards"""

import argparse

from scrummd.collection import get_collection
from scrummd.config_loader import load_fs_config


def entry():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "collection",
        nargs="?",
        help="The collection to return. If none is given, all cards are returned.",
    )
    parser.add_argument(
        "-c",
        "--columns",
        nargs="?",
        help="A comma separated list of columns to return.",
    )
    parser.description = __doc__
    args = parser.parse_args()

    config = load_fs_config()

    collection = get_collection(config, args.collection)

    if args.columns:
        columns = [column.strip() for column in args.columns.split(",")]
    else:
        columns = config.columns

    print(", ".join(columns))

    for card in collection.values():
        values = [card[col] if (col in card and card[col]) else "" for col in columns]
        print(", ".join(values))


if __name__ == "__main__":
    entry()

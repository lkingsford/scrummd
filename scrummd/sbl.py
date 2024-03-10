"""Display a collection of scrum cards"""

import argparse

from scrummd.collection import Groups, get_collection, group_collection
from scrummd.config import ScrumConfig
from scrummd.config_loader import load_fs_config
from scrummd.exceptions import ValidationError
from scrummd.scard import format_field

VALIDATION_ERROR = 1


def create_parser() -> argparse.ArgumentParser:
    """Create an argument parser for sbl

    Returns:
        argparse.ArgumentParser: ArgumentParser for sbl
    """
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
    parser.add_argument(
        "-b",
        "--bare",
        action="store_true",
        help="Return bare paths only suitable for scripting. Effectively shorthand for `sbl -H -c path`.",
    )
    parser.add_argument(
        "-H",
        "--omit-headers",
        action="store_true",
        help="Omit headers from output.",
    )

    parser.add_argument(
        "-g",
        "--group-by",
        action="append",
        help="Group by field in card. Can use multiple group-by arguments to have multiple levels of grouping.",
    )

    parser.description = __doc__
    return parser


def entry():
    """Entry point for sbl"""
    parser = create_parser()
    args = parser.parse_args()

    config = load_fs_config()

    try:
        collection = get_collection(config, args.collection)
    except ValidationError:
        if config.strict:
            return VALIDATION_ERROR

    if args.columns:
        columns = [column.strip() for column in args.columns.split(",")]
    else:
        columns = config.columns

    omit_headers = args.omit_headers or config.omit_headers

    if args.bare:
        columns = ["path"]
        omit_headers = True

    if not omit_headers:
        print(", ".join(columns))

    if not args.group_by:
        for card in collection.values():
            values = [format_field(card.get_field(col)) for col in columns]
            print(", ".join(values))

    else:
        grouped = group_collection(config, collection, args.group_by)

        def output_group(
            config: ScrumConfig, collection: Groups, group_fields: list[str], level=1
        ):
            for group_key, cards in collection.items():
                if not omit_headers:
                    print(
                        f"[" * level
                        + group_fields[0]
                        + " = "
                        + str(group_key)
                        + "]" * level
                    )

                if isinstance(cards, dict):
                    output_group(config, cards, group_fields[1:], level + 1)

                else:
                    for card in cards:
                        values = [format_field(card.get_field(col)) for col in columns]
                        print(", ".join(values))

        output_group(config, grouped, args.group_by)


if __name__ == "__main__":
    entry()

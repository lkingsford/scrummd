"""Display a collection in the style of a scrum board to the console"""

import sys
import argparse
from scrummd.collection import filter_collection, get_collection, group_collection
from scrummd.config_loader import load_fs_config
from scrummd.exceptions import ValidationError
import scrummd.sbl.board_output
from scrummd.sbl.output import OutputConfig
from scrummd.sbl.sbl import (
    VALIDATION_ERROR,
    field_to_sort_criteria,
    include_to_filter,
)
from scrummd.version import version_to_output


def create_parser() -> argparse.ArgumentParser:
    """Create an argument parser for sboard.

    Returns:
        argparse.ArgumentParser: ArgumentParser for sboard.
    """

    # Borrowed wholesale from sbl, and should probably be refactored to share code.

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
        "-g",
        "--group-by",
        action="append",
        metavar="FIELD",
        help="Group by field in card. Can use multiple group-by arguments to have multiple levels of grouping. Either must be set here, or in config.",
    )

    parser.add_argument(
        "-i",
        "--include",
        action="append",
        metavar="FILTER",
        type=include_to_filter,
        help="Only include collections that match this filter. The filter is in the format "
        + "`key=value1[, value2, ...]`. Multiple values verify if the field is any of the values. "
        + "Multiple --include statements must all be matched.",
    )

    parser.add_argument(
        "-s",
        "--sort-by",
        action="append",
        metavar="FIELD",
        type=field_to_sort_criteria,
        help="Sort by a field in card. Can use multiple sort-by arguments to have multiple levels "
        + "of grouping. Can prefix field with ^ to reverse the sort.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=version_to_output(),
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
        columns = config.sbl.columns

    if args.include:
        collection = filter_collection(collection, args.include)

    group_by = args.group_by or config.sboard.default_group_by
    if not group_by:
        print(
            "--group-by argument must be set, or default_group_by must be set in the [tools.scrummd.board] configuration to use sboard",
            file=sys.stderr,
        )
        return 1

    board_config = scrummd.sbl.board_output.BoardConfig()

    grouped = group_collection(config, collection, group_by, args.sort_by or [])
    scrummd.sbl.board_output.board_grouped_output(
        config,
        OutputConfig(False, group_by, columns),
        board_config,
        grouped,
    )


if __name__ == "__main__":
    exit_code = entry()
    if exit_code:
        sys.exit(exit_code)

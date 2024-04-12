"""Display a collection of scrum cards"""

import argparse

from scrummd.collection import (
    Filter,
    Groups,
    SortCriteria,
    get_collection,
    group_collection,
    filter_collection,
    sort_collection,
)
from scrummd.config_loader import load_fs_config
from scrummd.exceptions import ValidationError
from scrummd.sbl import board_output, text_output
from scrummd.sbl.output import (
    OutputConfig,
    SblOutputGroupedFunction,
    SblOutputUngroupedFunction,
)
from scrummd.version import version_to_output

VALIDATION_ERROR = 1
OUTPUT_FORMATS = ["text", "board"]

UNGROUPED_OUTPUTTERS: dict[str, SblOutputUngroupedFunction] = {
    "text": text_output.text_ungrouped_output,
    "board": board_output.board_ungrouped_output,
}

GROUPED_OUTPUTTERS: dict[str, SblOutputGroupedFunction] = {
    "text": text_output.text_grouped_output,
    "board": board_output.board_grouped_output,
}


def include_to_filter(source: str) -> Filter:
    """Transform an --include argument into a Filter

    Args:
        source (str): FILTER from --include

    Returns:
        Filter: Filter object from the string
    """
    try:
        field, value_str = source.split("=")
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Filter not in valid format. Expected format is --include key=value1[, value2]"
        )

    values = [value.strip() for value in value_str.split(",")]

    return Filter(field.strip(), values, Filter.FilterMode.EQUALS)


def field_to_sort_criteria(argument: str) -> SortCriteria:
    """Transform a --sort-by argument into a sort criteria

    Args:
        argument (str): the FIELD to sort by from --sort-by

    Returns:
        SortCriteria: A criteria to sort by
    """

    stripped = argument.strip()
    if len(stripped) == 0 or stripped[1] == "^" and len(stripped) == 1:
        raise argparse.ArgumentTypeError("Sort criteria not in valid format")
    if stripped[0] == "^":
        return SortCriteria(stripped[1:], True)
    return SortCriteria(stripped, False)


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
        metavar="FIELD",
        help="Group by field in card. Can use multiple group-by arguments to have multiple levels of grouping.",
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
        "-o", "--output", default="text", choices=OUTPUT_FORMATS, help="Output format"
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

    omit_headers = args.omit_headers or config.sbl.omit_headers

    if args.bare:
        columns = ["path"]
        omit_headers = True

    if args.include:
        collection = filter_collection(collection, args.include)

    output_specific_config = None
    if args.output == "board":
        output_specific_config = board_output.BoardConfig()

    group_by = args.group_by or config.sboard.default_group_by
    if not group_by:
        sorted_collection = sort_collection(collection, args.sort_by or [])
        UNGROUPED_OUTPUTTERS[args.output](
            config,
            OutputConfig(omit_headers, [], columns),
            output_specific_config,
            sorted_collection,
        )

    else:
        grouped = group_collection(config, collection, group_by, args.sort_by or [])

        GROUPED_OUTPUTTERS[args.output](
            config,
            OutputConfig(omit_headers, group_by, columns),
            output_specific_config,
            grouped,
        )


if __name__ == "__main__":
    entry()

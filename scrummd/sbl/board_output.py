from dataclasses import dataclass
from typing import Optional
from scrummd.collection import Groups, Collection
from scrummd.config import ScrumConfig
from scrummd.sbl.output import OutputConfig, UnsupportedOutputError
import os

MIN_COLUMN_WIDTH = 15


@dataclass
class BoardConfig:
    default_column_width: int = 20
    """Column width to use if unable to get the width of the terminal"""

    minimum_column_width: int = 15
    """Don't let a column be thinner than this """

    override_column_width: Optional[int] = None
    """Column width to force to use"""


def _format_field(field: str, width: int) -> str:
    stripped_field = field.strip().replace("\n", " ")
    if len(stripped_field) > width:
        return stripped_field[0 : width - 1] + "…"
    else:
        return stripped_field + " " * (width - len(stripped_field))


def _output_last_level_groups(
    config: ScrumConfig,
    output_config: OutputConfig,
    board_config: BoardConfig,
    groups: Groups,
):
    """Output the first level of groups that's actually split

    Args:
        config (ScrumConfig): Scrum configuration
        output_config (OutputConfig): Output specific config
        board_config (BoardConfig): Board specific configuration
        groups (Groups): Final level of groups to display
    """
    group_count = len(groups)
    if group_count == 0:
        return
    try:
        terminal_width = os.get_terminal_size().columns
        column_width = board_config.override_column_width or max(
            (terminal_width) // group_count, board_config.minimum_column_width
        )
        too_many = column_width * group_count > terminal_width
    except OSError:
        # Can't get width of terminal
        column_width = board_config.default_column_width
        too_many = False

    if too_many:
        display_count = terminal_width // column_width
        keys = list(groups.keys())[0:display_count]
    else:
        display_count = group_count
        keys = list(groups.keys())

    # Print headers
    header_row = ""
    for _, group_key in enumerate(keys):
        if len(str(group_key)) > (column_width - 1):
            header_value = str(group_key)[: column_width - 1] + "…"
        else:
            header_value = str(group_key) + " " * (
                column_width - 1 - len(str(group_key))
            )
        header_row += "|" + header_value

    if too_many:
        header_row += ">"
    else:
        header_row += "|"
    print(header_row)

    border_row = ""
    for _ in range(display_count):
        border_row += "|" + "-" * (column_width - 1)

    if too_many:
        border_row += ">"
    else:
        border_row += "|"
    print(border_row)

    text_width = column_width - 1

    # We build the strings for each column, and then display them line by line
    output_columns: dict[str, list[str]] = {str(key): [] for key in keys}
    for group_key, group_value in groups.items():
        if group_key not in keys:
            # Deal with too many columns for screen
            continue
        output_list = output_columns[str(group_key)]
        for card in group_value.collection.values():
            for field_name in output_config.columns:
                output_list.append(
                    _format_field(str(card.get_field(field_name)), text_width)
                )
            output_list.append(" " * text_width)

    for line_no in range(
        max([len(value_column) for value_column in output_columns.values()])
    ):
        value_line = ""
        for column in output_columns.values():
            if len(column) > line_no:
                value_line += "|" + column[line_no]
            else:
                value_line += "|" + " " * (column_width - 1)

        if too_many:
            value_line += ">"
        else:
            value_line += "|"
        print(value_line)


def _output_group(
    config: ScrumConfig,
    output_config: OutputConfig,
    board_config: BoardConfig,
    collection: Groups,
    group_fields: list[str],
    level=1,
):
    """Output groups to stdout in multiple levels in a scrum-board style
        format

    Args:
        config (ScrumConfig): Active scrummd configuration
        output_config (OutputConfig): Active output configuration
        board_config (BoardConfig): Board specific configuration
        collection (Groups): Collection to output to the screen
        group_fields (list[str]): Fields that are being grouped by
        level (int, optional): For internal use in recursion only. Defaults to 1.
    """
    if len(group_fields) == 1:
        _output_last_level_groups(config, output_config, board_config, collection)
        return
    for group_key, cards in collection.items():
        if not output_config.omit_headers:
            print(f"[" * level + group_fields[0] + " = " + str(group_key) + "]" * level)
        _output_group(
            config,
            output_config,
            board_config,
            cards.groups,
            group_fields[1:],
            level + 1,
        )


def board_grouped_output(
    config: ScrumConfig,
    output_config: OutputConfig,
    board_config: BoardConfig,
    groups: Groups,
) -> None:
    """Output a board to the console using the current display size

    Args:
        config (ScrumConfig): ScrumConfig
        output_config (OutputConfig): Output specific config
        board_config (BoardConfig): Configuration related to the board output specifically
        groups (Groups): Groups to output
    """

    _output_group(config, output_config, board_config, groups, output_config.group_by)
    # _output_last_level_groups(config, output_config, groups)


def board_ungrouped_output(
    config: ScrumConfig,
    output_config: OutputConfig,
    board_config: None,
    collection: Collection,
) -> None:
    """Unsupported output type for Board

    Args:
        config (ScrumConfig): ScrumConfig
        output_config (OutputConfig): Output specific config
        text_config (None): Not used (yet)
        collection (Collection): Collection of cards to output
    """
    raise UnsupportedOutputError(
        "Board output requires at least one --group-by parameter"
    )

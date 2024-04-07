from scrummd.collection import Groups, Collection
from scrummd.config import ScrumConfig
from scrummd.sbl.output import OutputConfig, UnsupportedOutputError
import os


def _format_field(field: str, width: int) -> str:
    stripped_field = field.strip().replace("/n", "")
    if len(stripped_field) > width:
        return stripped_field[0 : width - 1] + "…"
    else:
        return stripped_field + " " * (width - len(stripped_field))


def board_grouped_output(
    config: ScrumConfig,
    output_config: OutputConfig,
    board_config: None,
    groups: Groups,
) -> None:
    """Output a board to the console using the current display size

    Args:
        config (ScrumConfig): ScrumConfig
        output_config (OutputConfig): Output specific config
        text_config (None): Not used (yet)
        groups (Groups): Groups to output
    """
    group_count = len(groups)
    column_width = os.get_terminal_size().columns // group_count

    # Print headers

    header_row = "|"
    for i, group_key in enumerate(groups.keys()):
        if len(str(group_key)) > (column_width - 1):
            header_value = str(group_key)[: column_width - 1] + "…"
        else:
            header_value = str(group_key) + " " * (
                column_width - 1 - len(str(group_key))
            )
        header_row += header_value + "|"
    print(header_row)

    border_row = "|"
    for i in range(len(groups.keys())):
        border_row += "-" * (column_width - 1) + "|"
    print(border_row)

    text_width = column_width - 1

    # We build the strings for each column, and then display them line by line
    output_columns: dict[str, list[str]] = {str(key): [] for key in groups.keys()}
    for group_key, group_value in groups.items():
        output_list = output_columns[str(group_key)]
        for card in group_value.collection.values():
            for field_name in output_config.columns:
                output_list.append(
                    _format_field(str(card.get_field(field_name)), text_width)
                )
            output_list.append(" " * text_width)

    for line_no in range(group_count):
        value_line = "|"
        for column in output_columns.values():
            if len(column) > line_no:
                value_line += column[line_no] + "|"
            else:
                value_line += " " * (column_width - 1) + "|"
        print(value_line)


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

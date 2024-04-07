from scrummd.collection import Groups, Collection
from scrummd.config import ScrumConfig
from .output import OutputConfig
from scrummd.scard import format_field


def _output_group(
    config: ScrumConfig,
    output_config: OutputConfig,
    collection: Groups,
    group_fields: list[str],
    level=1,
):
    """Internal recursive function to text_grouped_output"""
    for group_key, cards in collection.items():
        if not output_config.omit_headers:
            print(f"[" * level + group_fields[0] + " = " + str(group_key) + "]" * level)

        if len(cards.groups) > 0:
            _output_group(
                config, output_config, cards.groups, group_fields[1:], level + 1
            )

        else:
            for card in cards.collection.values():
                values = [
                    format_field(card.get_field(col)) for col in output_config.columns
                ]
                print(", ".join(values))


def text_grouped_output(
    config: ScrumConfig,
    output_config: OutputConfig,
    text_config: None,
    groups: Groups,
) -> None:
    """Output groups to stdout

    Args:
        config (ScrumConfig): ScrumConfig
        output_config (OutputConfig): Output specific config
        text_config (None): Not used (yet)
        groups (Groups): Groups to output
    """

    _output_group(config, output_config, groups, output_config.group_by)


def text_ungrouped_output(
    config: ScrumConfig,
    output_config: OutputConfig,
    text_config: None,
    collection: Collection,
) -> None:
    """Output collection to stdout

    Args:
        config (ScrumConfig): ScrumConfig
        output_config (OutputConfig): Output specific config
        text_config (None): Not used (yet)
        collection (Collection): Collection of cards to output
    """
    if not output_config.omit_headers:
        print(", ".join(output_config.columns))
    for card in collection.values():
        values = [format_field(card.get_field(col)) for col in output_config.columns]
        print(", ".join(values))

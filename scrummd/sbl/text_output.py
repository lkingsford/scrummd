from scrummd.collection import Groups, Collection
from scrummd.config import ScrumConfig
from .output import OutputConfig
from scrummd.scard import format_field


def text_grouped_output(
    config: ScrumConfig, output_config: OutputConfig, text_config: None, groups: Groups
) -> None:
    """Output groups to stdout

    Args:
        config (ScrumConfig): ScrumConfig
        output_config (OutputConfig): Output specific config
        text_config (None): Not used (yet)
        groups (Groups): Groups to output
    """
    pass


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

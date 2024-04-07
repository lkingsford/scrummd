from typing import Optional
from scrummd.collection import Groups, Collection
from scrummd.config import ScrumConfig
from sbl.output import OutputConfig


def text_output(
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

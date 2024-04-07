from typing import Any, Callable, NamedTuple, Optional
from scrummd.collection import Groups, Collection, SortCriteria
from scrummd.config import ScrumConfig


class OutputConfig(NamedTuple):
    """Common run specific config for all types of output"""

    omit_headers: bool = False
    group_by: list[str] = []
    columns: list[str] = ["index", "summary"]


SblOutputGroupedFunction = Callable[[ScrumConfig, OutputConfig, Any, Groups], None]
"""Function for outputting groups"""

SblOutputUngroupedFunction = Callable[
    [ScrumConfig, OutputConfig, Any, Collection], None
]
"""Function for outputting bare collection"""

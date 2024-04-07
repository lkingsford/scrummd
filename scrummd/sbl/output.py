from typing import Callable, NamedTuple, Optional
from scrummd.collection import Groups, Collection, SortCriteria
from scrummd.config import ScrumConfig


class OutputConfig(NamedTuple):
    """Common run specific config for all types of output"""

    omit_headings: bool = False
    group_by: list[str] = []
    columns: list[str] = ["index", "summary"]


SblOutputGroupedFunction = Callable[
    [ScrumConfig, OutputConfig, Optional[any], Groups], None
]
"""Function for outputting groups"""

SblOutputUngroupedFunction = Callable[
    [ScrumConfig, OutputConfig, Optional[any], Collection], None
]
"""Function for outputting bare collection"""

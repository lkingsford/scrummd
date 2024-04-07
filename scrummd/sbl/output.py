from typing import Callable
from scrummd.collection import Groups, Collection
from scrummd.config import ScrumConfig

SblGroupOutputFunction = Callable[[ScrumConfig, Groups, list[str]], None]
"""A function that outputs the results of grouped sbl data"""

SblCollectionOutputFunction = Callable[[ScrumConfig, Collection], None]
"""A function that outputs the results of a collection sbl data"""

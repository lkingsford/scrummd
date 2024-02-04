from io import StringIO
from typing import Optional, TypedDict

from scrumcli.config import ScrumConfig


class ValidationError(ValueError):
    """Triggered if there's a failure validating a card that's being built"""

    pass


class Card(TypedDict):
    """A Scrum 'Card' - might be a chunk of work, might be an epic, might be a ticket."""

    index: Optional[str]
    summary: str


def fromStr(config: ScrumConfig, inputCard: str):
    return Card(index=None, summary="")

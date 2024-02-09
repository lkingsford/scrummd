from typing import Optional, TypedDict
from scrummd.exceptions import ValidationError

from scrummd.config import ScrumConfig
from scrummd.md import extract_fields


class Card(TypedDict):
    """A Scrum 'Card' - might be a chunk of work, might be an epic, might be a ticket."""

    index: Optional[str]
    summary: str


def fromStr(config: ScrumConfig, inputCard: str):
    fields: dict[str, Optional[str]] = extract_fields(inputCard)
    if "index" not in fields:
        fields["index"] = None
    if "summary" not in fields:
        raise ValidationError('"summary" expected but not present')

    return Card(**fields)  # type: ignore

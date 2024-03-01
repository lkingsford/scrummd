"""The ScrumConfig class to configure processing scrum files."""

from dataclasses import dataclass, field
from scrummd import const


@dataclass
class ScrumConfig:
    """The current configuration for processing scrum files."""

    scrum_path: str = const.DEFAULT_SCRUM_FOLDER_NAME
    """Base path for the scrum folder"""

    strict: bool = False
    """Fail on any error with the scrum folder (such as duplicate index or invalid file)"""

    columns: list[str] = field(default_factory=lambda: ["index", "summary"])
    """List of columns to return in output"""

    omit_headers: bool = False
    """Omit headers from output"""

    fields: dict[str, list[str]] = field(default_factory=dict)
    """Fields with limited permitted values and defined order"""

    scard_reference_format: str = "[$index]"
    """Fields to show when a card is referenced in a field in `scard`"""

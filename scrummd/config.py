"""The ScrumConfig class to configure processing scrum files."""

from dataclasses import dataclass, field, fields
from typing import Optional
from scrummd import const


@dataclass
class CollectionConfig:
    """Configuration for any specific collection of cards"""

    fields: dict[str, list[str]] = field(default_factory=dict)
    """Fields with limited permitted values and defined order"""

    required: list[str] = field(default_factory=list)
    """Fields that are required to be in a card"""


@dataclass
class SblConfig:
    """Configuration specific to sbl"""

    columns: list[str] = field(default_factory=lambda: ["index", "summary"])
    """List of columns to return in output"""
    default_group_by: Optional[str] = None
    """Default group-by for sbl"""
    omit_headers: bool = False
    """Omit headers from output"""


@dataclass
class SboardConfig:
    """Configuration specific to sboard"""

    columns: list[str] = field(default_factory=lambda: ["index", "summary"])
    """List of columns to return in output"""
    default_group_by: Optional[str] = None
    """Default group-by for sboard"""


@dataclass
class ScardConfig:
    """Configuration specific to scard"""

    reference_format: str = "[$index]"
    """Fields to show when a card is referenced in a field in `scard`"""


@dataclass
class ScrumConfig(CollectionConfig):
    """The configuration that applies to all cards and ScrumMD"""

    scrum_path: str = const.DEFAULT_SCRUM_FOLDER_NAME
    """Base path for the scrum folder"""

    strict: bool = False
    """Fail on any error with the scrum folder (such as duplicate index or invalid file)"""

    collections: dict[str, CollectionConfig] = field(default_factory=dict)
    """Embedded collection config"""

    scard: ScardConfig = field(default_factory=ScardConfig)

    sbl: SblConfig = field(default_factory=SblConfig)

    sboard: SboardConfig = field(default_factory=SboardConfig)

    def __post_init__(self):
        """Fix up embedded fields, which default to dicts"""

        for key, collection in self.collections.items():
            self.collections[key] = CollectionConfig(**collection)

        if isinstance(self.sbl, dict):
            self.sbl = SblConfig(**self.sbl)
        if isinstance(self.scard, dict):
            self.scard = ScardConfig(**self.scard)
        if isinstance(self.sboard, dict):
            self.sboard = SboardConfig(**self.sboard)

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from scrummd.exceptions import (
    InvalidFileError,
    InvalidRestrictedFieldValueError,
)
from scrummd.config import ScrumConfig
from scrummd.source_md import FieldStr, extract_collection, extract_fields, Field


@dataclass
class Card:
    """A Scrum 'Card' - might be a chunk of work, might be an epic, might be a ticket."""

    index: str
    """Index of the card"""

    summary: str
    """Title of the card - used by default in places like output"""

    collections: list[str]
    """Collections that the card is in"""

    defined_collections: dict[str, list[str]]
    """Collections that are defined by this card"""

    path: str
    """Path of the file for this card"""

    udf: dict[str, Field]
    """All additional fields in the file"""

    def get_field(self, field_name: str) -> Optional[Field]:
        """Get a field from either the card if present, or UDF if not

        Args:
            field_name (str): Field to retrieve

        Returns:
            Field: Field from Card, or UDF if not present
        """
        if field_name not in NON_UDF_FIELDS:
            return self.udf.get(field_name)

        if field_name == "index":
            return FieldStr(self.index)
        if field_name == "summary":
            return FieldStr(self.summary)
        if field_name == "_path":
            return FieldStr(self.path)

        raise NotImplementedError("%f not yet available for output", [field_name])


NON_UDF_FIELDS = ["summary", "collections", "tags", "index"]
"""Fields that are read into the Card itself rather than into the UDF"""


def fromStr(
    config: ScrumConfig,
    input_card: str,
    collection: str,
    path: Path,
) -> Card:
    """Create a card from a string (usually, the file)

    Args:
        config (ScrumConfig): ScrumMD configuration to use.
        input_card (str): String containing the card data from the file.
        collection (str): Collection the card is known to be in.
        index_from_filename (str): Index suggested by the filename of the card

    Raises:
        InvalidFileError: Error with the MD file

    Returns:
        Card: The card for the md file
    """
    fields: dict[str, Field] = extract_fields(input_card)
    collections: list[str] = [collection]
    index = path.name.split(".")[0]
    udf: dict[str, Field] = {k: v for k, v in fields.items() if k not in NON_UDF_FIELDS}

    if "collections" in fields:
        if isinstance(fields["collections"], list):
            collections.extend(fields["collections"])
        else:
            raise InvalidFileError('"Collections" (if present) must be a list')

    if "tags" in fields:
        tags = fields["tags"]
        if isinstance(tags, list):
            collections.extend(fields["tags"])
        else:
            raise InvalidFileError('"tags" (if present) must be a list')

    if "index" in fields:
        if isinstance(fields["index"], list):
            raise InvalidFileError('"index" must not be a list')
        index = fields["index"]

    if "summary" not in fields:
        raise InvalidFileError('"summary" expected but not present')
    if isinstance(fields["summary"], list):
        raise InvalidFileError('"summary" must not be a list')

    for key, value in fields.items():
        if key in config.fields:
            if isinstance(value, str) and value.lower() not in [
                f.lower() for f in config.fields[key]
            ]:
                raise InvalidRestrictedFieldValueError(
                    f'{key} is "{value}". Per configuration, {key} must be one of [{", ".join(config.fields[key])}]'
                )

    defined_collections: dict[str, list[str]] = {}
    if "items" in fields:
        defined_collections[index] = extract_collection(fields["items"])

    for key, value in fields.items():
        if value is not None and (isinstance(value, str) or isinstance(value, list)):
            defined_collection = extract_collection(value)
            if len(defined_collection) > 0:
                defined_collections[key] = defined_collection

    return Card(
        path=str(path),
        summary=fields["summary"],
        index=index,
        collections=collections,
        defined_collections=defined_collections,
        udf=udf,
    )

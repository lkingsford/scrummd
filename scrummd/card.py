from typing import Any, Optional, TypedDict
from scrummd.exceptions import ValidationError, InvalidRestrictedFieldValueError
from scrummd.config import ScrumConfig
from scrummd.source_md import extract_collection, extract_fields


class Card(TypedDict):
    """A Scrum 'Card' - might be a chunk of work, might be an epic, might be a ticket."""

    index: Optional[str]
    summary: str
    _collections: list[str]
    _defined_collections: dict[str, list[str]]
    _path: str


def fromStr(config: ScrumConfig, inputCard: str, collection: list[str] = []) -> Card:
    """Create a card from a string (usually, the file)

    Args:
        config (ScrumConfig): ScrummMD configuration to use.
        inputCard (str): String containing the card data from the file.
        collection (list[str]): Collections the card is known to be in. Defaults to [].

    Raises:
        ValidationError: Error with the MD file

    Returns:
        Card: The card for the md file
    """
    fields: dict[str, Any] = extract_fields(inputCard)
    fields["_collections"] = collection

    if "collections" in fields:
        if isinstance(fields["collections"], list):
            fields["_collections"].extend(fields["collections"])
        else:
            raise ValidationError('"Collections" (if present) must be a list')

    if "tags" in fields:
        if isinstance(fields["tags"], list):
            fields["_collections"].extend(fields["tags"])
        else:
            raise ValidationError('"tags" (if present) must be a list')

    if "index" not in fields:
        fields["index"] = None
    else:
        if isinstance(fields["index"], list):
            raise ValidationError('"index" must not be a list')
    if "summary" not in fields:
        raise ValidationError('"summary" expected but not present')
    if isinstance(fields["summary"], list):
        raise ValidationError('"summary" must not be a list')

    for key, value in fields.items():
        if key in config.fields:
            if value.lower() not in [f.lower() for f in config.fields[key]]:
                raise InvalidRestrictedFieldValueError(
                    f'{key} is "{value}". Per configuration, {key} must be one of [{", ".join(config.fields[key])}]'
                )

    fields["_defined_collections"] = {}
    if "items" in fields:
        extracted_collection = extract_collection(fields["items"])
        fields["_defined_collections"][""] = [
            card["cardIndex"] for card in extracted_collection
        ]

    for key, value in fields.items():
        if value is not None and (isinstance(value, str) or isinstance(value, list)):
            extracted_collection = extract_collection(value)
            if len(extracted_collection) > 0:
                fields["_defined_collections"][key] = [
                    card["cardIndex"] for card in extracted_collection
                ]

    return Card(**fields)  # type: ignore

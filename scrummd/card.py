from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from scrummd.exceptions import (
    InvalidFileError,
    InvalidRestrictedFieldValueError,
    RequiredFieldNotPresentError,
)
from scrummd.config import ScrumConfig, CollectionConfig
from scrummd.source_md import (
    FieldStr,
    extract_collection,
    extract_fields,
    Field,
    ParsedMd,
)


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

    collection_from_path: str
    """Collection that was implied from the path"""

    udf: dict[str, Field]
    """All additional fields in the file"""

    _config: ScrumConfig
    """Config card created with"""

    parsed_md: ParsedMd
    """The MD with additional metadata"""

    def get_field(self, field_name: str) -> Optional[Field]:
        """Get a field from either the card if present, or UDF if not

        Args:
            field_name (str): Field to retrieve

        Returns:
            Optional[Field]: Field from Card, UDF if not present, or None if in neither.
        """
        if field_name not in NON_UDF_FIELDS:
            return self.udf.get(field_name)

        match field_name:
            case "index":
                return FieldStr(self.index)
            case "summary":
                return FieldStr(self.summary)
            case "path":
                return FieldStr(self.path)
            case _:
                raise NotImplementedError(f"{field_name} not yet available for output")

    def assert_valid_rules(self, config: CollectionConfig) -> None:
        """Raise an error if a card doesn't comply with an active configuration

        Args:
            config (ScrumConfig | CollectionConfig): Current Config
                to check against

        Returns:
            None

        Raises:
            RequiredFieldNotPresentError: A field required by the collection's
                `required` config wasn't present.
            InvalidRestrictedFieldValueError: A field was not set to a valid
                value per the collections `fields` config.
        """

        for key, value in self.udf.items():
            if key in config.fields:
                if isinstance(value, str) and value.lower() not in [
                    f.lower() for f in config.fields[key]
                ]:
                    raise InvalidRestrictedFieldValueError(
                        f'{key} is "{value}". Per configuration, {key} must be one of [{", ".join(config.fields[key])}]'
                    )

        for key in config.required:
            if key.lower() not in self.udf.keys():
                raise RequiredFieldNotPresentError(
                    f"{key} is a required field per configuration."
                )

    def __post_init__(self):
        """Perform required validations"""
        self.assert_valid_rules(self._config)


def assert_valid_fields(config: ScrumConfig, fields: ParsedMd) -> None:
    """Raise an error if there is an (internal or config) rule violation

    Args:
        config (ScrumConfig): ScrumMD Config
        fields (dict[str, Field]): Fields of a card to assess

    Raises:
        InvalidFileError: There is an issue with the fields that means it is
            invalid for ScrumMD regardless of configuration.
        InvalidRestrictedFieldValueError: A field with restricted permitted
            values per config has another value present.
        RequiredFieldNotPresentError: A field required by the config is not
            present
    """
    if "collections" in fields:
        if not isinstance(fields["collections"], list):
            raise InvalidFileError('"Collections" (if present) must be a list')

    if "tags" in fields:
        tags = fields["tags"]
        if not isinstance(tags, list):
            raise InvalidFileError('"tags" (if present) must be a list')

    if "index" in fields:
        if isinstance(fields["index"], list):
            raise InvalidFileError('"index" must not be a list')

    if "summary" not in fields:
        raise InvalidFileError('"summary" expected but not present')

    if isinstance(fields["summary"], list):
        raise InvalidFileError('"summary" must not be a list')


NON_UDF_FIELDS = ["summary", "index", "path"]
"""Fields that are read into the Card itself rather than into the UDF"""


def from_parsed(
    config: ScrumConfig, parsed_md: ParsedMd, collection_from_path: str, path: Path
) -> Card:
    """Create a card from a parsed MD file (usually, from a file via extract_fields)

    Args:
        config (ScrumConfig): ScrumMD configuration to use.
        parsed_md (ParsedMd): The ParsedMd file to create the card with
        collection_from_path (str): Collection from the relative path
        path (Path): Path of the file

    Raises:
        InvalidFileError: Error with the MD file
        InvalidRestrictedFieldValueError: A field with restricted permitted
            values per config has another value present.
        RequiredFieldNotPresentError: A field required by the config is not
            present

    Returns:
        Card: The card for the md file
    """

    collections: list[str] = [collection_from_path]

    index = path.name.split(".")[0]
    udf: dict[str, Field] = {
        k: v for k, v in parsed_md.items() if k not in NON_UDF_FIELDS
    }

    assert_valid_fields(config, parsed_md)

    if "index" in parsed_md:
        assert isinstance(parsed_md["index"], str)
        index = str(parsed_md["index"])

    # collections is a UDF field (as what's in the file) as is tags, but both
    # comprise of the actual collections that it's in.
    if "collections" in parsed_md:
        # Little back forward here to appease the typechecker
        parsed_collections = parsed_md["collections"]
        assert isinstance(parsed_collections, list)
        collections.extend(parsed_collections)

    if "tags" in parsed_md:
        parsed_tags = parsed_md["tags"]
        assert isinstance(parsed_tags, list)
        collections.extend(parsed_tags)

    defined_collections: dict[str, list[str]] = {}
    if "items" in parsed_md:
        defined_collections[index] = extract_collection(parsed_md["items"])

    for key, value in parsed_md.items():
        if value is not None and (isinstance(value, str) or isinstance(value, list)):
            defined_collection = extract_collection(value)
            if len(defined_collection) > 0:
                defined_collections[f"{index}.{key}"] = defined_collection

    parsed_summary = parsed_md["summary"]
    assert isinstance(parsed_summary, str)
    new_card = Card(
        path=str(path),
        collection_from_path=collection_from_path,
        summary=parsed_summary,
        index=index,
        collections=collections,
        defined_collections=defined_collections,
        udf=udf,
        _config=config,
        parsed_md=parsed_md,
    )

    return new_card


def from_str(
    config: ScrumConfig,
    input_card: str,
    collection_from_path: str,
    path: Path,
) -> Card:
    """Create a card from a string (usually, the file)

    Args:
        config (ScrumConfig): ScrumMD configuration to use.
        input_card (str): String containing the card data from the file.
        collection_from_path (str): Collection the card is known to be from the relative path.
        path (Path): Path of the file

    Raises:
        InvalidFileError: Error with the MD file
        InvalidRestrictedFieldValueError: A field with restricted permitted
            values per config has another value present.
        RequiredFieldNotPresentError: A field required by the config is not
            present

    Returns:
        Card: The card for the md file
    """
    parsed_md: ParsedMd = extract_fields(config, input_card)
    return from_parsed(config, parsed_md, collection_from_path, path)

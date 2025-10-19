from dataclasses import dataclass
import re
import itertools
from copy import deepcopy
from enum import Enum
from typing import Optional, TYPE_CHECKING
from collections.abc import ItemsView, KeysView
import logging

from scrummd.config import ScrumConfig
from scrummd.exceptions import (
    InvalidFileError,
    ImplicitChangeOfTypeError,
    UnsupportedModificationError,
    NotAListError,
    FieldNotPresentError,
    ValuesNotPresentError,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from scrummd.card import Card
    from scrummd.collection import Collection


class FIELD_MD_TYPE(Enum):
    """How the field appears in the md file itself"""

    IMPLICIT = 0
    PROPERTY = 1
    BLOCK = 2
    LIST_PROPERTY = 3
    LIST_HEADER = 4
    IMPLICIT_SUMMARY = 5


class FIELD_GROUP_TYPE(Enum):
    """Type of group these fields are in"""

    UNSET = (0,)
    PROPERTY_BLOCK = (1,)
    HEADER_BLOCK = (2,)
    IMPLICIT_SUMMARY = 3


"""Fields types that are grouped together in output"""
GROUPED_TYPES = {
    FIELD_MD_TYPE.IMPLICIT: FIELD_GROUP_TYPE.UNSET,
    FIELD_MD_TYPE.PROPERTY: FIELD_GROUP_TYPE.PROPERTY_BLOCK,
    FIELD_MD_TYPE.LIST_PROPERTY: FIELD_GROUP_TYPE.PROPERTY_BLOCK,
    FIELD_MD_TYPE.BLOCK: FIELD_GROUP_TYPE.HEADER_BLOCK,
    FIELD_MD_TYPE.LIST_HEADER: FIELD_GROUP_TYPE.HEADER_BLOCK,
    FIELD_MD_TYPE.IMPLICIT_SUMMARY: FIELD_GROUP_TYPE.IMPLICIT_SUMMARY,
}

GroupedKeys = list[tuple[FIELD_GROUP_TYPE, list[str]]]


class FieldComponent:
    """A section of the field component"""


@dataclass
class CardComponent(FieldComponent):
    """A component of the field that refers to a card"""

    card_index: str
    """The index of the card"""

    card: Optional["Card"] = None
    """The referred to card"""

    def __post_init__(self):
        if self.card == None:
            logger.warning(f"Card index {self.card_index} referred to but not found.")


@dataclass
class StringComponent(FieldComponent):
    """A component of the field that is just a string"""

    value: str


_extract_collection_re = re.compile(r"\[\[([^!][^\]\n]*)\]\]")
"""Regex expression used to extract the [[cardindexes]] out of a field for a collection, ignoring [[!]] cards"""

_extract_card_component_re = re.compile(r"\[\[[!]*([^\]\n]*)\]\]")
"""Regex expression used to extract the [[cardindexes]] out of a field to store in the field, including [[!]] cards"""

_extract_header_level_re = re.compile(r"^#*")
"""Regex expression used to extract the amount of #'s"""

_extract_octothorpless_header_re = re.compile("^#*(.*)")
"""Regex to get the bits without #"""


class FieldStr(str):
    """A str with the extra parsed information from the str"""

    _components: Optional[list[FieldComponent]]

    def __init__(self, value):
        super().__init__()
        self._components = None

    def components(self, collection: "Collection") -> list[FieldComponent]:
        """Break the field string into its components. This can be used for when the card is outputted to - for instance - format the strings.

        Returns:
            list[FieldComponent]: All the components of the str.
        """

        # Caching in case used again. Only need to do once, because strings are immutable.
        if self._components:
            return self._components

        self._components = []
        cursor = 0
        for match in _extract_card_component_re.finditer(self):
            if match.start() != cursor:
                self._components.append(StringComponent(self[cursor : match.start()]))

            self._components.append(
                CardComponent(match.group(1), collection.get(match.group(1)))
            )
            cursor = match.end()
        if cursor != len(self):
            self._components.append(StringComponent(self[cursor:]))

        return self._components


class FieldNumber(float, FieldComponent):
    """A float with the extra parsed information"""

    pass


Field = FieldStr | list[FieldStr] | FieldNumber
"""A field from the md file"""


@dataclass
class FieldMetadata:
    """Metadata for a field

    Stores the logical type of the field, as well as the original field name.
    """

    md_type: FIELD_MD_TYPE
    """The physical type of the field, as it appears in the md file"""

    raw_field_name: str
    """The original field name, as it appears in the md file."""

    header_level: int
    """The amount of #'s (or lines under) of the header"""


class ParsedMd:
    """A dictionary of the MD with additional metadata from the md file"""

    def __init__(self) -> None:
        """
        Constructor for ParsedMd.

        Does nothing else, but is a docstring placeholder.
        """
        self._fields: dict[str, Field] = {}
        self._meta: dict[str, FieldMetadata] = {}
        self._order: list[str] = []

    def __getitem__(self, key: str) -> Field:
        """
        Gets an item from the fields.

        Args:
            key (str): The key of the item to retrieve.

        Returns:
            Field: The value of the item.
        """
        return self._fields[key]

    def __contains__(self, key: str) -> bool:
        """
        Checks if a key is in the fields.

        Args:
            key (str): The key to check for.

        Returns:
            bool: True if the key is in the fields, false otherwise.
        """
        return key in self._fields

    def items(self) -> ItemsView[str, Field]:
        """
        Exposes the field dict items().

        Returns:
            list[tuple[str, Field]]: The items of the field dict.
        """
        return self._fields.items()

    def keys_grouped_by_field_md_type(self) -> GroupedKeys:
        """
        Field IDs grouped by the blocks of data types in the original source.

        Used for recreating the md file from scratch. Property/Property Lists are included in the
        same group. It's possible to have multiple groups of the same type of field (for instance -
        if there's multiple property blocks)

        Returns:
            list[list[key]]: Ordered groups, with ordered lists of keys.
        """
        return [
            # Converting to a list to open up more possibilities of use when formatting
            (group[0] or FIELD_GROUP_TYPE.IMPLICIT_SUMMARY, list(group[1]))
            for group in itertools.groupby(
                self._order, lambda k: GROUPED_TYPES.get(self._meta[k].md_type)
            )
        ]

    def copy(self) -> "ParsedMd":
        """
        Creates a new ParsedMd with the same fields and metadata.

        Returns:
            ParsedMd: A new ParsedMd with the same fields and metadata.
        """
        # TBD if this is fast enough or overkill
        return deepcopy(self)

    def keys(self) -> KeysView[str]:
        """
        Exposes the field dict keys().

        Returns:
            list[str]: The keys of the field dict.
        """
        return self._fields.keys()

    def append_field(
        self, raw_key: str, value: Field, md_type: FIELD_MD_TYPE, header_level: int = 1
    ) -> None:
        """
        Add a field to the field dictionary, storing its location in metadata.

        Args:
            key (str): The key of the field to add.
            value (Field): The value of the field to add.
            md_type (FIELD_MD_TYPE): The type of the field in the md file.
        """
        key = raw_key.casefold()
        self._fields[key] = value
        self._meta[key] = FieldMetadata(md_type, raw_key, header_level)
        self._order.append(key)

    def insert_field(
        self,
        raw_key: str,
        value: Field,
        md_type: FIELD_MD_TYPE,
        index: int,
        header_level: int = 1,
    ) -> None:
        """
        Add a field to the field dictionary, storing its location in metadata.

        Args:
            key (str): The key of the field to add.
            value (Field): The value of the field to add.
            md_type (FIELD_MD_TYPE): The type of the field in the md file.
            index (int): The index to insert the field at.
        """
        key = raw_key.casefold()
        self._fields[key] = value
        self._meta[key] = FieldMetadata(md_type, raw_key, header_level)
        self._order.insert(index, key)

    def remove_field(self, key: str) -> None:
        """
        Remove a field from the field dictionary.

        Args:
            key (str): The key of the field to remove.
        """
        del self._fields[key]
        self._meta.pop(key)
        self._order.remove(key)

    def order(self) -> list[str]:
        """
        Returns the order of the fields.

        Returns:
            list[str]: The order of the fields.
        """
        return list(self._order)

    def meta(self, key: str) -> FieldMetadata:
        """
        Returns the metadata for a field.

        Args:
            key (str): The key of the field to get the metadata of.

        Returns:
            FieldMetadata: The metadata of the field.
        """
        return self._meta[key]


    def set_fields(self, config: ScrumConfig, fields_to_set: list[tuple[str, str]]) -> "ParsedMd":
        """
        Sets all fields in fields_to_set to their respective values (creating them if they don't
            exist. Returns a new ParsedMd with the new value.

        Args:
            config (ScrumConfig): The config to use for type checking.
            fields_to_set (list[tuple[str, str]]): Fields to set or create.
                Each change is in the form of (FieldToChange, ValueToSetItTo).
        """
        new_md = self.copy()
        for raw_key, new_value in fields_to_set:
            key = raw_key.casefold()
            if key == "index":
                raise UnsupportedModificationError(
                    "Index can not be modified inside ScrumMD"
                )

            # There's not _really_ enough overlap here to reuse the code in extract_fields (given
            # that there's more code there to figure out what type it is, which isn't so relevant
            # here)
            stripped = new_value.strip()
            if (
                len(new_value) > 1
                and stripped.startswith("-")
                and not (stripped.startswith("---"))
                and all(v.strip().startswith("-") for v in new_value.split("\n"))
            ):
                # Treating as list
                field: Field = [FieldStr(v[1:].strip()) for v in stripped.split("\n")]
            else:
                field = typed_field(stripped)

            if key not in self._fields:
                logical_type = _logical_type(config, key, field)
                # Fixed logical header for new fields for now.
                logical_header_level = (
                    0 if logical_type == FIELD_MD_TYPE.PROPERTY else 1
                )
                meta = FieldMetadata(logical_type, raw_key, logical_header_level)
                new_md._meta[key] = meta
                if logical_type == FIELD_MD_TYPE.IMPLICIT_SUMMARY:
                    new_md._order.insert(0, key)
                else:
                    new_md._order.append(key)

            if new_md._meta[key].md_type == FIELD_MD_TYPE.PROPERTY:
                _assert_valid_as_property(key, field)

            new_md._fields[key] = field
        return new_md

    def add_to_list(
        self, config: ScrumConfig, field: str, values: list[str]
    ) -> "ParsedMd":
        """
        Add an item to a field list, returning a new ParsedMd

        Args:
            config (ScrumConfig): The config to use for type checking..
            field (str): The field to add to.
            values (list[str]): The values to add to the field.

        Raises:
            NotAListError: Raised when the field to be written to is not a list.
            FieldNotPresentError: Raised when the field is not present in the file.
        """
        # Need a deepcopy, because we're modifying (not replacing) child objects.
        new_md = deepcopy(self)
        key = field.casefold()
        if key not in self._fields:
            raise FieldNotPresentError(field)

        meta = self._meta.get(key)
        assert meta
        if meta.md_type not in (FIELD_MD_TYPE.LIST_HEADER, FIELD_MD_TYPE.LIST_PROPERTY):
            raise NotAListError(field)

        field_list = new_md._fields.get(key)
        assert field_list
        assert isinstance(field_list, list)

        for value in values:
            field_list.append(FieldStr(value.strip()))

        return new_md

    def remove_from_list(
        self, config: ScrumConfig, field: str, values: list[str]
    ) -> "ParsedMd":
        """
        Remove an item from a field list, returning a new ParsedMD. Multiple matching items will
        result in only the first being removed.

        Args:
            config (ScrumConfig): The config to use for type checking..
            field (str): The field to add to.
            values (list[str]): The (case insensitive) values to remove from the field.


        Raises:
            NotAListError: Raised when the field to be written to is not a list.
            FieldNotPresentError: Raised when the field is not present in the file.
            ValuesNotPresentError: Raised when the value is not present in the list to remove.
        """

        # Need a deepcopy, because we're modifying (not replacing) child objects.
        new_md = deepcopy(self)
        key = field.casefold()
        if key not in self._fields:
            raise FieldNotPresentError(field)

        meta = self._meta.get(key)
        assert meta
        if meta.md_type not in (FIELD_MD_TYPE.LIST_HEADER, FIELD_MD_TYPE.LIST_PROPERTY):
            raise NotAListError(field)

        field_list = new_md._fields.get(key)
        assert field_list
        assert isinstance(field_list, list)

        prepped_values = [value.strip().casefold() for value in values]
        logger.info("before {}", prepped_values)

        # Can't use filterfalse, because removing only the first. We at least only get one pass,
        # right? And _should_ speed up as we go. (At the expense of a little extra big O).
        for field_value in field_list[:]:
            liberal_value = field_value.casefold()

            if liberal_value in prepped_values:
                prepped_values.remove(liberal_value)
                field_list.remove(field_value)

        if prepped_values:
            logger.info(prepped_values)
            raise ValuesNotPresentError(prepped_values, field)

        return new_md


def _logical_type(config: ScrumConfig, key: str, field: Field) -> FIELD_MD_TYPE:
    """Returns the most sensible (or necessary) type for this field

    Args:
        config (ScrumConfig): Full ScrumMD config
        key (str): Name of the field
        field (Field): Value of the field

    Returns:
        FIELD_MD_TYPE: The suggested physical type of the field
    """
    if config.allow_header_summary and key == "summary":
        return FIELD_MD_TYPE.IMPLICIT_SUMMARY
    if isinstance(field, list):
        return FIELD_MD_TYPE.LIST_PROPERTY
    if isinstance(field, FieldStr) and "\n" not in field:
        return FIELD_MD_TYPE.PROPERTY
    return FIELD_MD_TYPE.BLOCK


def _assert_valid_as_property(field_name: str, field: Field) -> None:
    """Raise an exception if the field is currently a property, and its new value doesn't support it.

    Args:
        field_name (str): Name of the field
        field (Field): Value that is attempting to be saved

    Raises:
        ImplicitChangeOfTypeError: If the existing physical type doesn't support the new value of
            the field
    """
    # TODO: Add an 'overwrite type' option
    if isinstance(field, FieldStr) and ("\n" in field):
        raise ImplicitChangeOfTypeError(
            "Attempting to set property %s to a multi-line string.", field_name
        )

    if isinstance(field, list) and any(("\n" in entry) for entry in field):
        raise ImplicitChangeOfTypeError(
            "Attempting to set entry in list %s to include a multi-line string.",
            field_name,
        )


def get_raw_block_name(md_line: str) -> str:
    """Get the name of the block from the header line

    Args:
        md_line (str): Line to remove any preceeding '#'s from

    Returns
        str: Text of header
    """
    results = re.match(r"\#+(.*)", md_line)
    if results is not None:
        return results.group(1).strip()
    else:
        raise InvalidFileError("%s has no valid header", md_line)


def split_property(md_line: str) -> tuple[str, str]:
    """Split the property into its key and value

    Args:
        md_line (str): Line in the format of "key: value" to split

    Returns:
        tuple(str, str): Key and value
    """
    results = re.match(r"\W*([^\:]+)\:(.*)", md_line)
    if results is not None:
        return (results.group(1).strip(), results.group(2).strip())
    else:
        raise InvalidFileError("Error parsing property line %s", md_line)


def split_list_item(md_line: str) -> str:
    """Return the 'value' part of a list, stripping the bullet

    Args:
        md_line (str): Line to split

    Returns:
        str: Output after '-'
    """
    if len(md_line) > 1:
        return md_line[1:].strip()
    else:
        return ""


def extract_collection(field_value: Field) -> list[str]:
    """Extract all of the card ids from a field (str or list of strings)

    Args:
        field_value (Field): Field from the md file

    Returns:
        list[Index]: A list of all card indexes
    """
    field_list: list[Field] = []
    if isinstance(field_value, list):
        field_list.extend(field_value)
    else:
        field_list.append(field_value)

    results = []
    for value in field_list:
        results.extend(_extract_collection_re.findall(str(value)))
    return results


def typed_field(field: str) -> Field:
    """Return a Field of an appropriate type from the string

    Currently supports strings and numbers - not lists.

    Args:
        field (str): Field value to interpret

    Returns:
        Field: A correctly typed field
    """

    try:
        # I don't really like doing this as a non-exceptional exception, but it
        # is at least clear
        return FieldNumber(field)
    except ValueError:
        return FieldStr(field)


def extract_fields(config: ScrumConfig, md_file: str) -> ParsedMd:
    """Extract all fields from the md_file

    There are two types of fields:
    - 'Property' style fields
    - 'md header' style fields:

    There are two types of value:
    - Strings
    - Lists

    Lists are defined as items in a list of items starting with '-' and ending with a newline following the header or property.

    All keys are case insensitive and made lowercase.

    Args:
        md_file (str): Contents of file to get data out of

    Returns:
        dict[str, Field]: a dictionary of all field names and values
    """

    parsed: ParsedMd = ParsedMd()

    class BlockStatus(Enum):
        NO_BLOCK = 0
        IN_PROPERTY_BLOCK = 1
        IN_HEADER_BLOCK = 2
        IN_PROPERTY_LIST = 3
        IN_HEADER_LIST = 4
        IN_CODE_BLOCK = 5

    block_name: Optional[str] = None
    block_status = BlockStatus.NO_BLOCK
    block_value = ""
    list_field_key = ""
    raw_block_name = ""
    header_level = 0

    for line in md_file.splitlines():
        stripped_line = line.strip()
        if len(stripped_line) == 0:
            block_value += "\n"
            continue

        if block_status == BlockStatus.NO_BLOCK:
            if stripped_line == "---":
                block_status = BlockStatus.IN_PROPERTY_BLOCK
                continue
            elif stripped_line[0] == "#":
                raw_block_name = get_raw_block_name(stripped_line)
                block_name = raw_block_name
                block_value = ""
                block_status = BlockStatus.IN_HEADER_BLOCK
                starting_hashes = _extract_header_level_re.match(stripped_line)
                assert starting_hashes
                header_level = len(starting_hashes[0])
                assert header_level > 0
                continue
            elif stripped_line.startswith("====") or stripped_line.startswith("----"):
                # Currently, ==== and ---- are conflated, but they may become
                # first and second level headers respectively
                block_value_lines = block_value.splitlines()
                if len(block_value_lines) > 1:
                    raw_block_name = block_value_lines[-1].strip()
                    block_name = (block_value_lines[-1]).casefold()
                    block_value = ""
                    header_level = 1 if stripped_line[0] == "=" else 2
                    block_status = BlockStatus.IN_HEADER_BLOCK
                    continue
            else:
                block_value += line
                continue

        if block_status == BlockStatus.IN_PROPERTY_LIST:
            if stripped_line[0] == "-" and stripped_line != "---":
                value = split_list_item(stripped_line)
                field_list = parsed[list_field_key]
                assert isinstance(field_list, list)
                field_list.append(FieldStr(value))
                continue
            else:
                block_status = BlockStatus.IN_PROPERTY_BLOCK

        if block_status == BlockStatus.IN_PROPERTY_BLOCK:
            if stripped_line == "---":
                block_status = BlockStatus.NO_BLOCK
                continue
            if ":" not in stripped_line:
                raise InvalidFileError("Invalid property line %s", stripped_line)
            raw_list_field_key, value = split_property(stripped_line)
            if value == "":
                block_status = BlockStatus.IN_PROPERTY_LIST
                list_field_key = raw_list_field_key.casefold()
                parsed.append_field(
                    raw_list_field_key, [], FIELD_MD_TYPE.LIST_PROPERTY, 0
                )
            else:
                parsed.append_field(
                    raw_list_field_key, typed_field(value), FIELD_MD_TYPE.PROPERTY, 0
                )
            continue

        if block_status == BlockStatus.IN_HEADER_LIST:
            if stripped_line[0] == "-" and stripped_line != "---":
                value = split_list_item(stripped_line)
                field_list = parsed[list_field_key]
                assert isinstance(field_list, list)
                field_list.append(FieldStr(value))
                continue
            else:
                block_name = None
                block_status = BlockStatus.IN_HEADER_BLOCK

        if block_status == BlockStatus.IN_CODE_BLOCK:
            if "```" in stripped_line:
                block_status = BlockStatus.IN_HEADER_BLOCK
            block_value += line + "\n"
            continue

        if block_status == BlockStatus.IN_HEADER_BLOCK:
            if stripped_line == "---":
                block_status = BlockStatus.IN_PROPERTY_BLOCK
                if block_name is not None:
                    parsed.append_field(
                        raw_block_name,
                        FieldStr(block_value.strip()),
                        FIELD_MD_TYPE.BLOCK,
                        header_level,
                    )
                block_value = ""
                continue
            elif stripped_line.startswith("====") or stripped_line.startswith("----"):
                # Currently, ==== and ---- are conflated, but they may become
                # first and second level headers respectively
                block_value_lines = block_value.splitlines()
                if block_name is not None:
                    if len(block_value_lines) > 1:
                        parsed.append_field(
                            raw_block_name,
                            typed_field("\n".join(block_value_lines[0:-1]).strip()),
                            FIELD_MD_TYPE.BLOCK,
                            header_level,
                        )
                if len(block_value_lines) > 1:
                    raw_block_name = (block_value_lines[-1]).strip()
                    block_name = raw_block_name.casefold()
                    header_level = 1 if stripped_line[0] == "=" else 2
                block_value = ""
            elif stripped_line[0] == "#":
                block_status = BlockStatus.IN_HEADER_BLOCK
                if block_name is not None:
                    assert header_level > 0
                    parsed.append_field(
                        raw_block_name,
                        typed_field(block_value.strip()),
                        FIELD_MD_TYPE.BLOCK,
                        header_level,
                    )
                raw_block_name = get_raw_block_name(stripped_line)
                starting_hashes = _extract_header_level_re.match(stripped_line)
                assert starting_hashes
                header_level = len(starting_hashes[0])
                block_name = raw_block_name.casefold()
                block_value = ""
                continue
            elif stripped_line[0] == "-" and block_value.strip() == "":
                block_status = BlockStatus.IN_HEADER_LIST
                if raw_block_name is not None:
                    list_field_key = raw_block_name.casefold()
                parsed.append_field(
                    raw_block_name,
                    [FieldStr(split_list_item(stripped_line))],
                    FIELD_MD_TYPE.LIST_HEADER,
                    header_level,
                )
            elif "```" in stripped_line:
                block_status = BlockStatus.IN_CODE_BLOCK
                block_value += line + "\n"
            else:
                block_value += line + "\n"

    if block_status == BlockStatus.IN_HEADER_BLOCK:
        if block_name is not None:
            parsed.append_field(
                raw_block_name,
                FieldStr(block_value.strip()),
                FIELD_MD_TYPE.BLOCK,
                header_level,
            )

    if config.allow_header_summary and "summary" not in parsed:
        possible_headers: list[str] = [
            key
            for key, value in parsed.items()
            if value == None or (isinstance(value, FieldStr) and len(value) == 0)
        ]
        if len(possible_headers) == 1:
            header_key = possible_headers[0]
            # Need to get the actual casing of the summary -
            # the summary has been CaseFold. By doing a second pass
            # we can reduce the complexity of holding the data in
            # the algorithm proper
            for line in md_file.splitlines():
                summary_text_matches = _extract_octothorpless_header_re.search(line)
                assert summary_text_matches is not None
                content_text = summary_text_matches[1].casefold().strip()
                if content_text == header_key:
                    previous_position = parsed.order().index(header_key)
                    summary_text = _extract_octothorpless_header_re.search(line)
                    parsed.insert_field(
                        "Summary",
                        FieldStr(summary_text_matches[1].strip()),
                        FIELD_MD_TYPE.IMPLICIT_SUMMARY,
                        previous_position,
                    )
                    parsed.remove_field(header_key)
                    break
        else:
            raise InvalidFileError("No clear summary field")

    return parsed

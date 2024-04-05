from dataclasses import dataclass
import re

from enum import Enum
from typing import Optional, Any, Union

from scrummd.exceptions import InvalidFileError


class FieldComponent:
    """A section of the field component"""

    pass


@dataclass
class CardComponent(FieldComponent):
    """A component of the field that refers to a card"""

    cardIndex: str


@dataclass
class StringComponent(FieldComponent):
    """A component of the field that is just a string"""

    value: str


_extract_re = re.compile(r"\[\[([^\]\n]*)\]\]")
"""Regex expression used to extract the [[cardindexes]] out of a field"""


class FieldStr(str):
    """A str with the extra parsed information from the str"""

    _components: list[FieldComponent]

    def __init__(self, value):
        super().__init__()
        self._components = None

    def components(self) -> list[FieldComponent]:
        """Break the field string into its components. This can be used for when the card is outputted to - for instance - format the strings.

        Returns:
            list[FieldComponent]: All the components of the str.
        """

        # Caching in case used again. Only need to do once, because strings are immutable.
        if self._components:
            return self._components

        self._components = []
        cursor = 0
        for match in _extract_re.finditer(self):
            if match.start() != cursor:
                self._components.append(StringComponent(self[cursor : match.start()]))

            self._components.append(CardComponent(match.group(1)))
            cursor = match.end()
        if cursor != len(self):
            self._components.append(StringComponent(self[cursor:]))

        return self._components


FieldNumber = float

Field = FieldStr | list[FieldStr] | FieldNumber
"""A field from the md file"""


def get_block_name(md_line: str) -> str:
    """Get the name of the block from the header line"""
    results = re.match(r"\#+(.*)", md_line)
    if results is not None:
        return results.group(1).casefold().strip()
    else:
        raise InvalidFileError("%s has no valid header", md_line)


def split_property(md_line: str) -> tuple[str, str]:
    """Split the property"""
    results = re.match(r"\W*([^\:]+)\:(.*)", md_line)
    if results is not None:
        return (results.group(1).casefold().strip(), results.group(2).strip())
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
        results.extend(_extract_re.findall(str(value)))
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


def extract_fields(md_file: str) -> dict[str, Field]:
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

    fields: dict[str, Field] = {}

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
                block_name = get_block_name(stripped_line)
                block_value = ""
                block_status = BlockStatus.IN_HEADER_BLOCK
                continue

        if block_status == BlockStatus.IN_PROPERTY_LIST:
            if stripped_line[0] == "-" and stripped_line != "---":
                value = split_list_item(stripped_line)
                field_list = fields[list_field_key]
                assert isinstance(field_list, list)
                field_list.append(FieldStr(value))
                continue
            else:
                list_field_key = ""
                block_status == BlockStatus.IN_PROPERTY_BLOCK

        if block_status == BlockStatus.IN_PROPERTY_BLOCK:
            if stripped_line == "---":
                block_status = BlockStatus.NO_BLOCK
                continue
            if ":" not in stripped_line:
                raise InvalidFileError("Invalid property line %s", stripped_line)
            key, value = split_property(stripped_line)
            if value == "":
                block_status = BlockStatus.IN_PROPERTY_LIST
                list_field_key = key
                fields[list_field_key] = []
            else:
                fields[key] = typed_field(value)
            continue

        if block_status == BlockStatus.IN_HEADER_LIST:
            if stripped_line[0] == "-" and stripped_line != "---":
                value = split_list_item(stripped_line)
                field_list = fields[list_field_key]
                assert isinstance(field_list, list)
                field_list.append(FieldStr(value))
                continue
            else:
                list_field_key = ""
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
                    fields[block_name] = typed_field(block_value)
                block_value = ""
                continue
            elif stripped_line[0] == "#":
                block_status = BlockStatus.IN_HEADER_BLOCK
                if block_name is not None:
                    fields[block_name] = typed_field(block_value.strip())
                block_name = get_block_name(stripped_line)
                block_value = ""
                continue
            elif stripped_line[0] == "-" and block_value.strip() == "":
                block_status = BlockStatus.IN_HEADER_LIST
                if block_name is not None:
                    list_field_key = block_name
                fields[list_field_key] = [FieldStr(split_list_item(stripped_line))]
            elif "```" in stripped_line:
                block_status = BlockStatus.IN_CODE_BLOCK
                block_value += line + "\n"
            else:
                block_value += line + "\n"

    if block_status == BlockStatus.IN_HEADER_BLOCK:
        if block_name is not None:
            fields[block_name] = FieldStr(block_value)

    return fields

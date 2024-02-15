import re

from enum import Enum
from typing import Optional, Any

from scrummd.exceptions import ValidationError


def get_block_name(md_line: str) -> str:
    """Get the name of the block from the header line"""
    results = re.match(r"\#+(.*)", md_line)
    if results is not None:
        return results.group(1).lower().strip()
    else:
        raise ValidationError("%s has no valid header", md_line)


def split_property(md_line: str) -> tuple[str, str]:
    """Split the property"""
    results = re.match(r"\W*([^\:]+)\:(.*)", md_line)
    if results is not None:
        return (results.group(1).lower().strip(), results.group(2).strip())
    else:
        raise ValidationError("Error parsing property line %s", md_line)


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


def extract_fields(md_file: str) -> dict[str, Any]:
    """Extract all fields from the md_file

    There are two types of fields:
    - 'Property' style fields:
      ---
      `Key: Value`
      `Key2: Value2`
      ---
    - 'md header' style fields:
      `# key
      Value

    There are two types of value:
    - Strings
    - Lists

    Lists are defined as items in a list of items starting with '-' and ending with a newline following the header or property.

    All keys are case insensitive and made lowercase.
    """

    fields: dict[str, Any] = {}

    class BlockStatus(Enum):
        NO_BLOCK = 0
        IN_PROPERTY_BLOCK = 1
        IN_HEADER_BLOCK = 2
        IN_PROPERTY_LIST = 3
        IN_HEADER_LIST = 4

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
                fields[list_field_key].append(value)
                continue
            else:
                list_field_key = ""
                block_status == BlockStatus.IN_PROPERTY_BLOCK

        if block_status == BlockStatus.IN_PROPERTY_BLOCK:
            if stripped_line == "---":
                block_status = BlockStatus.NO_BLOCK
                continue
            if ":" not in stripped_line:
                raise ValidationError("Invalid property line %s", stripped_line)
            key, value = split_property(stripped_line)
            if value == "":
                block_status = BlockStatus.IN_PROPERTY_LIST
                list_field_key = key
                fields[list_field_key] = []
            else:
                fields[key] = value
            continue

        if block_status == BlockStatus.IN_HEADER_LIST:
            if stripped_line[0] == "-" and stripped_line != "---":
                value = split_list_item(stripped_line)
                fields[list_field_key].append(value)
                continue
            else:
                list_field_key = ""
                block_status = BlockStatus.IN_HEADER_BLOCK

        if block_status == BlockStatus.IN_HEADER_BLOCK:
            if stripped_line == "---":
                block_status = BlockStatus.IN_PROPERTY_BLOCK
                if block_name is not None:
                    fields[block_name] = block_value
                block_value = ""
                continue
            elif stripped_line[0] == "#":
                block_status = BlockStatus.IN_HEADER_BLOCK
                if block_name is not None:
                    fields[block_name] = block_value.strip()
                block_name = get_block_name(stripped_line)
                block_value = ""
                continue
            elif stripped_line[0] == "-" and block_value.strip() == "":
                block_status = BlockStatus.IN_HEADER_LIST
                if block_name is not None:
                    list_field_key = block_name
                fields[list_field_key] = [split_list_item(stripped_line)]
            else:
                block_value += line + "\n"

    if block_status == BlockStatus.IN_HEADER_BLOCK:
        if block_name is not None:
            fields[block_name] = block_value

    return fields

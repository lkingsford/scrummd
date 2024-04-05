"""Display any number of scrum cards"""

import argparse
import logging
import re
from typing import Optional
from scrummd.card import Card
from scrummd.collection import Collection, get_collection
from scrummd.config import ScrumConfig
from scrummd.config_loader import load_fs_config
from scrummd.source_md import (
    CardComponent,
    Field,
    FieldNumber,
    FieldStr,
    StringComponent,
)
from scrummd.version import version_to_output

logger = logging.getLogger(__name__)

_field_re = re.compile(r"\$(\w+)")


def format_field(value: Optional[Field]) -> str:
    """Format a given field for output

    Args:
        value (Optional[Field]): Field to output

    Raises:
        TypeError: Field is not a recognised formattable type

    Returns:
        str: Field suitable to use in output
    """
    if value is None:
        return ""
    if isinstance(value, FieldStr):
        return value
    if isinstance(value, list):
        return f"[{', '.join(value)}]"
    if isinstance(value, FieldNumber):
        return f"{value:g}"
    else:
        raise TypeError(f"Unsupported type {type(value)}")


def format_card_summary(config: ScrumConfig, card: Card) -> str:
    """Format the summary of a card per the config

    Args:
        config (ScrumConfig): Active scrum configuration
        card (Card): Card to format

    Returns:
        str: Card formatted per configuration
    """
    format = config.scard_reference_format

    output = _field_re.sub(lambda m: format_field(card.get_field(m.group(1))), format)
    return output


def output_fieldstr(config: ScrumConfig, value: Field, collection: Collection) -> str:
    """Generate the formatted output value for the field from the components

    Args:
        config (ScrumConfig): Active scrum configuration
        value (FieldStr): Value to generate output for
        collection (Collection): Full collection of cards for reference's sake

    Returns:
        str: Output ready field
    """
    output = ""
    if not isinstance(value, FieldStr) and isinstance(value, str):
        # Likely index
        return value

    if isinstance(value, FieldStr):
        for component in value.components():
            if isinstance(component, StringComponent):
                output += component.value
            elif isinstance(component, CardComponent):
                card = collection.get(component.cardIndex)
                if card:
                    output += format_card_summary(config, card)
                else:
                    output += f"[[{component.cardIndex}]] (NOT FOUND)"
                    logger.warning(
                        f"Card index {component.cardIndex} not found when expanding"
                    )
                    # Should strict fail here?
            else:
                raise ValueError("Component of invalid type")

    return output


def output_cards(config: ScrumConfig, collection: Collection, card_indexes: list[str]):
    """Output cards to stdout

    Args:
        config (ScrumConfig): Current configuration
        collection (Collection): Complete collection of cards
        card_index (list[str]): Indexes of cards to output
    """

    for card_index in card_indexes:
        if card_index not in collection:
            logger.error("Card %s not found", card_index)
            continue
        card = collection[card_index]
        print("---")
        print(f"{card_index}: {card.summary}")
        print("---")
        for k, v in card.udf.items():
            if v is None:
                continue

            if isinstance(v, list):
                for item in v:
                    formatted_value = output_fieldstr(config, item, collection)
                    print(f"- {formatted_value}")
            elif isinstance(v, FieldStr):
                formatted_value = output_fieldstr(config, v, collection)
                if v.find("\n") > 0:
                    print(f"# {k}")
                    print(formatted_value)
                    print()
                else:
                    print(f"{k}: {formatted_value}")
            elif isinstance(v, FieldNumber):
                formatted_value = f"{v:g}"
                print(f"{k}: {formatted_value}")
            else:
                raise ValueError(f"Unsupported type {type(v)}")


def create_parser() -> argparse.ArgumentParser:
    """Create an argument parser for scard

    Returns:
        ArgumentParser: Argument parser to use
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("card", nargs="*", help="Index of cards to return")
    parser.add_argument(
        "--version",
        action="version",
        version=version_to_output(),
    )
    parser.description = __doc__
    return parser


def entry():
    """Entry point for scard"""
    args = create_parser().parse_args()

    config = load_fs_config()

    collection = get_collection(config)

    output_cards(config, collection, args.card)


if __name__ == "__main__":
    pass

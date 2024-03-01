"""Display any number of scrum cards"""

import argparse
import logging
import re
from scrummd.card import Card
from scrummd.collection import Collection, get_collection
from scrummd.config import ScrumConfig
from scrummd.config_loader import load_fs_config
from scrummd.source_md import CardComponent, FieldStr, StringComponent

logger = logging.getLogger(__name__)

_field_re = re.compile(r"\$(\w+)")


def format_card(config: ScrumConfig, card: Card) -> str:
    """Format a card per the config

    Args:
        config (ScrumConfig): Active scrum configuration
        card (Card): Card to format

    Returns:
        str: Card formatted per configuration
    """
    format = config.scard_reference_format
    output = _field_re.sub(
        lambda m: str(card[m.group(1)]) if m.group(1) in card else "", format
    )
    return output


def output_value(config: ScrumConfig, value: FieldStr, collection: Collection) -> str:
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

    for component in value.components():
        if isinstance(component, StringComponent):
            output += component.value
        elif isinstance(component, CardComponent):
            card = collection.get(component.cardIndex)
            if card:
                output += format_card(config, card)
            else:
                output += f"[[{component.cardIndex}]] (NOT FOUND)"
                logger.warning(
                    f"Card index {component.cardIndex} not found when expanding"
                )
                # Should strict fail here?
        else:
            raise ValueError("Component of invalid type")

    return output


def entry():
    parser = argparse.ArgumentParser()
    parser.add_argument("card", nargs="*", help="Index of cards to return")
    parser.description == __doc__
    args = parser.parse_args()

    config = load_fs_config()

    collection = get_collection(config)

    for card_index in args.card:
        if card_index not in collection:
            logger.error("Card %s not found", card_index)
            continue
        card = collection[card_index]
        print("---")
        print(f"{card_index}: {card['summary']}")
        print("---")
        for k, v in card.items():
            if k == "summary":
                continue
            if k[0] == "_":
                continue
            if v is None:
                continue

            formatted_value = output_value(config, v, collection)
            if isinstance(v, list):
                print(f"- {formatted_value}")
            elif v.find("\n") > 0:
                print(f"# {k}")
                print(formatted_value)
                print()

            else:
                print(f"{k}: {formatted_value}")


if __name__ == "__main__":
    pass

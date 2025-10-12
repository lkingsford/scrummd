"""Display any number of scrum cards"""

import argparse
import logging
from typing import Optional
from scrummd import formatter
from scrummd.card import Card
from scrummd.collection import Collection, get_collection
from scrummd.config import ScrumConfig
from scrummd.config_loader import load_fs_config
from scrummd.version import version_to_output
from scrummd.source_md import (
    Field,
    FieldNumber,
    FieldStr,
)

logger = logging.getLogger(__name__)


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


def output_cards(
    config: ScrumConfig,
    template: str,
    collection: Collection,
    card_indexes: list[str],
):
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
        print(formatter.format(config, template, card, collection))


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
    parser.add_argument(
        "-t", "--template", help="Template file to use", default="default_scard.j2"
    )
    parser.description = __doc__
    return parser


def entry(args=None, config=None):
    """Entry point for scard"""
    args = create_parser().parse_args(args)
    config = config or load_fs_config()
    collection = get_collection(config)

    output_cards(config, args.template, collection, args.card)


if __name__ == "__main__":
    entry()

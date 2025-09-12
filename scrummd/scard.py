"""Display any number of scrum cards"""

import argparse
import logging
import re
from typing import Optional
import jinja2
from scrummd import formatter
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


def format_field(field):
    raise NotImplemented("Unimplemented whilst moving to Jinja")


def output_cards(
    config: ScrumConfig,
    template: jinja2.Template,
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
        assert config.scard.default_template
        print(formatter.format(config.scard.default_template, card, collection))


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


def entry():
    """Entry point for scard"""
    args = create_parser().parse_args()
    config = load_fs_config()
    collection = get_collection(config)
    template = formatter.load_template(args.template, config)

    output_cards(config, template, collection, args.card)


if __name__ == "__main__":
    pass

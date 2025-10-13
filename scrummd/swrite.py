"""Set fields of a card"""

import argparse
import logging
import sys
from pathlib import Path
from scrummd.collection import get_collection
from scrummd.card import from_parsed
from scrummd.config import ScrumConfig
from scrummd.config_loader import load_fs_config
from scrummd.version import version_to_output

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create an argument parser for sprop

    Returns:
        argparse.ArgumentParser: ArgumentParser for sprop
    """
    parser = argparse.ArgumentParser()
    parser.description = __doc__
    parser.add_argument(
        "--version",
        action="version",
        version=version_to_output(),
    )
    parser.add_argument("cards", nargs="+", help="Cards to set property on.")
    parser.add_argument(
        "--set",
        "-s",
        action="append",
        nargs=2,
        metavar=("FIELD", "VALUE"),
        help='Fields to set in the format "field=value".',
    )
    parser.add_argument(
        "--set-stdin", "-i", metavar=("FIELD"), help="Field to set from stdin."
    )
    parser.add_argument(
        "-o",
        action="store_true",
        help="Output to stdout instead of overwriting the card.",
        default=False,
    )

    return parser


import pprint


def entry() -> None:
    """Entry point"""
    parser = create_parser()
    args = parser.parse_args()

    config = load_fs_config()
    collection = get_collection(config)

    if not args.set and not args.set_stdin:
        parser.error("At least one of --set/-s or --set-stdin/-i must be provided.")

    for card in args.cards:
        if card not in collection:
            # All or nothing - if any fail, they all fail. A hint of ACID.
            parser.error(f"Card {card} not found. No changes made.")

    cards = [collection[card] for card in args.cards]

    changes = [(arg[0], arg[1]) for arg in (args.set or [])]

    if args.set_stdin:
        if sys.stdout.isatty():
            # Little thing to just make a users life nicer
            print("Reading into %s from terminal.", file=sys.stderr)
            print(
                "<ctrl+d> (on Linux/Mac) or <ctrl+z> <enter> (on Windows) to close input.",
                file=sys.stderr,
            )
        std_input = sys.stdin.read()

        changes.append((args.set_stdin, std_input.strip()))

    print(changes)

    # Apply all - but again, not actually outputting until we've proven we're all good with
    # everything
    modified_cards = [
        from_parsed(
            config,
            card.parsed_md.apply_modifications(config, changes),
            card.collection_from_path,
            Path(card.path),
        )
        for card in cards
    ]

    print("----new----")

    for card in modified_cards:
        pprint.pprint(card)


if __name__ == "__main__":
    entry()

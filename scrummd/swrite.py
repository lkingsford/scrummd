"""Set fields of a card"""

import argparse
import logging
import sys
from io import StringIO
from typing import Optional
from functools import reduce
from pathlib import Path
from typing import List, TextIO
from scrummd.collection import get_collection
from scrummd.card import from_parsed
from scrummd.exceptions import ModificationError
from scrummd.formatter import format, DEFAULT_MD_TEMPLATE
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
        help="Fields to set.",
    )
    parser.add_argument(
        "--set-stdin", "-i", metavar=("FIELD"), help="Field to set from stdin."
    )
    parser.add_argument(
        "-o",
        "--stdout",
        action="store_true",
        help="Output to stdout instead of overwriting the card.",
        default=False,
    )

    parser.add_argument(
        "--add",
        "-a",
        action="append",
        nargs=2,
        metavar=("FIELD", "VALUE"),
        help="Add values to an existing list in a card.",
    )

    parser.add_argument(
        "--remove",
        "-r",
        action="append",
        nargs=2,
        metavar=("FIELD", "VALUE"),
        help="Remove values (case insensitively) from an existing list in a card.",
    )

    return parser


def entry(
    injected_args: Optional[List[str]] = None,
    config: Optional[ScrumConfig] = None,
    stdin: Optional[StringIO] = None,
    stdout: Optional[StringIO] = None,
) -> None:
    """Entry point"""
    parser = create_parser()
    args = parser.parse_args(injected_args)
    _stdin = stdin or sys.stdin
    _stdout = stdout or sys.stdout

    _config = config or load_fs_config()
    assert _config
    collection = get_collection(_config)

    if not any((args.set, args.set_stdin, args.add, args.remove)):
        parser.error(
            "At least one of --set/-s, --set-stdin/-i, --add/-a or --remove/-r must be provided."
        )

    for card in args.cards:
        if card not in collection:
            # All or nothing - if any fail, they all fail. A hint of ACID.
            parser.error(f"Card {card} not found. No changes made.")

    cards = [collection[card] for card in args.cards]

    set_fields: list[tuple[str, str]] = [(arg[0], arg[1]) for arg in (args.set or [])]
    add_values: list[tuple[str, list[str]]] = [
        (arg[0], [arg[1]]) for arg in (args.add or [])
    ]
    remove_values: list[tuple[str, list[str]]] = [
        (arg[0], [arg[1]]) for arg in (args.remove or [])
    ]

    if args.set_stdin:
        if _stdout.isatty():
            # Little thing to just make a users life nicer
            print("Reading into %s from terminal.", file=sys.stderr)
            print(
                "<ctrl+d> (on Linux/Mac) or <ctrl+z> <enter> (on Windows) to close input.",
                file=sys.stderr,
            )
        std_input = _stdin.read()

        set_fields.append((args.set_stdin, std_input.strip()))

    try:
        # Apply all - but again, not actually outputting until we've proven we're all good with
        # everything
        modified_cards = [
            from_parsed(
                _config,
                reduce(
                    lambda parsed_md, to_remove: parsed_md.remove_from_list(
                        _config, *to_remove
                    ),
                    remove_values,
                    reduce(
                        lambda parsed_md, to_add: parsed_md.add_to_list(
                            _config, *to_add
                        ),
                        add_values,
                        card.parsed_md.set_fields(_config, set_fields),
                    ),
                ),
                card.collection_from_path,
                Path(card.path),
            )
            for card in cards
        ]

        for card in modified_cards:
            formatted = format(_config, DEFAULT_MD_TEMPLATE, card, collection)
            if args.stdout:
                _stdout.writelines(formatted)
            else:
                with open(card.path, "w") as card_file:
                    card_file.write(formatted)

    except ModificationError as e:
        # I know this eats the backtrace and is a less meaningful error, but these particular
        # exceptions are intended for the user (and formatted accordingly).
        logger.error(str(e))


if __name__ == "__main__":
    entry()

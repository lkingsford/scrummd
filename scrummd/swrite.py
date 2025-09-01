"""Set fields of a card"""

import argparse
from scrummd.collection import get_collection
from scrummd.config import ScrumConfig
from scrummd.config_loader import load_fs_config
from scrummd.version import version_to_output


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
    parser.add_argument("cards", nargs="*", help="Cards to set property on")
    parser.add_argument(
        "property", nargs="*", help='Properties to set in the format "property=value"'
    )
    parser.add_argument(
        "-s",
        action="store_true",
        help="Output to stdout instead of overwriting the card",
        default=False,
    )
    return parser


def entry() -> None:
    """Entry point"""
    args = create_parser().parse_args()

    config = load_fs_config()


if __name__ == "__main__":
    entry()

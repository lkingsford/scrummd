"""Display any number of scrum cards"""

import argparse
import logging
from scrummd.collection import get_collection
from scrummd.config_loader import load_fs_config

logger = logging.getLogger(__name__)


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
            if v is None:
                continue

            if v.find("\n") > 0:
                print(f"# {k}")
                print(v)
                print()

            else:
                print(f"{k}: {v}")


if __name__ == "__main__":
    pass

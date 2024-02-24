from argparse import ArgumentError
import os
import pathlib
from typing import Optional, Union
import scrummd.card
import logging
from scrummd.config import ScrumConfig
from scrummd.exceptions import ValidationError

logger = logging.getLogger(__name__)

Collection = dict[str, scrummd.card.Card]


class DuplicateIndexError(ValueError):
    """Called when an index of a card is declared twice in the collection."""

    def __init__(self, index, path):
        self.index = index
        self.path = path
        super().__init__(f"Duplicate index {self.index} found in {self.path}")


def get_collection(
    config: ScrumConfig, collection_name: Optional[str] = None
) -> Collection:
    """Get a collection of cards

    Args:
        config (ScrumConfig): ScrumMD Configuration to use
        collection_name (Optional[str], optional): Collection to return. Defaults to None (being All).

    Raises:
        DuplicateIndexError: A card with an index is found twice

    Returns:
        dict[str, scrummd.card.Card]: A dict with the index of the card, and a card object
    """

    all_cards: dict[str, scrummd.card.Card] = {}
    collection: dict[str, scrummd.card.Card] = {}
    collection_path = pathlib.Path(config.scrum_path)
    for root, _, files in os.walk(collection_path, followlinks=True):
        # So - this'll turn "scrum/backlog/special" into "backlog.special"
        path_parts = pathlib.Path(root).relative_to(collection_path).parts
        collection_from_path = ".".join(path_parts)
        # Ignore any folder starting with .
        if any([folder_name[0] == "." for folder_name in path_parts]):
            continue

        for name in files:
            path = pathlib.Path(root, name)
            if name[0] == ".":
                # Ignore all files that start with .
                continue
            try:
                with open(path, "r") as fo:
                    contents = fo.read()
                    card = scrummd.card.fromStr(
                        config, contents, [collection_from_path]
                    )
                    index = card["index"] or path.name.split(".")[0]
                    if index in all_cards:
                        raise DuplicateIndexError(index, path)
                    card["index"] = index
                    card["_path"] = str(path)
                    all_cards[index] = card

            except scrummd.card.ValidationError as ex:
                if config.strict:
                    logging.error("ValidationError (%s) reading %s", ex, path)
                    raise
                else:
                    logging.warn("ValidationError (%s) reading %s", ex, path)

            except DuplicateIndexError as ex:
                if config.strict:
                    raise
                else:
                    logging.warn("%s ignored", path)

    if not collection_name:
        return all_cards

    for index, card in all_cards.items():
        for _collection in card["_collections"]:
            if _collection == collection_name or _collection.startswith(
                collection_name + "."
            ):
                collection[index] = card

        for collection_subname, _defined_collection in card[
            "_defined_collections"
        ].items():
            current_collection_name = (
                index if collection_subname == "" else f"{index}.{collection_subname}"
            )
            if (
                current_collection_name == collection_name
                or current_collection_name.startswith(collection_name + ".")
            ):
                for card_index in _defined_collection:
                    collection[card_index] = all_cards[card_index]

    return collection


Groups = dict[Optional[str], Union["Groups", list[scrummd.card.Card]]]


def group_collection(
    config: ScrumConfig, collection: Collection, groups: list[str]
) -> Groups:
    """Group collection into (potentially nested) groups by the field in the Card

    Args:
        config (ScrumConfig): Scrum config
        collection (Collection): Collection of cards to group
        groups (list[str]): All the groups that need to be made

    Returns:
        Groups: A dict with the group value, and either more groups or the field value
    """

    cur_group = groups[0].casefold()
    predefined = cur_group in [k.casefold() for k in config.fields.keys()]
    card_groups: Groups = {}
    fields: set[Optional[str]] = set()

    if predefined:
        group = next(
            fields
            for key, fields in config.fields.items()
            if key.casefold() == cur_group
        )
        fields = set([f.casefold() for f in group])
    else:
        for card in collection.values():
            if cur_group in card:
                card_field = card[cur_group]  # type: ignore
                fields.add(card_field.casefold())
    fields.add(None)

    for f in fields:
        if len(groups) == 1:
            card_groups[f] = []
        else:
            card_groups[f] = Groups()

    # This could potentially be squished into the generating the fields so we don't have to pass through all of the cards multiple times
    # But - this is clearer, and don't want to prematurely optimize
    for card in collection.values():
        card_field = card.get(cur_group)  # type: ignore
        if card_field:
            if not isinstance(card_field, str):
                msg = f"{card['index']} can't group by {cur_group}: must be string."
                if config.strict:
                    raise ValidationError(msg)
                else:
                    logger.warn(msg)
                    continue
            else:
                field = card_field.casefold()
        else:
            field = None

        output_collection = card_groups[field]
        assert isinstance(output_collection, list)
        output_collection.append(card)

    if len(groups) == 1:
        return card_groups

from argparse import ArgumentError
from collections import OrderedDict
import os
import pathlib
from typing import Optional, Union
from scrummd.card import Card, fromStr
import logging
from scrummd.config import ScrumConfig
from scrummd.exceptions import ValidationError, DuplicateIndexError

logger = logging.getLogger(__name__)

Collection = dict[str, Card]


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
        dict[str, Card]: A dict with the index of the card, and a card object
    """

    all_cards: dict[str, Card] = {}
    collection: dict[str, Card] = {}
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
                    card = fromStr(config, contents, collection_from_path, path)
                    if card.index in all_cards:
                        raise DuplicateIndexError(card.index, path)
                    all_cards[card.index] = card

            except ValidationError as ex:
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
        for _collection in card.collections:
            if _collection == collection_name or _collection.startswith(
                collection_name + "."
            ):
                collection[index] = card

        for collection_subname, _defined_collection in card.defined_collections.items():
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


Groups = dict[Optional[str], Union["Groups", list[Card]]]


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
    card_groups: Groups = OrderedDict()

    if predefined:
        group = next(
            fields
            for key, fields in config.fields.items()
            if key.casefold() == cur_group
        )
        for f in [f.casefold() for f in group]:
            card_groups[f] = []
    else:
        fields: set[str] = set()
        for card in collection.values():
            card_field = card.get_field(cur_group)
            if isinstance(card_field, str):
                fields.add(card_field.casefold())
        ordered_fields = sorted(fields)
        for f in ordered_fields:
            card_groups[f] = []

    card_groups[None] = []

    # This could potentially be squished into the generating the fields so we don't have to pass through all of the cards multiple times
    # But - this is clearer, and don't want to prematurely optimize
    for card in collection.values():
        card_field = card.get_field(cur_group)
        if card_field:
            if not isinstance(card_field, str):
                msg = f"{card.get_field('index')} can't group by {cur_group}: must be string."
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

    # This is not particularly clear - if there's more groups to embed, recurse.
    return {
        key: group_collection(
            config, {c.index: c for c in group if isinstance(c, Card)}, groups[1:]
        )
        for key, group in card_groups.items()
    }

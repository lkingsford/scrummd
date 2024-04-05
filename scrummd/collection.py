from collections import OrderedDict
from copy import copy
from dataclasses import dataclass
from enum import Enum
import itertools
import os
import pathlib
from typing import Optional
from scrummd.card import Card, from_str
import logging
from scrummd.config import ScrumConfig
from scrummd.exceptions import ValidationError, DuplicateIndexError
from scrummd.source_md import Field, FieldNumber, FieldStr, typed_field

logger = logging.getLogger(__name__)


Collection = OrderedDict[str | Field, Card]


# Weird use of tuple here - but we need to be able to distinguish whether it's
# a "Groups" or "Collection"
@dataclass
class Group:
    groups: "Groups"
    collection: Collection


Groups = OrderedDict[Optional[str | Field], Group]


@dataclass
class Filter:
    """Filter for filtering through a collection"""

    class FilterMode(Enum):
        """Types of filter"""

        EQUALS = 1

    field: str
    """Field that is being tested"""

    values: str | list[str]
    """Potential values for the field"""

    mode: FilterMode = FilterMode.EQUALS
    """Mode that the filter is in"""

    def apply(self, collection: Collection) -> Collection:
        """Apply this filter to a collection

        Args:
            collection (Collection): Collection to apply the filter to

        Returns:
            Collection: The filtered collection
        """
        if isinstance(self.values, list):
            values = [value.strip().lower() for value in self.values]
        else:
            values = [str(self.values).strip().lower()]

        return OrderedDict(
            [
                (card_index, card)
                for card_index, card in collection.items()
                if not isinstance(card.get_field(self.field), list)
                and str(card.get_field(self.field)).strip().lower() in values
            ]
        )


@dataclass
class SortCriteria:
    """Fields and order to sort by"""

    key: str
    """Field name to sort by"""

    reversed: bool
    """Reverse the order of the collection"""


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

    all_cards = Collection()

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
                    card = from_str(config, contents, collection_from_path, path)
                    if card.index in all_cards:
                        raise DuplicateIndexError(card.index, path)
                    all_cards[card.index] = card

            except ValidationError as ex:
                if config.strict:
                    logging.error("ValidationError (%s) reading %s", ex, path)
                    raise
                else:
                    logging.warning("ValidationError (%s) reading %s", ex, path)

            except DuplicateIndexError as ex:
                if config.strict:
                    raise
                else:
                    logging.warning("%s ignored", path)

    collections: dict[str, Collection] = {}

    # Get all the cards in each collection per implicit collection from folder
    # and collections listed in the card
    for index, card in all_cards.items():
        for _collection in card.collections:
            # The partial name stuff here is because if a card is in
            # 'collection.subcollection', it's also in 'collection' implicitly
            # - accumulate with that lambda means that for A.B.C, it adds it to
            # A, then A.B, then A.B.C
            for partial_name in itertools.accumulate(
                _collection.split("."), lambda i, j: f"{i}.{j}"
            ):
                if partial_name in collections:
                    collections[partial_name][index] = card
                else:
                    collections[partial_name] = Collection({index: card})

    # Get all the collections defined in a card in the fields. Again - needs to
    # add to parent collections too.
    # Holy horizontal ladder, Batman!
    for all_card_index, card in all_cards.items():
        assert isinstance(all_card_index, str)
        for defined_name, defined_collection in card.defined_collections.items():
            for referenced_card_index in defined_collection:
                if referenced_card_index not in all_cards:
                    # Card not found
                    continue

                if defined_name in collections:
                    collections[defined_name][referenced_card_index] = all_cards[
                        referenced_card_index
                    ]
                else:
                    collections[defined_name] = Collection(
                        {referenced_card_index: all_cards[referenced_card_index]}
                    )
                if all_card_index in collections:
                    collections[all_card_index][referenced_card_index] = all_cards[
                        referenced_card_index
                    ]
                else:
                    collections[all_card_index] = Collection(
                        {referenced_card_index: all_cards[referenced_card_index]}
                    )

    # Validate that all cards in a collection are valid per its rules in config
    for _collection_name, collection in collections.items():
        collection_config = config.collections.get(_collection_name)
        if not collection_config:
            continue
        for _, card in collection.items():
            try:
                card.assert_valid_rules(collection_config)
            except ValidationError as ex:
                if config.strict:
                    logging.error("ValidationError (%s) reading %s", ex, path)
                    raise
                else:
                    logging.warn("ValidationError (%s) reading %s", ex, path)

    if not collection_name:
        return Collection(all_cards)

    return collections.get(collection_name) or Collection({})


def _sort_key(field: Field | str | None) -> tuple[float, str]:
    """
    Sort by None, then Numerical order, then Strings

    Args:
        field (Field): Field to sort

    Raises:
        TypeError: There was a field that wasn't an expected type

    Returns:
        tuple[float, str]: A tuple suitable for sorting by
    """
    if field is None:
        return (float("-inf"), "")
    elif isinstance(field, FieldNumber):
        return (field, "")
    elif isinstance(field, FieldStr) or isinstance(field, str):
        return (float("inf"), field)
    else:
        raise TypeError("%s is not an available type", type(field))


def group_collection(
    config: ScrumConfig,
    collection: Collection,
    groups: list[str],
    sort_criteria: list[SortCriteria] = [],
) -> Groups:
    """Group collection into (potentially nested) groups by the field in the Card, sorted if
    required

    Args:
        config (ScrumConfig): Scrum config
        collection (Collection): Collection of cards to group
        groups (list[str]): All the groups that need to be made
        sort_criteria (list[SortCriteria]): Criteria to sort the groups and cards by

    Returns:
        Groups: A dict with the group value, and either more groups or the field value
    """

    # Why are we sorting here? It means we don't need to store the grouping fields to sort them
    # later. This may change

    cur_group = groups[0].casefold()
    predefined = cur_group in [k.casefold() for k in config.fields.keys()]
    card_groups: Groups = Groups()

    if predefined:
        group = next(
            fields
            for key, fields in config.fields.items()
            if key.casefold() == cur_group
        )
        for predefined_field in [typed_field(f.casefold()) for f in group]:
            card_groups[predefined_field] = Group(Groups(), Collection())
    else:
        fields: set[Optional[Field]] = set()
        for card in collection.values():
            card_field = card.get_field(cur_group)
            if isinstance(card_field, str):
                fields.add(typed_field(card_field.casefold()))
            else:
                fields.add(card_field)
        ordered_fields = sorted(fields, key=_sort_key)
        for ordered_field in ordered_fields:
            card_groups[ordered_field] = Group(Groups(), Collection())

    card_groups[None] = Group(Groups(), Collection())

    # This chunk here sorts the group headings themselves, if there is a sort
    # for them
    matching_sort = [
        criteria for criteria in sort_criteria if criteria.key.casefold() == cur_group
    ]
    if matching_sort:
        # sort by matching_sort[0]
        sorted_card_groups_result = sorted(
            card_groups.items(),
            key=lambda k: _sort_key(k[0]),
            reverse=matching_sort[0].reversed,
        )
        sorted_card_groups = OrderedDict(sorted_card_groups_result)
    else:
        sorted_card_groups = card_groups

    # The FieldStr/FieldNumber was supposed to make this more readable, but I
    # really have more reflection here than I'd prefer
    for card in collection.values():
        card_field = card.get_field(cur_group)
        if card_field:
            if isinstance(card_field, FieldStr):
                output_collection = sorted_card_groups[
                    FieldStr(card_field.casefold())
                ].collection
            elif isinstance(card_field, FieldNumber):
                output_collection = sorted_card_groups[card_field].collection
            else:
                msg = f"{card.get_field('index')} can't group by {cur_group}: must be string or number."
                if config.strict:
                    raise ValidationError(msg)
                else:
                    logger.warn(msg)
                    continue
        else:
            output_collection = sorted_card_groups[None].collection

        assert output_collection is not None
        output_collection[card.index] = card

    for group_key, group_value in sorted_card_groups.items():
        sorted_output_collection = sort_collection(
            group_value.collection, sort_criteria
        )
        sorted_card_groups[group_key].collection = sorted_output_collection

    if len(groups) == 1:
        return sorted_card_groups

    # This is not particularly clear - if there's more groups to embed, recurse.
    embedded_groups = [
        (
            key,
            Group(
                group_collection(
                    config,
                    Collection({c.index: c for c in group.collection.values()}),
                    groups[1:],
                ),
                Collection(),
            ),
        )
        for key, group in card_groups.items()
    ]
    return Groups(embedded_groups)


def filter_collection(collection: Collection, filters: list[Filter]) -> Collection:
    """Apply all filters to a collection

    Args:
        collection (Collection): Collection to apply filters to.
        filters (list[Filter]): Filters to apply. All filters are applied.

    Returns:
        Collection: Filtered collection of cards.
    """
    working_collection = copy(collection)
    for f in filters:
        working_collection = f.apply(working_collection)
    return working_collection


def sort_collection(collection: Collection, criteria: list[SortCriteria]) -> Collection:
    """Sort a collection of cards by the sort criteria

    Args:
        collection (Collection): Collection to sort
        criteria (list[SortCriteria]): Criteria to sort by

    Returns:
        SortedCollection: Sorted collection of cards
    """

    # Yet more recursion. We can't just use `sorted` with multiple tuples joined
    # together because some criteria might be reversed
    # The 'O's with the loop are bigger than I'd prefer, but practically, I'm
    # seeing ~0.04-0.05s with `sbench` sorting 10000 cards by 2 criteria - so
    # not _really_ wanting to prematurely optimize it yet.

    if len(criteria) == 0:
        return OrderedDict(collection)

    sorted_by_criteria = sorted(
        collection.items(),
        key=lambda k: _sort_key(k[1].get_field(criteria[0].key)),
        reverse=criteria[0].reversed,
    )
    if len(criteria) > 1:
        output_collection = Collection()
        grouped = itertools.groupby(
            sorted_by_criteria, key=lambda k: _sort_key(k[1].get_field(criteria[0].key))
        )
        for _, group in grouped:
            subcollection = Collection(group)
            sorted_subcollection = sort_collection(subcollection, criteria[1:])
            for index, card in sorted_subcollection.items():
                output_collection[FieldStr(index)] = card
        return output_collection
    else:
        return OrderedDict(sorted_by_criteria)

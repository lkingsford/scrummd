"""Tests for `collection.py`"""

from copy import copy
import os
import pytest
from pathlib import Path

from scrummd.config import ScrumConfig
from scrummd.collection import (
    Filter,
    SortCriteria,
    get_collection,
    group_collection,
    filter_collection,
    sort_collection,
)
from fixtures import data_config
from scrummd.exceptions import RuleViolationError


# NOTE: These almost all retrieve the same set of data. We might want to think
# about ways we can restructure this to see more useful fail cases if something
# was to go wrong.


def test_get_basic_collection(data_config):
    """Test that all the cards in a basic collection are returned"""
    test_collection = get_collection(data_config, "collection1")

    indices = test_collection.keys()
    assert sorted(indices) == ["c1", "c2", "c3", "e1"]


def test_get_basic_subcollection(data_config):
    """Test that all the cards in a collection inside another collection are returned"""
    test_collection = get_collection(data_config, "collection1.embedded")

    indices = test_collection.keys()
    assert list(indices) == ["e1"]


def test_get_collection_with_tags_and_folder(data_config):
    """Test that all the cards in a collection of both folder and tags are returned

    Includes some tags with both property and header styles
    """

    test_collection = get_collection(data_config, "collection2")
    indices = test_collection.keys()
    assert sorted(indices) == ["c2", "c3", "c4", "c5", "c6"]


def test_get_collection_with_tags(data_config):
    """Test that all the cards in a collection of just tags are returned

    Includes some tags with both property and header styles, and both 'tags' and 'collections'
    """

    test_collection = get_collection(data_config, "special")
    indices = test_collection.keys()
    assert sorted(indices) == ["c4", "c5", "c6"]


def test_ignore_dot_folders(data_config):
    """Test that any paths or cards under folders starting with . are completely ignored"""
    test_collection = get_collection(data_config, "collection2")
    indices = test_collection.keys()
    # If i1 is in, then folders aren't ignored
    assert "i1" not in indices
    # If i2 is in, then not dot folders aren't dot folders aren't ignored
    assert "i2" not in indices


@pytest.mark.parametrize(
    ["collection_name", "expected_items"],
    [
        ["collection3", set(["c1", "c2", "c4", "c5"])],
        ["collection3.key", set(["c5"])],
        ["collection3.special", set(["c1", "c4"])],
    ],
    ids=["Add to root (Items)", "Single item in param", "Subcollection"],
)
def test_reference_collection(data_config, collection_name, expected_items):
    """Test that items"""
    test_collection = get_collection(data_config, collection_name)
    indices = test_collection.keys()
    assert set(indices) == expected_items


def test_index_set(data_config):
    """Test that the index value of the card is set from filename where it's
    not set in the fields of the card itself"""
    test_collection = get_collection(data_config)
    assert test_collection["c1"].index == "c1"


def test_path_set(data_config):
    """Test that the _path is set of cards to the relative path of the card"""
    test_collection = get_collection(data_config)
    assert test_collection["c1"].path == "test/data/collection1/c1.md"
    assert test_collection["e1"].path == "test/data/collection1/embedded/e1.md"


def test_group_collection_defined_fields(data_config):
    """Test that grouping when a field is defined by config returns correct groups"""
    test_collection = get_collection(data_config, "collection1")
    grouped = group_collection(data_config, test_collection, ["status"])
    assert set((card.index for card in grouped["ready"].collection.values())) == set(
        ["c1", "c2", "e1"]
    )
    assert set((card.index for card in grouped["done"].collection.values())) == set(
        ["c3"]
    )


def test_group_collection_undefined_fields(data_config):
    """Test that grouping when a field is defined by config returns correct groups"""
    test_collection = get_collection(data_config, "collection1")
    grouped = group_collection(data_config, test_collection, ["assignee"])
    assert set((card.index for card in grouped["bob"].collection.values())) == set(
        ["c1", "c3"]
    )
    assert set((card.index for card in grouped["mary"].collection.values())) == set(
        ["c2"]
    )


def test_multiple_groupbys(data_config):
    """Test that grouping when there are two fields is correct"""
    test_collection = get_collection(data_config, "collection1")
    grouped = group_collection(data_config, test_collection, ["status", "assignee"])
    assert set(
        (card.index for card in grouped["ready"].groups["bob"].collection.values())
    ) == set(["c1"])
    assert set(
        (card.index for card in grouped["ready"].groups["mary"].collection.values())
    ) == set(["c2"])
    assert set(
        (card.index for card in grouped["done"].groups["bob"].collection.values())
    ) == set(["c3"])


def test_collection_with_rules(data_config):
    """Test that a card with valid collection-level rules is added"""
    collection4 = get_collection(data_config, "collection4").values()
    assert set((card.index for card in collection4)) == set(["c7"])


def test_collection_with_invalid_collection_rules(data_config):
    """Test that a card violating collection rules raises an error"""
    config = copy(data_config)
    config.scrum_path = "test/fail_cases/collection_rule_violation"
    with pytest.raises(RuleViolationError):
        get_collection(config, "collection4")


def test_path_correctly_set(data_config):
    """Test that the path for a card is as expected"""
    test_collection = get_collection(data_config, "collection1")
    assert Path(test_collection["c1"].path) == Path("test/data/collection1/c1.md")
    assert Path(test_collection["e1"].path) == Path(
        "test/data/collection1/embedded/e1.md"
    )


def test_get_collection_maintains_listed_order(data_config):
    """Test that where a collection is formed from references in a file, that
    the order of the cards is maintained when that collection is 'got'"""
    test_collection = get_collection(data_config, "sort_collection")
    assert list(test_collection.keys()) == ["c6", "c2", "c3", "c4", "c5", "c1"]


@pytest.mark.parametrize(
    ["filters", "expected_card_ids"],
    [
        [[Filter("assignee", "Bob")], ["c1", "c3"]],
        [[Filter("assignee", ["Bob", "Mary"])], ["c1", "c2", "c3", "c5", "c6"]],
        [[Filter("assignee", "bob")], ["c1", "c3"]],
        [[Filter("assignee", "bob"), Filter("status", "ready")], ["c1"]],
        [[Filter("assignee", " bob"), Filter("status", "ready")], ["c1"]],
    ],
    ids=[
        "1 field",
        "1 field, 2 values",
        "Check for case insensitivity",
        "Multiple conditions",
        "Strip whitespace",
    ],
)
def test_filtering(data_config, filters, expected_card_ids):
    """Test that filters are correctly applied"""
    test_collection = get_collection(data_config)
    result = filter_collection(test_collection, filters).keys()
    assert set(result) == set(expected_card_ids)


@pytest.mark.parametrize(
    ["field", "expected_card_order"],
    [["Estimate", ["c6", "c4", "c5"]]],
    ids=["Sort by number field"],
)
def test_sorting(data_config, field, expected_card_order):
    pass


def test_group_sorting(data_config):
    """Test that groups are in the order specified by sort"""
    test_collection = get_collection(data_config, "collection1")
    grouped_collection = group_collection(
        data_config, test_collection, ["assignee"], [SortCriteria("assignee", False)]
    )
    assert list(grouped_collection.keys()) == [None, "aleph", "bob", "mary"]


def test_group_reverse_sorting(data_config):
    """Test that groups are in the order specified by sort when sort is reversed"""
    test_collection = get_collection(data_config, "collection1")
    grouped_collection = group_collection(
        data_config, test_collection, ["assignee"], [SortCriteria("assignee", True)]
    )
    assert list(grouped_collection.keys()) == ["mary", "bob", "aleph", None]


def test_sorting_collection_with_numbers(data_config):
    """Test that an ungrouped collection of cards is sorted by criteria including numbers in the values"""
    # SBL output for the collection:
    # index, assignee, estimate
    # c3, Bob,
    # c2, Mary, 2.5
    # c1, Bob, 5
    # e1, Aleph, Unknown
    test_collection = get_collection(data_config, "collection1")
    sorted_collection = sort_collection(
        test_collection, [SortCriteria("estimate", False)]
    )
    assert list(sorted_collection.keys()) == ["c3", "c2", "c1", "e1"]


def test_sorting_collection_multiple_criteria(data_config):
    """Test that sorting with multiple sort criteria. without grouping, applies
    them correctly"""
    test_collection = get_collection(data_config, "sort_collection")
    sorted_collection = sort_collection(
        test_collection,
        [SortCriteria("assignee", False), SortCriteria("estimate", True)],
    )
    # SBL output for the collection:
    # index, assignee, estimate
    # c1, Bob, 5
    # c2, Mary, 2.5
    # c3, Bob,
    # c4, Aleph, Unknown
    # c5, Mary, 1
    # c6, Mary, Unknown
    assert list(sorted_collection.keys()) == ["c4", "c1", "c3", "c6", "c2", "c5"]


def test_sorting_inside_group(data_config):
    """Test that the inner parts of groups are sorted correctly"""
    test_collection = get_collection(data_config, "sort_collection")
    grouped_sorted_collection = group_collection(
        data_config, test_collection, ["Assignee"], [SortCriteria("estimate", False)]
    )
    assert list(grouped_sorted_collection["mary"].collection.keys()) == [
        "c5",
        "c2",
        "c6",
    ]

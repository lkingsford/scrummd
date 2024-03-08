import os
import pytest

from scrummd.config import ScrumConfig
from scrummd.collection import get_collection, group_collection
from fixtures import data_config


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
    assert set((card.index for card in grouped["ready"])) == set(["c1", "c2", "e1"])
    assert set((card.index for card in grouped["done"])) == set(["c3"])


def test_group_collection_undefined_fields(data_config):
    """Test that grouping when a field is defined by config returns correct groups"""
    test_collection = get_collection(data_config, "collection1")
    grouped = group_collection(data_config, test_collection, ["assignee"])
    assert set((card.index for card in grouped["bob"])) == set(["c1", "c3"])
    assert set((card.index for card in grouped["mary"])) == set(["c2"])


def test_multiple_groupbys(data_config):
    """Test that grouping when there are two fields is correct"""
    test_collection = get_collection(data_config, "collection1")
    grouped = group_collection(data_config, test_collection, ["status", "assignee"])
    assert set((card.index for card in grouped["ready"]["bob"])) == set(["c1"])
    assert set((card.index for card in grouped["ready"]["mary"])) == set(["c2"])
    assert set((card.index for card in grouped["done"]["bob"])) == set(["c3"])

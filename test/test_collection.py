import pytest

from scrummd.config import ScrumConfig
from scrummd.collection import get_collection


@pytest.fixture(scope="session")
def data_config() -> ScrumConfig:
    return ScrumConfig(scrum_path="test/data")


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

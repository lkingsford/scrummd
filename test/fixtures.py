import copy
import pytest
from scrummd import collection

from scrummd.config import CollectionConfig, ScrumConfig

DATA_CONFIG = ScrumConfig(
    strict=True,
    scrum_path="test/data",
    fields={"status": ["Ready", "Done"]},
    collections={
        "collection4": CollectionConfig(
            required=["assignee"], fields={"status": ["ready"]}
        )
    },
)


@pytest.fixture(scope="session")
def data_config() -> ScrumConfig:
    """Data config with common parameters for tests"""
    return copy.deepcopy(DATA_CONFIG)


@pytest.fixture(scope="session")
def test_collection(data_config) -> collection.Collection:
    """Full collection of cards from test"""
    return collection.get_collection(data_config)


TEST_COLLECTION_KEYS = collection.get_collection(DATA_CONFIG)
"""
This is here (and separate to test_collection) to allow parameterization
on test_collection.
"""

IMPLICIT_SUMMARY_CONFIG = copy.deepcopy(DATA_CONFIG)
IMPLICIT_SUMMARY_CONFIG.allow_header_summary = True
IMPLICIT_SUMMARY_CONFIG.scrum_path = "test/special_cases/header_summary"


@pytest.fixture(scope="session")
def implicit_summary_collection() -> collection.Collection:
    """Collection of cards with the header/implicit summary used."""
    return collection.get_collection(IMPLICIT_SUMMARY_CONFIG)


IMPLICIT_SUMMARY_KEYS = collection.get_collection(IMPLICIT_SUMMARY_CONFIG)

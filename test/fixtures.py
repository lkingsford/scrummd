import pytest
from scrummd import collection

from scrummd.config import ScrumConfig


@pytest.fixture(scope="session")
def data_config() -> ScrumConfig:
    """Data config with common parameters for tests"""
    return ScrumConfig(
        strict=True,
        scrum_path="test/data",
        fields={"status": ["Ready", "Done"]},
        collections={
            "collection4": {"required": ["assignee"], "fields": {"status": ["ready"]}}
        },
    )


@pytest.fixture(scope="session")
def test_collection(data_config) -> collection.Collection:
    """Full collection of cards from test"""
    return collection.get_collection(data_config)

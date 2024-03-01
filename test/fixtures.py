import pytest
from scrummd import collection

from scrummd.config import ScrumConfig


@pytest.fixture(scope="session")
def data_config() -> ScrumConfig:
    """Data config with common parameters for tests"""
    return ScrumConfig(
        scrum_path="test/data",
        fields={"Status": ["Ready", "Done"]},
    )


@pytest.fixture(scope="session")
def test_collection(data_config) -> collection.Collection:
    """Full collection of cards from test"""
    return collection.get_collection(data_config)

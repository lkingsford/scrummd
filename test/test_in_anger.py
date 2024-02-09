"""Tests using the scrum workspace for scrummd itself"""

import pytest
from scrummd.collection import get_collection

from scrummd.config import ScrumConfig


@pytest.fixture(scope="session")
def scrumcli_config() -> ScrumConfig:
    # TODO: Read the actual config
    return ScrumConfig(scrum_path="scrum")


def test_get_backlog(scrumcli_config):
    """Gets the backlog from the scrummd project"""
    backlog = get_collection(scrumcli_config, "backlog")
    assert len(backlog) > 0

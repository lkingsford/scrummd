"""Tests using the scrum workspace for scrumcli itself"""

import pytest
from scrumcli.collection import get_collection

from scrumcli.config import ScrumConfig


@pytest.fixture(scope="session")
def scrumcli_config() -> ScrumConfig:
    # TODO: Read the actual config
    return ScrumConfig(scrum_path="scrum")


def test_get_backlog(scrumcli_config):
    """Gets the backlog from the scrumcli project"""
    backlog = get_collection(scrumcli_config, "backlog")
    assert len(backlog) > 0

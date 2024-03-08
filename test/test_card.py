from pathlib import Path
import pytest
from scrummd.config import ScrumConfig
from scrummd.exceptions import InvalidRestrictedFieldValueError
import scrummd.card


@pytest.fixture(scope="session")
def data_config() -> ScrumConfig:
    return ScrumConfig(fields={"key": ["valid", "valid2"]})


def test_valid_restricted_field(data_config):
    """Test that a field with a limited permitted set of values is correctly set"""
    valid_card = """
---
summary: valid
key: valid
---
"""
    card = scrummd.card.fromStr(
        data_config, valid_card, "collection", Path("collection/card.md")
    )
    assert card.get_field("key") == "valid"


def test_invalid_restricted_field(data_config):
    """Test that a field with a limited permitted set of values raises an exception when an invalid value is set"""
    invalid_card = """
---
summary: valid
key: invalid
---
"""
    with pytest.raises(InvalidRestrictedFieldValueError):
        card = scrummd.card.fromStr(
            data_config, invalid_card, "collection", Path("collection/card.md")
        )

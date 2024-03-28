from copy import copy
from pathlib import Path
import pytest
from scrummd.config import ScrumConfig
from scrummd.exceptions import (
    InvalidRestrictedFieldValueError,
    RequiredFieldNotPresentError,
)

import scrummd.card
from scrummd.source_md import FieldNumber


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
    card = scrummd.card.from_str(
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
        card = scrummd.card.from_str(
            data_config, invalid_card, "collection", Path("collection/card.md")
        )


def test_required_present(data_config):
    """Test that a collection with a required field by config that's present works"""
    valid_card = """
---
summary: valid
required: present
---
"""
    config = copy(data_config)
    config.required = ["required"]
    scrummd.card.from_str(config, valid_card, "collection", Path("collection/1.md"))
    # Here means test passed


def test_required_missing(data_config):
    """Test that a collection with a required field by config that's not present fails"""
    invalid_card = """
---
summary: valid
---
"""
    config = copy(data_config)
    config.scrum_path = "test/fail_cases/no_status/"
    config.required = ["required"]
    with pytest.raises(RequiredFieldNotPresentError):
        scrummd.card.from_str(
            config, invalid_card, "collection", Path("collection/1md")
        )


def test_integer_field(data_config):
    """Test that a field with an integer value has a number type"""
    card_str = """
---
summary: int card
estimate: 5
---
"""
    card = scrummd.card.from_str(
        data_config, card_str, "collection", Path("collection/int.md")
    )
    assert card.udf["estimate"] == FieldNumber(5)


def test_float_field(data_config):
    """Test that a field with an integer value has a number type"""
    card_str = """
---
summary: int card
estimate: 4.2
---
"""
    card = scrummd.card.from_str(
        data_config, card_str, "collection", Path("collection/float.md")
    )
    assert card.udf["estimate"] == FieldNumber(4.2)

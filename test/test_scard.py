from copy import copy
from pathlib import Path
from scrummd.card import Card, from_str
from scrummd.scard import output_value, format_card
from fixtures import data_config, test_collection
import pytest


@pytest.fixture(scope="function")
def test_card(data_config) -> Card:
    test_card = """
---
summary: Test Card
key: Field [[c1]]
key 2: [[c2]][[c3]]
---
"""
    card = from_str(data_config, test_card, "collection", Path("collection/card.md"))
    return card


def test_output_value(data_config, test_card, test_collection):
    config = copy(data_config)
    config.scard_reference_format = "[$index $assignee $status]"
    assert (
        output_value(config, test_card.get_field("key"), test_collection)
        == "Field [c1 Bob Ready]"
    )
    assert (
        output_value(config, test_card.get_field("key 2"), test_collection)
        == "[c2 Mary ready][c3 Bob Done]"
    )


@pytest.fixture()
def sample_card(data_config):
    return Card(
        index="i",
        summary="1",
        collections=[],
        defined_collections=[],
        path="test/i.md",
        udf={"assignee": "me"},
        _config=data_config,
    )


@pytest.mark.parametrize(
    ["input_format", "expected"],
    [
        ["$index", "i"],
        ["$index $assignee", "i me"],
        ["[$index] $assignee", "[i] me"],
    ],
)
def test_format_card(data_config, sample_card, input_format, expected):
    config = copy(data_config)
    config.scard_reference_format = input_format
    assert format_card(config, sample_card) == expected

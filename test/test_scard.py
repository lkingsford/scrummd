from copy import copy
from scrummd.card import Card, fromStr
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
    card = fromStr(data_config, test_card)
    return card


def test_output_value(data_config, test_card, test_collection):
    config = copy(data_config)
    config.scard_reference_format = "[$index $assignee $status]"
    assert (
        output_value(config, test_card["key"], test_collection)
        == "Field [c1 Bob Ready]"
    )
    assert (
        output_value(config, test_card["key 2"], test_collection)
        == "[c2 Mary ready][c3 Bob Done]"
    )


@pytest.mark.parametrize(
    ["input_format", "input_card", "expected"],
    [
        ["$index", {"index": "i"}, "i"],
        ["$index $assignee", {"index": "i", "assignee": "me"}, "i me"],
        ["[$index] $assignee", {"index": "i", "assignee": "me"}, "[i] me"],
    ],
)
def test_format_card(data_config, input_format, input_card, expected):
    config = copy(data_config)
    config.scard_reference_format = input_format
    assert format_card(config, input_card) == expected

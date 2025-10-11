"""
These are all tests that format a card with the default_md, and verify the fields read back the same
way.
"""

import pathlib
import pytest
from typing import Tuple

import scrummd.collection
import scrummd.card
import scrummd.formatter

from fixtures import (
    data_config,
    TEST_COLLECTION_KEYS,
    test_collection,
    IMPLICIT_SUMMARY_CONFIG,
    IMPLICIT_SUMMARY_KEYS,
    implicit_summary_collection,
)


def reread_card(
    card_key, test_collection, config
) -> Tuple[scrummd.card.Card, scrummd.card.Card]:
    """Utility function for the test_default_md* tests"""
    card: scrummd.card.Card = test_collection.get(card_key)
    formatted_as_md = scrummd.formatter.format(
        config, "default_md.j2", card, test_collection
    )
    reread = scrummd.card.from_str(
        config, formatted_as_md, card.collections[0], pathlib.Path(card.path)
    )
    return card, reread


def assert_meta_correct(card: scrummd.card.Card, reread: scrummd.card.Card):
    """
    Test that the meta of the two cards matches
    """
    assert card.parsed_md.order() == reread.parsed_md.order()
    for field in card.parsed_md.order():
        assert (
            card.parsed_md.meta(field).header_level
            == reread.parsed_md.meta(field).header_level
        )
        assert (
            card.parsed_md.meta(field).md_type == reread.parsed_md.meta(field).md_type
        )
        assert (
            card.parsed_md.meta(field).raw_field_name
            == reread.parsed_md.meta(field).raw_field_name
        )


@pytest.mark.parametrize("card_key", TEST_COLLECTION_KEYS)
def test_default_md_meta(card_key: str, test_collection, data_config):
    """
    Test that the meta writes/reads correctly.
    """

    card, reread = reread_card(card_key, test_collection, data_config)
    assert_meta_correct(card, reread)


FIELDS_TO_VERIFY = [
    "udf",
    "summary",
    "index",
]


@pytest.mark.parametrize("field", FIELDS_TO_VERIFY)
@pytest.mark.parametrize("card_key", TEST_COLLECTION_KEYS)
def test_default_md_fields(card_key: str, field: str, test_collection, data_config):
    """
    Test that various fields write/read correctly.
    """

    card, reread = reread_card(card_key, test_collection, data_config)

    assert card.__dict__[field] == reread.__dict__[field]


@pytest.mark.parametrize("card_key", IMPLICIT_SUMMARY_KEYS)
def test_default_md_implicit_summary(card_key: str, implicit_summary_collection):
    """
    Test that cards with implicit summaries write/read correctly.
    """

    card, reread = reread_card(
        card_key, implicit_summary_collection, IMPLICIT_SUMMARY_CONFIG
    )

    # Verify key values
    assert card.summary == reread.summary
    assert card.udf == reread.udf
    assert card.index == reread.index

    # Verify meta
    assert_meta_correct(card, reread)

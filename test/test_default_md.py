import pathlib
import pytest

import scrummd.collection
import scrummd.card
import scrummd.formatter

from fixtures import data_config, TEST_COLLECTION_KEYS, test_collection


@pytest.mark.parametrize("card_key", TEST_COLLECTION_KEYS)
def test_read_format_read_md(card_key: str, test_collection, data_config):
    """
    So - we read our test card, format it as an md, read it again, then check that it has the same
    metadata, fields and values.
    """
    card: scrummd.card.Card = test_collection.get(card_key)
    formatted_as_md = scrummd.formatter.format(
        data_config, "default_md.j2", card, test_collection
    )
    reread = scrummd.card.from_str(
        data_config, formatted_as_md, card.collections[0], pathlib.Path(card.path)
    )

    assert card.udf == reread.udf
    assert card.summary == reread.summary
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

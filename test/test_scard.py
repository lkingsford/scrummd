import pytest
from fixtures import data_config, TEST_COLLECTION_KEYS, test_collection
from scrummd.scard import format_field, entry
from scrummd.source_md import Field, FieldNumber, FieldStr


@pytest.mark.parametrize(
    ["input_data", "expected"],
    [
        [FieldStr("abc"), "abc"],
        [FieldNumber(123), "123"],
        [FieldNumber(123.0), "123"],
        [FieldNumber(123.1), "123.1"],
        [[FieldStr("a"), FieldStr("b"), FieldStr("3")], "[a, b, 3]"],
    ],
)
def test_format_field(input_data: Field | list[FieldStr], expected: str):
    """Test that formatting a field produces the expected output"""
    assert format_field(input_data) == expected


@pytest.mark.parametrize("card_key", TEST_COLLECTION_KEYS)
def test_scard_end_to_end(card_key: str, test_collection, data_config):
    """Basic 'run with default settings on everything' integration test"""
    # No assertions, because no crash is sufficient
    entry(["scard", card_key], data_config)

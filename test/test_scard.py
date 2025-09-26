from scrummd.scard import format_field
from scrummd.source_md import Field, FieldNumber, FieldStr
import pytest


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

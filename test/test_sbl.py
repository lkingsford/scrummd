import pytest
from scrummd.collection import Filter
import scrummd.sbl


@pytest.mark.parametrize(
    ["argument_value", "expected_filter"],
    [
        [
            "a=b",
            Filter("a", ["b"], mode=Filter.FilterMode.EQUALS),
        ],
        [
            "a= b",
            Filter("a", ["b"], mode=Filter.FilterMode.EQUALS),
        ],
        [
            "a=b, c",
            Filter("a", ["b", "c"], mode=Filter.FilterMode.EQUALS),
        ],
        [
            "a= b, c",
            Filter("a", ["b", "c"], mode=Filter.FilterMode.EQUALS),
        ],
        [
            "a = b, c",
            Filter("a", ["b", "c"], mode=Filter.FilterMode.EQUALS),
        ],
        [
            "a 1=b, c",
            Filter("a 1", ["b", "c"], mode=Filter.FilterMode.EQUALS),
        ],
        [
            "a= b 2, c",
            Filter("a", ["b 2", "c"], mode=Filter.FilterMode.EQUALS),
        ],
    ],
)
def test_include_to_filter(argument_value, expected_filter):
    assert scrummd.sbl.include_to_filter(argument_value) == expected_filter

import os
import pytest
import scrummd.md as md

# Should these be one fixture?


@pytest.fixture(scope="function")
def md1_fo() -> str:
    fo = open("test/data/md1.md")
    yield fo
    fo.close()


@pytest.fixture(scope="function")
def c4_md() -> str:
    fo = open("test/data/collection2/c4.md")
    yield fo
    fo.close()


@pytest.fixture(scope="function")
def c5_md() -> str:
    fo = open("test/data/collection2/c5.md")
    yield fo
    fo.close()


def test_extract_property(md1_fo):
    """Test extracting property variables from an md file"""
    results = md.extract_fields(md1_fo.read())
    assert results["summary"] == "Summary of card"
    assert results["status"] == "Status of card"


def test_extract_header(md1_fo):
    """Test extracting header style variables from an md file"""
    results = md.extract_fields(md1_fo.read())
    assert (
        results["description"].strip()
        == """Multi line description

here"""
    )


@pytest.mark.parametrize(
    ["expected", "result"],
    [
        ["# Header", "header"],
        ["## Header 2", "header 2"],
        ["### Header #3", "header #3"],
        ["###Header No Space", "header no space"],
    ],
)
def test_get_block_name(expected, result):
    """Verify that get_block_name returns the string part of # headers"""
    assert md.get_block_name(expected) == result


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        ["key: value", ("key", "value")],
        ["key: value: 2", ("key", "value: 2")],
        [" key: value ", ("key", "value")],
    ],
)
def test_extract_property(input, expected):
    """Verify that the property is extracted with expected key and value"""
    assert md.split_property(input) == expected


def test_extract_property_list(c4_md):
    """Tests that the list from a property is correctly extracted"""
    results = md.extract_fields(c4_md.read())
    assert sorted(results["tags"]) == ["special", "special2"]


def test_extract_header_list(c5_md):
    """Tests that the list from a header is correctly extracted"""
    results = md.extract_fields(c5_md.read())
    assert sorted(results["tags"]) == ["special", "special2", "special3"]

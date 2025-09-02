from copy import copy
from io import TextIOWrapper
import os
import pytest
from scrummd.exceptions import ImplicitChangeOfTypeError, UnsupportedModificationError
import scrummd.source_md as source_md
from typing import Generator
from fixtures import data_config

# Should these be one fixture?


@pytest.fixture(scope="function")
def md1_fo() -> Generator[TextIOWrapper, None, None]:
    fo = open("test/data/md1.md")
    yield fo
    fo.close()


@pytest.fixture(scope="function")
def md2_fo() -> Generator[TextIOWrapper, None, None]:
    fo = open("test/data/md2.md")
    yield fo
    fo.close()


@pytest.fixture(scope="function")
def md3_fo() -> Generator[TextIOWrapper, None, None]:
    fo = open("test/special_cases/header_summary/md3.md")
    yield fo
    fo.close()


@pytest.fixture(scope="function")
def c4_md() -> Generator[TextIOWrapper, None, None]:
    fo = open("test/data/collection2/c4.md")
    yield fo
    fo.close()


@pytest.fixture(scope="function")
def c5_md() -> Generator[TextIOWrapper, None, None]:
    fo = open("test/data/collection2/c5.md")
    yield fo
    fo.close()


@pytest.fixture(scope="function")
def c7_md() -> Generator[TextIOWrapper, None, None]:
    fo = open("test/data/collection4/c7.md")
    yield fo
    fo.close()


def test_extract_property_from_full_file(data_config, md1_fo):
    """Test extracting property variables from an md file"""
    results = source_md.extract_fields(data_config, md1_fo.read())
    assert results["summary"] == "Summary of card"
    assert results["status"] == "Ready"


def test_extract_header(data_config, md1_fo):
    """Test extracting header style variables from an md file"""
    results = source_md.extract_fields(data_config, md1_fo.read())
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
def test_get_block_name(data_config, expected, result):
    """Verify that get_block_name returns the string part of # headers"""
    assert source_md.get_block_name(expected) == result


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        ["key: value", ("key", "value")],
        ["key: value: 2", ("key", "value: 2")],
        [" key: value ", ("key", "value")],
    ],
)
def test_extract_property(data_config, input, expected):
    """Verify that the property is extracted with expected key and value"""
    assert source_md.split_property(input) == expected


def test_extract_property_list(data_config, c4_md):
    """Tests that the list from a property is correctly extracted"""
    results = source_md.extract_fields(data_config, c4_md.read())
    assert sorted(results["tags"]) == ["special", "special2"]


def test_extract_header_list(data_config, c5_md):
    """Tests that the list from a header is correctly extracted"""
    results = source_md.extract_fields(data_config, c5_md.read())
    assert sorted(results["tags"]) == ["special", "special2", "special3"]


def test_extract_variety(data_config, c7_md):
    """Tests that where there's a variety of fields, all are added"""
    # Test exists because of bug noted in [[cli019]]
    results = source_md.extract_fields(data_config, c7_md.read())
    assert sorted(results.keys()) == ["assignee", "status", "summary", "test list"]


def test_underline_header_summary(data_config, md3_fo):
    config = copy(data_config)
    config.allow_header_summary = True
    results = source_md.extract_fields(config, md3_fo.read())
    assert results["summary"] == "This is the summary without it being in a property"


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        ["double equals", source_md.FieldStr("Test")],
        ["list", [source_md.FieldStr("Item 1"), source_md.FieldStr("Item 2")]],
        ["entry after list", source_md.FieldStr("Multi\nLine\nField")],
    ],
)
def test_underline_header_values(data_config, md3_fo, input, expected):
    config = copy(data_config)
    results = source_md.extract_fields(config, md3_fo.read())
    assert results[input] == expected


def test_property_meta(data_config, md1_fo):
    results = source_md.extract_fields(data_config, md1_fo.read())
    assert results.meta("summary").md_type == source_md.FIELD_MD_TYPE.PROPERTY


def test_block_meta(data_config, md1_fo):
    results = source_md.extract_fields(data_config, md1_fo.read())
    assert results.meta("description").md_type == source_md.FIELD_MD_TYPE.BLOCK


def test_underline_header_summary_meta(data_config, md3_fo):
    config = copy(data_config)
    config.allow_header_summary = True
    results = source_md.extract_fields(config, md3_fo.read())
    assert results.meta("summary").md_type == source_md.FIELD_MD_TYPE.IMPLICIT_SUMMARY


def test_underline_head_summary_order(data_config, md3_fo):
    config = copy(data_config)
    config.allow_header_summary = True

    results = source_md.extract_fields(config, md3_fo.read())
    assert results.order() == [
        "note",
        "summary",
        "double equals",
        "list",
        "entry after list",
    ]


def test_ignore_code_block(data_config, md2_fo):
    """Test that fields inside a ``` block are ignored, and just form part of the value"""
    results = source_md.extract_fields(data_config, md2_fo.read())
    # This would be 'Test Card 4' if it read inside the code block
    assert results["summary"] == "Test Card With Code"
    # This wouldn't be there if the block wasn't there as a string
    assert "Test Card 4" in results["description"]
    # This wouldn't be there if it stopped adding after the block
    assert "something else" in results["description"]


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        ["abc", []],
        ["[[card1]] [[card2]]", ["card1", "card2"]],
        ["123 [[card1]] [[card2]]", ["card1", "card2"]],
        [["[[card1]]", "[[card2]][[card3]]"], ["card1", "card2", "card3"]],
        ["123 [[!card1]] [[card2]]", ["card2"]],
        [["[[card1]]", "[[card2]] [[!card3]]"], ["card1", "card2"]],
    ],
)
def test_extract_collection(input, expected):
    results = source_md.extract_collection(input)
    assert results == expected


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        ["test", [source_md.StringComponent("test")]],
        [
            "test[[card]]test2",
            [
                source_md.StringComponent("test"),
                source_md.CardComponent("card"),
                source_md.StringComponent("test2"),
            ],
        ],
        ["[[card]]", [source_md.CardComponent("card")]],
        [
            "[[card]][[card2]]",
            [source_md.CardComponent("card"), source_md.CardComponent("card2")],
        ],
    ],
)
def test_fieldstr_component(input, expected):
    """Test that the components of a str are properly separated"""
    field = source_md.FieldStr(input)
    assert field.components() == expected


def test_modify_property_basic(data_config, md1_fo):
    """Test modifying a property"""
    extracted = source_md.extract_fields(data_config, md1_fo.read())
    modify = modify = extracted.apply_modifications(data_config, [("status", "Done")])
    assert modify["status"] == "Done"
    assert modify.meta("status").md_type == source_md.FIELD_MD_TYPE.PROPERTY


def test_modify_block_basic(data_config, md1_fo):
    """Test modifying a block"""
    extracted = source_md.extract_fields(data_config, md1_fo.read())
    modify = extracted.apply_modifications(
        data_config, [("description", "A\n new\n multiline description.")]
    )
    assert modify["description"] == "A\n new\n multiline description."
    assert modify.meta("description").md_type == source_md.FIELD_MD_TYPE.BLOCK


def test_modify_block_with_code_block(data_config, md1_fo):
    """Test modifying a block that includes a code block"""
    extracted = source_md.extract_fields(data_config, md1_fo.read())
    example_card_text = """Example card:
```
---
Summary: Test Card 4
Index: 5
---
# Description

Stuff here
```"""
    modify = extracted.apply_modifications(
        data_config, [("description", example_card_text)]
    )
    assert modify["description"] == example_card_text
    assert modify.meta("description").md_type == source_md.FIELD_MD_TYPE.BLOCK


def test_modify_header_summary(data_config, md3_fo):
    """Test modifying a header summary"""
    extracted = source_md.extract_fields(data_config, md3_fo.read())
    modify = extracted.apply_modifications(data_config, [("summary", "A new summary")])
    assert modify["summary"] == "A new summary"
    assert modify.meta("summary").md_type == source_md.FIELD_MD_TYPE.IMPLICIT_SUMMARY


def test_modify_list(data_config, c4_md):
    """Test modifying a list field"""
    extracted = source_md.extract_fields(data_config, c4_md.read())
    modify = extracted.apply_modifications(
        data_config, [("tags", """- new tag 1\n- new tag 2""")]
    )
    assert modify["tags"] == ["new tag 1", "new tag 2"]
    assert modify.meta("tags").md_type == source_md.FIELD_MD_TYPE.PROPERTY


def test_modify_invalid_newline_in_property(data_config, md1_fo):
    """Test that adding a newline in a property fails."""
    extracted = source_md.extract_fields(data_config, md1_fo.read())
    with pytest.raises(ImplicitChangeOfTypeError):
        modify = extracted.apply_modifications(
            data_config, [("status", "Done\nActually?")]
        )


def test_modify_invalid_newline_in_list(data_config, c4_md):
    """Test that adding a newline in an entry of a list fails."""
    extracted = source_md.extract_fields(data_config, c4_md.read())
    with pytest.raises(ImplicitChangeOfTypeError):
        modify = extracted.apply_modifications(
            data_config, [{"tags", ["tag1", "tag2\nnew line"]}]
        )


def test_modify_invalid_index(data_config, md1_fo):
    """Test that attempting to modify the index fails."""
    extracted = source_md.extract_fields(data_config, md1_fo.read())
    with pytest.raises(UnsupportedModificationError):
        modify = extracted.apply_modifications(data_config, {"index": "duck"})


def test_modify_multiple(data_config, md1_fo):
    """Test modifying multiple fields."""
    extracted = source_md.extract_fields(data_config, md1_fo.read())
    modify = extracted.apply_modifications(
        data_config,
        [
            ("status", "Done"),
            ("description", "A\n new\n multiline description."),
        ],
    )
    assert modify["status"] == "Done"
    assert modify["description"] == "A\n new\n multiline description."
    assert modify.meta("status").md_type == source_md.FIELD_MD_TYPE.PROPERTY
    assert modify.meta("description").md_type == source_md.FIELD_MD_TYPE.BLOCK


def test_modify_add_logical_block(data_config, md1_fo):
    extracted = source_md.extract_fields(data_config, md1_fo.read())
    modify = extracted.apply_modifications(
        data_config, [("new field", "A\n new\n multiline description.")]
    )
    assert modify["new field"] == "A\n new\n multiline description."
    assert modify.meta("new field").md_type == source_md.FIELD_MD_TYPE.BLOCK
    assert modify.order[-1] == "new field"


def test_modify_add_logical_property(data_config, md1_fo):
    extracted = source_md.extract_fields(data_config, md1_fo.read())
    modify = extracted.apply_modifications(
        data_config, [("new field", "A new summary")]
    )
    assert modify["new field"] == "A new summary"
    assert modify.meta("new field").md_type == source_md.FIELD_MD_TYPE.PROPERTY
    assert modify.order[-1] == "new field"

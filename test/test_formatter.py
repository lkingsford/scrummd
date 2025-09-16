from pathlib import Path
import pytest
import scrummd.card
import scrummd.formatter
from fixtures import data_config, test_collection


def test_basic_formatting(data_config, test_collection):
    card = scrummd.card.from_str(
        data_config,
        "---\nsummary: test\n---\n",
        "collection",
        Path("collection/test.md"),
    )
    assert (
        scrummd.formatter.format_from_str(
            data_config, "summary: {{ card.summary }}", card, {}
        )
        == "summary: test"
    )


@pytest.mark.parametrize(
    "input, expected_result",
    (
        pytest.param("Field [[c1]]", "Field [c1 Bob Ready]", id="string_and_reference"),
        pytest.param(
            "[[c2]][[c3]]",
            "[c2 Mary ready][c3 Bob Done]",
            id="card_reference_with_two_cards",
        ),
        pytest.param(
            "[[!c2]][[c3]]",
            "[c2 Mary ready][c3 Bob Done]",
            id="card_reference_with_negation",
        ),
        pytest.param(
            "[[zz01]]", "[zz01 (MISSING)]", id="card_reference_with_missing_card"
        ),
    ),
)
def test_format_with_card_reference(
    data_config, test_collection, input, expected_result
):
    basic_reference_template = """{% macro card_ref(component) -%}
    {%- if component.card is not none -%}
        [{{ component.card.index }} {{ component.card.udf["assignee"] }} {{ component.card.udf["status"] }}]
    {%- else -%}
        [{{ component.card_index }} (MISSING)]
    {%- endif %}
{%- endmacro %}
{{- card.udf["key"] | apply_field_macros() }}"""

    test_card = f""" ---
summary: Test Card
key: { input }
    ---
    """

    card = scrummd.card.from_str(
        data_config, test_card, "collection", Path("collection/card_ref.md")
    )
    result = scrummd.formatter.format_from_str(
        data_config, basic_reference_template, card, test_collection
    )
    assert result == expected_result


def test_format_card_reference_no_formatter(data_config, test_collection):
    template = """{{ card.udf["key"] | apply_field_macros() }}"""
    test_card = """ ---
summary: Test Card
key: Field [[c2]]
---"""
    card = scrummd.card.from_str(
        data_config, test_card, "collection", Path("collection/card_ref.md")
    )
    result = scrummd.formatter.format_from_str(
        data_config, template, card, test_collection
    )
    assert result == "Field [[ c2 ]]"

from pathlib import Path
import scrummd.card
import scrummd.formatter
from fixtures import data_config, test_collection


def test_basic_formatting(data_config, test_collection):
    card = scrummd.card.Card.from_str(
        data_config,
        "---\nsummary: test\n---\n",
        "collection",
        Path("collection/test.md"),
    )
    assert scrummd.formatter.format("summary: $summary", card) == "summary: test"


def test_format_with_card_reference(data_config, test_collection):
    basic_reference_template = """{% macro card_ref(card) -%}
    {{ card.index }} {{ card.assignee }} {{ card.status }})
{%- endmacro %}
{{ summary | expand_refs(card_ref) }}
{{ udf["key"] | expand_refs(card_ref) }}
{{ udf["key2"] | expand_refs(card_ref) }}
{{ udf["key3"] | expand_refs(card_ref) }}
"""

    test_card = """
    ---
    summary: Test Card
    key: Field [[c1]]
    key 2: [[c2]][[c3]]
    key 3: [[!c2]][[c3]]
    ---
    """

    expected_result = """Test Card
Field [c1 Bob Ready]
[c2 Mary ready][c3 Bob Done]
[c2 Mary ready][c3 Bob Done]"""

    card = scrummd.card.from_str(
        data_config, test_card, "collection", Path("collection/card_ref.md")
    )
    assert (
        scrummd.formatter.format(basic_reference_template, card, test_collection)
        == expected_result
    )

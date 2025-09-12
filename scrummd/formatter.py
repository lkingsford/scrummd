"""Tools for formatting a card to output"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional
import jinja2

from scrummd.source_md import FieldStr, CardComponent, StringComponent


if TYPE_CHECKING:
    from scrummd.card import Card
    from scrummd.scard import Collection

env = jinja2.Environment()


def _expand_field_str(
    field: FieldStr,
    cards: "Collection",
    format_macro: Optional[Callable] = None,
) -> str:
    """Format any card references in a field str with the template

    Args:
        field (Field): Field to expand
        cards (Collection): Collection of cards
        format_macro (Callable): Macro defined in template for formatting card references. Defaults to [[ {card.index} ]].

    Returns:
        str: Field with references formatted by template
    """

    # Default to "[[ index ]]" if no macro provided
    format_macro = format_macro or (lambda component: f"[[ {component.card.index} ]]")

    response = ""
    for component in field.components(cards):
        if isinstance(component, CardComponent):
            response += format_macro(component=component)
        else:
            assert isinstance(component, StringComponent)
            response += component.value

    return response


env.filters["expand_field_str"] = _expand_field_str


def format(formatter: str, card: "Card", collection: "Collection") -> str:
    """Format a card per the given template

    Args:
        formatter (str): Template to use
        card (Card): Card to format

    Returns:
        str: Card formatted per template
    """
    template = env.from_string(formatter)
    return template.render(card=card, cards=collection)

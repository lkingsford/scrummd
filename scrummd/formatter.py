"""Tools for formatting a card to output"""

from typing import TYPE_CHECKING
import jinja2


if TYPE_CHECKING:
    from scrummd.card import Card
    from scrummd.scard import Collection


def format(formatter: str, card: "Card", collection: "Collection") -> str:
    """Format a card per the given template

    Args:
        formatter (str): Template to use
        card (Card): Card to format

    Returns:
        str: Card formatted per template
    """
    template = jinja2.Template(formatter)
    return template.render(card=card)

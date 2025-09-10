"""Tools for formatting a card to output"""

import jinja2

from scrummd.scard import Card
from scrummd.scard import CardComponent
from scrummd.scard import Field
from scrummd.scard import FieldStr
from scrummd.scard import FieldNumber
from scrummd.scard import StringComponent
from scrummd.scard import Collection


def format(formatter: str, card: Card) -> str:
    """Format a card per the given template

    Args:
        formatter (str): Template to use
        card (Card): Card to format

    Returns:
        str: Card formatted per template
    """
    template = jinja2.Template(formatter)

"""Tools for getting templates, and formatting a card with them to output"""

import pathlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional
import jinja2
from importlib import resources

from scrummd.source_md import FieldStr, CardComponent, StringComponent

import scrummd.config
from scrummd.exceptions import TemplateNotFoundError


if TYPE_CHECKING:
    from scrummd.card import Card
    from scrummd.scard import Collection

env = jinja2.Environment()

_compiled_templates: dict[str, jinja2.Template] = {}


def load_template(filename: str, config: scrummd.config.ScrumConfig) -> jinja2.Template:
    """Load the template (using path rules) from the filename.

    Tries to find the file in the following order:
        1. The file in the current directory
        2. The file in the ``.templates`` directory in the ``scrum_path``
        3. The file in the ``templates`` directory in the ``scrum_path``
        4. The module resources

    Args:
        filename (str): Filename of template to load
        config (scrummd.config.ScrumConfig): Scrum Config

    Returns:
        jinja2.Template: Compiled Jinja2 Template
    """

    if filename in _compiled_templates:
        return _compiled_templates[filename]

    scrum_path = pathlib.Path(config.scrum_path)
    paths: list[pathlib.Path] = [
        pathlib.Path(filename),
        scrum_path / ".templates" / filename,
        scrum_path / "templates" / filename,
    ]

    # IT'S MY LIBRARY AND I'LL MAKE IT DENSE IF I WANT TO!
    found_file = next(
        (open(path, "rt") for path in paths if path.exists()),
        (
            resources.open_text(scrummd, "templates/" + filename)
            if resources.is_resource(scrummd, "templates/" + filename)
            else None
        ),
    )

    if found_file is None:
        raise TemplateNotFoundError(filename, paths)

    return env.from_string(found_file.read())


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


def format(
    config: scrummd.config.ScrumConfig,
    template_filename: str,
    card: "Card",
    collection: "Collection",
) -> str:
    """Format the card with the named template.

    Args:
        config (scrummd.config.ScrumConfig): Scrum Config
        template_filename (str): Name of template
        card (Card): Card to format
        collection (Collection): Collection of cards

    Returns:
        str: Card formatted per template
    """
    template = load_template(template_filename, config)
    return template.render(card=card, cards=collection)


def format_from_str(
    template: str,
    card: "Card",
    collection: "Collection",
) -> str:
    """Format a card with the provided template.

    Args:
        template (str): Template to use
        card (Card): Card to format
        collection (Collection): Collection of cards

    Returns:
        str: Card formatted per template
    """
    compiled_template = env.from_string(template)
    return compiled_template.render(card=card, cards=collection)

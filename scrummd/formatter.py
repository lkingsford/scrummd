"""Tools for getting templates, and formatting a card with them to output"""

import pathlib
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional, Any
from importlib import resources
import jinja2

from scrummd.source_md import (
    FieldMetadata,
    FieldStr,
    CardComponent,
    StringComponent,
    GroupedKeys,
)

import scrummd.config
from scrummd.exceptions import TemplateNotFoundError


if TYPE_CHECKING:
    from scrummd.card import Card
    from scrummd.scard import Collection

env = jinja2.Environment()

_compiled_templates: dict[str, jinja2.Template] = {}


DEFAULT_MD_TEMPLATE = "default_md.j2"
"""The default MD template"""

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

    # Check git history for previous version; this was modified for Python 3.11 support:
    # Python 3.13 files supports folder traversing in the path, 3.11 does not.
    module_path = resources.files("scrummd") / "templates" / filename
    found_file = next(
        (open(path, "rt") for path in paths if path.exists()),
        (
            module_path.open('r') if module_path.is_file() else None
        ),
    )

    if found_file is None:
        raise TemplateNotFoundError(filename, paths)

    return env.from_string(found_file.read())


@jinja2.pass_context
def _apply_field_macros(
    context: jinja2.runtime.Context,
    field: FieldStr,
) -> str:
    """Format any card references in a field str with the template

    Args:
        field (Field): Field to expand
        cards (Collection): Collection of cards
        format_macro (Callable): Macro defined in template for formatting card references. Defaults to [[ {card.index} ]].

    Returns:
        str: Field with references formatted by template
    """

    format_macro = context.get(
        "card_ref", lambda component: f"[[ {component.card.index} ]]"
    )
    cards = context["cards"]

    response = ""
    for component in field.components(cards):
        if isinstance(component, CardComponent):
            response += format_macro(component=component)
        else:
            assert isinstance(component, StringComponent)
            response += component.value

    return response


env.filters["apply_field_macros"] = _apply_field_macros


def _is_interactive() -> bool:
    """Check if runing in an interactive terminal

    Returns:
        bool: True if TTD
    """
    return sys.stdout.isatty()


@dataclass(frozen=True)
class TemplateFields:
    """Fields to pass to the template"""

    config: scrummd.config.ScrumConfig
    """The relevant ScrumMD config."""

    card: "Card"
    """The card being formatted."""

    cards: "Collection"
    """The full collection of cards."""

    interactive: bool
    """Whether the command is being run in an interactive terminal."""

    groups: GroupedKeys
    """Ordered keys groups by their block type in the md file."""

    meta: dict[str, FieldMetadata]
    """Metadata from the fields of original source md."""


def _template_fields(
    config: scrummd.config.ScrumConfig, card: "Card", cards: "Collection"
) -> TemplateFields:
    """Fields to pass to the template"""
    return TemplateFields(
        config=config,
        card=card,
        cards=cards,
        interactive=_is_interactive(),
        groups=card.parsed_md.keys_grouped_by_field_md_type(),
        meta=card.parsed_md._meta,  # TODO: Move _meta to a property or read only dict
    )


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
    return template.render(**_template_fields(config, card, collection).__dict__)


def format_from_str(
    config: scrummd.config.ScrumConfig,
    template: str,
    card: "Card",
    collection: "Collection",
) -> str:
    """Format a card with the provided template.

    Args:
        config (scrummd.config.ScrumConfig): Scrum Config
        template (str): Template to use
        card (Card): Card to format
        collection (Collection): Collection of cards

    Returns:
        str: Card formatted per template
    """
    compiled_template = env.from_string(template)
    return compiled_template.render(
        **_template_fields(config, card, collection).__dict__
    )

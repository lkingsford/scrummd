"""Tools for loading templates"""

import pathlib
import jinja2
from importlib import resources

import scrummd.config
from scrummd.exceptions import TemplateNotFoundError


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
            resources.open_text(scrummd, filename)
            if resources.is_resource(scrummd, filename)
            else None
        ),
    )

    if found_file is None:
        raise TemplateNotFoundError(filename, paths)

    return jinja2.Template(found_file.read())

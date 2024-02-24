"""The ScrumConfig class to configure processing scrum files."""

from scrummd import const


class ScrumConfig:
    """The current configuration for processing scrum files."""

    scrum_path: str = const.DEFAULT_SCRUM_FOLDER_NAME
    """Base path for the scrum folder"""

    strict: bool = False
    """Fail on any error with the scrum folder (such as duplicate index or invalid file)"""

    columns: list[str] = ["index", "summary"]
    """List of columns to return in output"""

    omit_headers: bool = False
    """Omit headers from output"""

    fields: dict[str, str] = {}
    """Fields with limited permitted values and defined order"""

    def __init__(
        self,
        scrum_path=scrum_path,
        strict=strict,
        columns=columns,
        omit_headers=omit_headers,
        fields=fields,
    ) -> None:
        self.scrum_path = scrum_path
        self.strict = strict
        self.columns = columns
        self.omit_headers = omit_headers
        self.fields = fields

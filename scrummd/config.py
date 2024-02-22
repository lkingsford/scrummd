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

    def __init__(self, scrum_path=scrum_path, strict=strict, columns=columns) -> None:
        self.scrum_path = scrum_path
        self.strict = strict
        self.columns = columns

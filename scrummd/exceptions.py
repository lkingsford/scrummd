class ValidationError(ValueError):
    """Raised if there's a failure validating a card that's being built"""

    pass


class InvalidFileError(ValidationError):
    """Raised if the file is not a valid scrummd md file"""

    pass


class RuleViolationError(ValidationError):
    """Raised if there is a validation of one of the rules for this scrum repo"""

    pass


class InvalidRestrictedFieldValueError(RuleViolationError):
    """Raised if there's a field with defined values, and a value in a file that isn't in those defined values"""

    pass


class DuplicateIndexError(RuleViolationError):
    """Raised when an index of a card is declared twice in the collection."""

    def __init__(self, index, path):
        self.index = index
        self.path = path
        super().__init__(f"Duplicate index {self.index} found in {self.path}")


class InvalidGroupError(ValueError):
    """Raised when a field is not a valid group"""

    pass


class RequiredFieldNotPresentError(RuleViolationError):
    """Raised when a field required by config isn't present"""

    pass


class ImplicitChangeOfTypeError(ValidationError):
    """Raised when the existing type of a field (list, property, block) no longer supports the new value."""


class UnsupportedModificationError(ValidationError):
    """Raised when a field can't be modified."""


class TemplateNotFoundError(FileNotFoundError):
    """Raised when a template file can't be found."""

    def __init__(self, filename, searched_paths):
        self.searched_paths = searched_paths
        super().__init__(
            f"Template {filename} not found in {searched_paths} or module."
        )


class ValuesNotPresentError(ValidationError):
    """Raised when a field isn't present that is to be removed."""

    def __init__(self, values: list[str], field: str, index: Optional[str] = None):
        self.field = field
        self.index = index
        if index:
            super().__init__(f"Values {values} are not in field {field} in {index}.")

        super().__init__(f"Values {values} are not in field {field}.")


class FieldNotPresentError(ValidationError):
    """Raised when a field that should be modified isn't present."""

    def __init__(self, field: str, index: Optional[str] = None):
        self.field = field
        self.index = index
        if index:
            super().__init__(f"Field {field} not found in {index}")
        super().__init__(f"Field {field} not found.")

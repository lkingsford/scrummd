class ValidationError(ValueError):
    """Triggered if there's a failure validating a card that's being built"""

    pass


class InvalidFileError(ValidationError):
    """Triggered if the file is not a valid scrummd md file"""

    pass


class RuleViolationError(ValidationError):
    """Triggered if there is a validation of one of the rules for this scrum repo"""

    pass


class InvalidRestrictedFieldValueError(RuleViolationError):
    """Triggered if there's a field with defined values, and a value in a file that isn't in those defined values"""

    pass


class DuplicateIndexError(RuleViolationError):
    """Called when an index of a card is declared twice in the collection."""

    def __init__(self, index, path):
        self.index = index
        self.path = path
        super().__init__(f"Duplicate index {self.index} found in {self.path}")


class InvalidGroupError(ValueError):
    """Called when a field is not a valid group"""

    pass


class RequiredFieldNotPresentError(RuleViolationError):
    """Called when a field required by config isn't present"""

    pass

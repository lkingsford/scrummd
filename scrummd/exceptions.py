class ValidationError(ValueError):
    """Triggered if there's a failure validating a card that's being built"""

    pass


class InvalidRestrictedFieldValueError(ValidationError):
    """Triggered if there's a field with defined values, and a value in a file that isn't in those defined values"""

    pass

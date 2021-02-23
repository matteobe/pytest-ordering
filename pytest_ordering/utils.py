"""
Utilities functions used to perform input validation, etc.
"""

from typing import List


class ValidationError(BaseException):

    def __init__(self, message: str):
        self.message = message
        super(ValidationError, self).__init__(message)


def require_not_none(to_be_validated, failure_message: str = "Must be specified but was None"):
    if to_be_validated is None:
        raise ValidationError(message=failure_message)


def require_not_empty(to_be_validated, failure_message: str = "Must not be empty"):
    if len(to_be_validated) == 0:
        raise ValidationError(message=failure_message)


def require_in_list(item, valid_items: List):
    if item not in valid_items:
        failure_message = f"Item '{item}' not in valid items list: {', '.join(valid_items)}"
        raise ValidationError(message=failure_message)

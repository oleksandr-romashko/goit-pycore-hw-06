"""
Name field for storing and validating contact names.

This module defines the `Name` class which extends `Field` and ensures
the contact name is valid on assignment.
"""

from field import Field
from validators.field_validators import validate_username_length


class Name(Field):
    """
    Class for storing and validating contact names.

    Ensures the name is validated on initialization.
    """

    def __init__(self, name: str):
        validate_username_length(name)
        super().__init__(name)

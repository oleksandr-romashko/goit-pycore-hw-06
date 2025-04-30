"""
Phone field for storing and validating phone numbers.

This module defines the `Phone` class which extends `Field` and ensures
the phone number is valid on assignment or update.
"""

from field import Field
from validators.field_validators import validate_phone_number


class Phone(Field):
    """
    Class for storing and validating phone numbers.

    Ensures the phone number matches expected format during initialization and
    value changes.
    """

    def __init__(self, phone: str):
        self._validate_phone(phone)
        super().__init__(phone)

    def update_phone(self, phone: str):
        """Sets a new validated phone value."""
        self._validate_phone(phone)
        self.value = phone

    def _validate_phone(self, phone: str):
        validate_phone_number(phone)

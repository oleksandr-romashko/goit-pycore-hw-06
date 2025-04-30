"""
Field base class for storing values in contact records.

This module defines the base `Field` class used for contact fields.
It provides basic storage and string conversion behavior.
"""


class Field:
    """
    Base class for contact record fields.

    Stores a single value and provides a default string representation.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

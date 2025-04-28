"""
Custom error for validation problems.

Intentionally implemented using functional style and avoiding OOP.
This error is derived from the built-in ValueError.
"""
ValidationError = type("ValidationError", (ValueError,), {})

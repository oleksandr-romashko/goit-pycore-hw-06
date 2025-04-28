"""
This module provides a decorator `@with_pattern` which attaches a regex pattern
(both raw string and compiled version) to the decorated function as attributes.

It is intended for use in functions where consistent regex patterns
are required for various purposes like validation or parsing operations.

The decorator will attempt to compile the pattern during decoration. If the
pattern is invalid, a `ValueError` will be raised.

Usage:
    @with_pattern(r"your-pattern-here")
    def parse_func(...):
        ...

    # Access inside decorated function:
    pattern = parse_func.PATTERN  # as raw pattern
    pattern = parse_func.compiled_pattern  # as compiled pattern
"""
import re
from functools import wraps
from typing import Callable, Any


def with_pattern(pattern: str) -> Callable:
    """
    Decorator that attaches a regex pattern (both raw string and compiled version)
    to the decorated function as attributes.

    If the pattern cannot be compiled, it raises an error.
    """
    # Try to compile the pattern during decoration
    try:
        compiled_pattern = re.compile(pattern)
    except re.error as exc:
        raise ValueError(f"Invalid regex pattern: {pattern}") from exc

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Wrapper function that executes the original function.

            This function simply calls the original decorated function and
            allows access to the attached pattern attributes.
            """
            return func(*args, **kwargs)

        # Attach both raw pattern and compiled pattern as attributes
        wrapper.PATTERN = pattern
        wrapper.compiled_pattern = compiled_pattern

        return wrapper

    return decorator

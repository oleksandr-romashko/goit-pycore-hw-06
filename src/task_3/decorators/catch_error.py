"""
This module provides a decorator `@catch_error` designed to wrap functions
with a try-except block to gracefully handle common runtime errors.

It captures and prints friendly error messages for expected issues like file
access problems, invalid input, or unexpected system errors. The program exits
with a specific exit code based on the error type.

- Exit code 1: For known errors like ValueError, FileNotFoundError,
               PermissionError, etc.
- Exit code 2: For unexpected errors.

Usage:
    @catch_error
    def main():
        ...
"""
import sys
from functools import wraps
from typing import Callable, Any


def catch_error(func: Callable) -> Callable:
    """
    This decorator wraps a function to handle common runtime errors.

    Args:
        func (callable): The function to decorate.

    Returns:
        callable: A wrapped version of the original function with error handling.

    Raises:
        SystemExit: Exits the program with code based on the error type.
    """

    @wraps(func)
    def inner(*args, **kwargs) -> Any:
        """
        This inner function calls the original function and handles any errors
        that occur during execution.

        It handles expected errors and unexpected with a generic message and
        a different exit code.

        Args:
            *args: Arguments to pass to the original function.
            **kwargs: Keyword arguments to pass to the original function.

        Returns:
            The result of the original function if no error occurs.

        Raises:
            SystemExit: Terminates the program if an error is caught.
        """
        try:
            return func(*args, **kwargs)
        except (
            ValueError,
            FileNotFoundError,
            PermissionError,
            IsADirectoryError,
            OSError,
        ) as exc:
            print(f"Error: {exc}")
            sys.exit(1)
        except Exception as exc:
            print(f"Error: An unexpected error occurred {exc}.")
            sys.exit(2)

    return inner

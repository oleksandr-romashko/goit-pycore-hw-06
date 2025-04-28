"""
Provides functionality to extract something from a text.
"""

import re
from typing import Iterator


def generator_numbers(text: str) -> Iterator[float]:
    """
    Generator function that extracts all valid floating-point numbers from a given text.

    Parameters:
        text (str): The input string containing the numbers.

    Yields:
        float: The next number (integer or float) found in the text, converted to float.
    """
    # Define regex pattern and compile it for performance
    # Matches floats like 1000.01, 27.45 etc.
    pattern = re.compile(r"\b\d+(?:\.\d+)?\b")

    # Find all matches in the text and yield them as float
    for match in pattern.finditer(text):
        yield float(match.group())

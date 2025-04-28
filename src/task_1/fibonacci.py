"""
This module implements a recursive Fibonacci number generator with caching
(memoization) using closures.

The implementation is based on lexical scoping principles (closures), where
the inner function maintains access to the cache defined in the outer function.

Example:
    fib = caching_fibonacci()
    print(fib(10))  # Outputs: 55
"""

import sys
import time


def caching_fibonacci():
    """
    Returns a Fibonacci function with internal caching.

    The returned function computes the n-th Fibonacci number using recursion,
    storing previously computed results in a cache to avoid redundant
    calculations.

    Returns:
        function: A function that takes an integer n and returns the n-th
                  Fibonacci number.
    """
    # Dictionary used to store cached values in a key-value form
    cache = {}

    def fibonacci(n: int) -> int:
        """
        Computes the n-th Fibonacci number using a recursive approach
        with caching.

        Args:
            n (int): The position in the Fibonacci sequence.

        Returns:
            int: The n-th Fibonacci number.

        Raises:
            ValueError: If the recursion limit is exceeded due to too large
                        input.

        Notes:
            - For n <= 0, the function returns 0.
            - For n == 1, the function returns 1.
            - Uses a closure to persist cache across recursive calls.
        """

        # Base recursion cases
        if n <= 0:
            return 0

        if n == 1:
            return 1

        # Retrieve previously calculated cached value, if any
        if n in cache:
            return cache[n]

        # Calculate new value and cache it
        try:
            cache[n] = fibonacci(n - 1) + fibonacci(n - 2)
            return cache[n]
        except RecursionError as exc:
            # Handle case when calculation exceeds recursion depth limit
            raise ValueError(
                f"The given number is too large to handle it and "
                f'failed already at value "{n}". Please try a '
                "smaller value."
            ) from exc

    return fibonacci


if __name__ == "__main__":
    # Tests
    print(f"Running tests for {__file__}...")

    fib = caching_fibonacci()
    assert fib(-5) == 0
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(3) == 2
    assert fib(10) == 55
    assert fib(15) == 610
    too_large_value = sys.getrecursionlimit() + 100
    try:
        fib(too_large_value)
        assert (
            False
        ), f"Expected ValueError for n = {too_large_value}, but no error was raised."
    except ValueError as exc:
        assert "too large to handle" in str(exc)

    time_test_number = 40
    start = time.time()
    fib(time_test_number)
    print(
        f"Test time with internal dict cache for number {time_test_number} is: {time.time() - start} seconds"
    )

    print("✅ All tests passed successfully.")

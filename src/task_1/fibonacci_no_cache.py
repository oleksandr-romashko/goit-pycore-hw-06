"""
This module implements a recursive Fibonacci number generator.
No caching (memoization) is used.

Example:
    fib = caching_fibonacci()
    print(fib(10))  # Outputs: 55
"""

import sys
import time


def no_caching_fibonacci():
    """
    Returns a Fibonacci function without caching.

    Returns:
        function: A function that takes an integer n and returns the n-th
                  Fibonacci number.
    """

    def fibonacci(n: int) -> int:
        """
        Computes the n-th Fibonacci number using a recursive approach.

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
        """

        # Base recursion cases
        if n <= 0:
            return 0

        if n == 1:
            return 1

        # Calculate new value
        try:
            n = fibonacci(n - 1) + fibonacci(n - 2)
            return n
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

    fib = no_caching_fibonacci()
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
        f"Test time without cache for number {time_test_number} is: {time.time() - start} seconds"
    )

    print("✅ All tests passed successfully.")

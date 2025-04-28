"""
This module serves as the entry point for running the Fibonacci number calculator
implemented using a recursive function with memoization (caching).

It accepts an optional command-line argument to compute the N-th Fibonacci number.
If no argument is provided, it prints a few default examples.

Usage:
    $ python main.py                # Prints Fibonacci numbers for n = 10 and 15 (default examples)
    $ python main.py 20             # Prints the 20th Fibonacci number
    $ python main.py not_a_number   # Error: invalid input
    $ python main.py 2000           # Error: value too large (recursion depth exceeded - by default is around 1000)
"""

import sys

from fibonacci import caching_fibonacci


def main():
    """
    Main function to run the Fibonacci calculator.

    Behavior:
        - If a command-line argument is provided:
            - Tries to parse it as an integer.
            - Computes and prints the corresponding Fibonacci number.
            - Handles invalid input and recursion limit issues gracefully.
        - If no argument is given:
            - Prints default Fibonacci numbers for n = 10 and 15.

    Exit Codes:
        0 - Success
        1 - Invalid input (non-integer)
        2 - Input too large (recursion depth exceeded)
    """
    # Get the fibonacci function
    fib = caching_fibonacci()

    if len(sys.argv) > 1:
        # Use the fibonacci function to compute Fibonacci number from the first argument
        try:
            n = int(sys.argv[1])
        except ValueError:
            print("Provided argument is not a valid integer.")
            sys.exit(1)  # Invalid input

        try:
            print(fib(n))
        except ValueError as exc:
            print(f"Error: {exc}")
            sys.exit(2)  # Input too large (recursion depth exceeded)
    else:
        # Use the fibonacci function to compute predefined Fibonacci numbers
        print("No argument provided. Showing default examples:")
        print(fib(10))
        print(fib(15))


if __name__ == "__main__":
    main()

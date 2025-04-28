"""
Entry point of the program that calculates the total income found in a given text.
It uses `generator_numbers` to extract numbers and `sum_profit` to calculate their sum.
"""


from text_analyzer import generator_numbers
from profit_calculator import sum_profit


def main():
    """
    Main function to demonstrate the income extraction and summing process.
    """
    example_text = (
        "The total income of the employee consists of several "
        "parts: 1000.01 as base income, supplemented by "
        "additional receipts of 27.45 and 324.00 dollars."
    )

    total_income = sum_profit(example_text, generator_numbers)

    print(f"Total income: {total_income}")


if __name__ == "__main__":
    main()

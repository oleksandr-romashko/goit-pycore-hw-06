"""
Log Analyzer CLI Tool

This module provides a command-line interface for analyzing and displaying
information from log files. It allows users to inspect log levels, count
occurrences, filter specific log types, and show potential issues in the log
entries.

Main Functionalities:
    - Load and parse logs from a file
    - Count logs by level
    - Display summary statistics
    - Optionally display issues found in logs
    - Optionally display logs filtered by a specific level

Usage:
    python main.py <log_file_path> [--level LEVEL] [--show-issues] [--issue-unknown-levels]

Example Usage:
    Analyze all logs in a file:
        python main.py logs.txt

    Show only ERROR logs:
        python main.py logs.txt --level ERROR

    Display potential issues in the log file, such as unknown levels or
    malformed entries:
        python main.py logs.txt --issues

    Consider unknown log levels as issues during analysis:
        python main.py logs.txt --issue-unknown-levels

Arguments:
    log_file_path               (str, required):
        Path to the log file to be analyzed. The file is expected to contain one
        log entry per line, formatted with a timestamp, log level, and message.

        Expected Log File Format:
            Each line in the log file should follow this format:
                YYYY-MM-DD HH:MM:SS LEVEL Message text

            Example:
                2024-01-22 09:00:45 ERROR Database connection failed.
                2024-01-22 11:30:15 WARNING Backup process skipped due to low disk space.
                2024-01-22 12:45:00 INFO Daily report generated successfully.

Optional Arguments:
    --level LEVEL               (str, optional):
        If provided, filters logs and displays detailed information only for the
        specified log level.
        Example levels: ERROR, WARNING, INFO, DEBUG.

    --show-issues               (flag, optional):
        If set, displays possible issues in the logs, such as format
        inconsistencies or missing parts.

    --issue-unknown-levels      (flag, optional):
        If set, treats unknown or unexpected log levels as issues and includes
        them in the issues analysis.
"""
import sys
import os
from pathlib import Path
import re
from collections import Counter
import argparse

from decorators.catch_error import catch_error
from decorators.with_pattern import with_pattern


ARG_SHOW_LINES_WITH_ISSUES = "--issues"
ARG_ISSUE_UNKNOWN_LOG_LEVELS = "--issue-unknown"

KNOWN_LOG_LEVELS = {"ERROR", "WARNING", "INFO", "DEBUG"}

PATTERN_DATE = r"\d{4}-\d{2}-\d{2}"
PATTERN_TIME = r"\d{2}:\d{2}:\d{2}"
PATTERN_LINE = (
    rf"^(?P<date>{PATTERN_DATE})\s"
    rf"(?P<time>{PATTERN_TIME})\s"
    r"(?P<level>\b[A-Z]+\b)\s"  # More flexible log policy (all uppercase words)
    r"(?P<message>.+)$"
)

# Dict key for logs with issues
ISSUE_KEY = "log line with issue"


def handle_input_args() -> tuple[str, str | None, bool, bool]:
    """
    Parses and validates command-line arguments for the script.

    Returns:
        tuple: A tuple containing:
            - path_str (str): Path to the input log file (required).
            - log_level (str | None): Log level to filter by, if provided.
            - do_show_issues (bool): Whether to print lines with detected issues.
            - do_issue_unknown_levels (bool): Whether to treat unknown log levels as issues.

    Raises:
        ValueError: If path is missing or invalid, or unknown arguments are detected.
    """
    path_str = None
    log_level = None
    do_show_issues = False
    do_issue_unknown_levels = False

    # No args
    if len(sys.argv) == 1:
        raise ValueError(
            "Please provide obligatory path to log file as the first argument."
        )

    # Path arg = Fixed first arg (obligatory)
    if len(sys.argv) > 1:
        path_str = sys.argv[1].strip()
        if not path_str:
            raise ValueError("Invalid empty path value.")

    # Other optional args in any order
    for arg in sys.argv[2:]:
        arg = arg.lower()
        if arg == ARG_SHOW_LINES_WITH_ISSUES.lower():
            do_show_issues = True
        elif arg == ARG_ISSUE_UNKNOWN_LOG_LEVELS.lower():
            do_issue_unknown_levels = True
        elif not arg.startswith("--") and log_level is None:
            log_level = arg  # First non-flag treated as log level
        else:
            raise ValueError(f"Unknown or unsupported argument: '{arg}'")

    return (path_str, log_level, do_show_issues, do_issue_unknown_levels)


def handle_input_args_alternative() -> tuple[str, str | None, bool, bool]:
    """
    Parses and validates command-line arguments using argparse.

    Returns:
        tuple: A tuple containing:
            - path (str): Path to the input log file (required).
            - level (str | None): Log level to filter by, if provided.
            - issues (bool): Whether to print lines with detected issues.
            - issue_unknown (bool): Whether to treat unknown log levels as issues.
    """
    parser = argparse.ArgumentParser(
        description="Process log file for log level statistics."
    )
    parser.add_argument("path", help="Path to the log file")
    parser.add_argument("level", nargs="?", help="Log level to filter (optional)")
    parser.add_argument(
        "--issues", dest="issues", action="store_true", help="Show lines with issues"
    )
    parser.add_argument(
        "--issue-unknown",
        dest="issue_unknown",
        action="store_true",
        help="Treat unknown log levels as issues",
    )

    args = parser.parse_args()

    return args.path, args.level, args.issues, args.issue_unknown


def get_valid_path(path_str: str) -> Path:
    """
    Validates and resolves the given file path.

    This function checks the following conditions:
    1. The path exists.
    2. The path is a valid file.
    3. The file has read permissions.
    4. The file is not empty.

    If any of these conditions are not met, an exception will be raised.
    If the path is valid, it returns the absolute resolved path.

    Args:
        path_str (str): The path to the file to be validated.

    Returns:
        Path: The resolved absolute path if valid.

    Raises:
        FileNotFoundError: If the file does not exist or the extension is wrong.
        OSError: If the path is not a file, the file is empty, or if permissions are denied.
    """
    path = Path(path_str).resolve()

    # Check file existence
    if not path.exists():
        message = f"File '{path_str}' does not exist"

        # Also try check if file name is just missing .log extension
        path_with_extension = Path(path_str + ".log").resolve()
        if path_with_extension.exists():
            message += f". Maybe you wanted to use '{path_with_extension.name}'?"
        else:
            message += "."

        raise FileNotFoundError(message)

    # Check if path object is a file
    if not path.is_file():
        raise OSError(f"'{path_str}' is not a file")

    # Check if file has read permissions
    if not os.access(path, os.R_OK):
        raise OSError(f"You have no permissions to access '{path_str}' file.")

    # Check if file is empty
    if path.stat().st_size == 0:
        raise OSError(f'The file "{path_str}" is empty.')

    return path


@with_pattern(PATTERN_LINE)
def parse_log_line(
    line: str, line_number: int = 1, do_issue_unknown_levels: bool = False
) -> dict[str, str]:
    """
    Parses a log line into its components (date, time, level, and message).

    Attributes added by decorator:
        - compiled_pattern (re.Pattern): compiled regex pattern for matching the log line.

    Args:
        line (str): The log line to be parsed.
        line_number (int, optional): The line number in the log file. Default is 1.
        do_issue_unknown_levels (bool, optional): Flag to indicate whether unknown log levels
                                                  should be flagged as issues. Default is False.

    Returns:
        dict[str, str]: A dictionary containing the parsed log components or an error message.
            - For valid lines, the dictionary will contain:
                - "date": The date of the log entry.
                - "time": The time of the log entry.
                - "level": The log level (e.g., INFO, ERROR).
                - "message": The log message.
            - If the line doesn't match the expected format or has an unknown log level,
              an issue dictionary will be returned:
                - "log_line_with_issue": A string describing the issue with the line
                                         (e.g., INVALID FORMAT, UNKNOWN LOG LEVEL).
    """
    match = re.fullmatch(parse_log_line.compiled_pattern, line)

    if not match:
        # Issue not matched line
        issue_key = ISSUE_KEY
        cause = "(INVALID FORMAT)"
        line_number_with_content = f"line: {line_number}: {cause} {line}"
        return {issue_key: line_number_with_content}

    # Issue unknown log level
    if do_issue_unknown_levels and not match.group("level") in KNOWN_LOG_LEVELS:
        issue_key = ISSUE_KEY
        cause = "(UNKNOWN LOG LEVEL)"
        line_number_with_content_and_cause = f"line: {line_number}: {cause} {line}"
        return {issue_key: line_number_with_content_and_cause}

    # Valid match
    return {
        "date": match.group("date"),
        "time": match.group("time"),
        "level": match.group("level"),
        "message": match.group("message"),
    }


def load_logs(
    file_path: str, do_issue_unknown_levels: bool = False
) -> list[dict[str, str]]:
    """
    Loads log lines from a given file and parses them.

    Args:
        file_path (str): Path to the log file.
        do_issue_unknown_levels (bool): Whether unknown log levels should be treated as issues.

    Returns:
        list[dict[str, str]]: List of parsed log lines as dictionaries.

    Raises:
        ValueError: If the file path is invalid or the file cannot be opened.
    """
    # Validate path
    path = get_valid_path(file_path)

    # Read file lines
    logs = []
    with open(path, encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            parsed_line = parse_log_line(
                line.strip(), line_number, do_issue_unknown_levels
            )
            logs.append(parsed_line)

    return logs


def filter_logs_by_level(
    logs: list[dict[str, str]], level: str
) -> list[dict[str, str]]:
    """
    Filters log entries by a specified log level.

    Parameters:
        logs (list[dict[str, str]]): A list of log entries, each expected to
                                     contain a 'level' key.
        level (str): The log level to filter by (e.g., "INFO", "ERROR").

    Returns:
        list[dict[str, str]]: A list of log entries matching the specified log
                              level (case-insensitive).
    """
    filtered_logs = filter(
        lambda log: log.get("level") and log["level"].upper() == level.upper(), logs
    )
    return list(filtered_logs)


def count_logs_by_level(logs: list[dict[str, str]]) -> dict[str, int]:
    """
    Counts the number of log entries for each log level.

    Args:
        logs (list[dict[str, str]]): A list of parsed log entries where each entry is
                                      a dictionary containing log components (e.g., date, time, level, message).

    Returns:
        dict[str, int]: A dictionary where keys are log levels (e.g., INFO, ERROR),
                        and values are the number of occurrences for each level.
                        Includes an entry for 'log_line_with_issue' for logs with invalid formats.
                        The dictionary is sorted by the count value in descending order.
    """
    level_counts = Counter()

    for log in logs:
        if "level" in log:
            # Increase corresponding level count when log has 'level' key
            level_value = log["level"]
            level_counts[level_value] += 1
        else:
            # Increase issues count otherwise
            level_counts[ISSUE_KEY] += 1

    # Sort by count value DESC
    return dict(level_counts.most_common())


def display_log_counts(counts: dict[str, int]) -> None:
    """
    Displays the overall statistics by log levels:
    Formats and prints the results in a readable table format.
    The results show the count of entries for each log level.

    Log Level | Count
    ----------|-------
    INFO      | 4
    DEBUG     | 3
    ERROR     | 2
    WARNING   | 1
    """
    HEADER_ROW_TITLE_LOG_LEVEL = "Log Level"
    HEADER_ROW_TITLE_COUNT = "Count"
    SEPARATOR_HORIZONTAL = "|"
    SEPARATOR_VERTICAL = "-"
    NO_LEVELS_MESSAGE = "No valid log level found"

    level_lines = []
    issues = None

    header = (HEADER_ROW_TITLE_LOG_LEVEL, HEADER_ROW_TITLE_COUNT)

    # Define initial column width
    column_level_max_length = len(header[0])
    column_count_max_length = len(header[1])

    for key, count in counts.items():
        # Add logs with levels to the levels list
        # Add issues occurrences (if any)
        if key != ISSUE_KEY:
            level_lines.append((key, count))
        else:
            issues = (key.capitalize(), count)

        # Update columns width (if necessary)
        column_level_max_length = max(column_level_max_length, len(key))
        column_count_max_length = max(column_count_max_length, len(str(count)))

    # Organize table (add header, separator lines and potential info about issues)
    separator = ("", "")

    # If no log levels were found, add the message instead of log level
    if not level_lines:
        message = NO_LEVELS_MESSAGE
        column_level_max_length = max(column_level_max_length, len(message))
        level_lines.append((message, ""))  # Add empty message on no levels

    level_lines.insert(0, header)  # Add header
    level_lines.insert(1, separator)  # Add separator under the header

    if issues:
        level_lines.append(("", ""))  # Add separator above issues
        level_lines.append(issues)  # Add issues

    # Print formatted table
    for line in level_lines:
        if line == separator:
            # Print separator case
            print(
                f"{SEPARATOR_VERTICAL * (column_level_max_length + 1)}"
                f"{SEPARATOR_HORIZONTAL}"
                f"{SEPARATOR_VERTICAL * (column_count_max_length + 1)}"
            )
        else:
            # Print line with data case
            print(
                f"{line[0]:<{column_level_max_length + 1}}"
                f"{SEPARATOR_HORIZONTAL}"
                f" {line[1]:<{column_count_max_length}}"
            )


def display_log_details(logs: list[dict[str, str]], level: str = None) -> None:
    """
    Displays detailed information for each log entry.

    Formats and prints log entries in a readable form.
    If multiple log levels are present, the level is shown for each entry.

    Parameters:
        logs (list[dict[str, str]]): A list of log entries, each expected to
                                     include keys like 'date', 'time', 'level',
                                     and 'message'.
        level (str, optional): The log level used to filter/display context.
                               If None, all logs are considered.

    Output format:
        - If only one level is found:
            2024-01-22 09:00:45 - Database connection failed.
        - If multiple levels are found (log level added):
            2024-01-22 09:00:45 ERROR - Database connection failed.
            2024-01-22 10:30:55 WARNING - Disk usage above 80%.
    """
    if not logs:
        level_label = f"'{level.upper()}'" if level else "your"
        print(f"\nThere are no logs matching {level_label} log level.")
        return

    # Identify all unique log levels in the provided logs
    found_levels = set(log["level"] for log in logs if log.get("level"))

    # Display title with the found log levels
    print(
        f"\nLogs details for level{'s' if len(found_levels) > 1 else ''} '{', '.join(found_levels)}':"
    )

    # Display each log entry in a formatted way
    for log in logs:
        level_prefix = f"{log.get('level')} " if len(found_levels) > 1 else ""
        print(
            f"{log.get('date')} {log.get('time')} {level_prefix}- {log.get('message')}"
        )


def handle_log_issues(
    logs: list[dict[str, str]], counts: dict[str, int], do_show_issues: bool
) -> None:
    """
    Handles displaying or notifying about issues found in logs.

    Depending on whether issues are present in `counts` and the value of
    `do_show_issues`, it either prints the issue details, a help message,
    a confirmation of no issues, or nothing at all.

    Parameters:
    logs (list[dict[str, str]]): A list of log entries, where each log is
    expected to be a dictionary.
        If an issue is present in a log, it should contain a key corresponding
        to ISSUE_KEY (e.g. "log_line_with_issue") with the issue description as
        its value.
    counts (dict[str, int]): A dictionary mapping log levels (or special keys
                             like ISSUE_KEY) to the number of times they were
                             encountered.
    do_show_issues (bool): Whether to show full issue details if they exist.

    Decision matrix:

    Issues in counts    do_show_issues      Action
        True                True            Display found issues
        True                False           Show help message of found issues
        False               True            No issues found message
        False               False           Do nothing
    """
    if ISSUE_KEY in counts:
        print()
        if do_show_issues:
            # Display found issues
            print(f"Found the following {counts.get(ISSUE_KEY)} issues with logs:")
            issues = [log.get(ISSUE_KEY) for log in logs if log.get(ISSUE_KEY)]
            for issue_message in issues:
                print("Issue at", issue_message)
        else:
            # Show help message of found issues
            print(
                f"[WARNING] Found {counts[ISSUE_KEY]} issues with logs."
                " To show all logs with issues, please provide"
                f" '{ARG_SHOW_LINES_WITH_ISSUES}' argument."
            )
    else:
        if do_show_issues:
            # No issues found message
            print()
            print("There were no issues with your logs.")


@catch_error
def main():
    """
    Main entry point for the log analyzer CLI.

    - Parses input arguments.
    - Loads logs from the specified file.
    - Displays summary statistics and potential issues.
    - If a log level is specified, displays detailed logs for that level.
    """
    # Parse input arguments
    file_path, log_level, do_show_issues, do_issue_unknown_levels = handle_input_args()

    # Load logs from a file
    logs = load_logs(file_path, do_issue_unknown_levels)

    # Count logs by their level
    counts = count_logs_by_level(logs)

    # Display log statistics
    display_log_counts(counts)

    # Check and display potential log issues
    handle_log_issues(logs, counts, do_show_issues)

    # If a log level was provided, filter and display matching logs details
    if log_level:
        filtered_logs = filter_logs_by_level(logs, log_level)
        display_log_details(filtered_logs, level=log_level)


if __name__ == "__main__":
    main()

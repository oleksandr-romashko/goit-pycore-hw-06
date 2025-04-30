"""
Validators for contact management commands.

Each function validates input arguments or contact data before executing a command.
Validators raise ValidationError with descriptive messages if validation fails.
"""
import re

from utils.constants import NAME_MIN_LENGTH, NAME_MAX_LENGTH, PHONE_FORMAT_DESC_STR
from utils.text_utils import truncate_string

from validators.errors import ValidationError


def validate_are_two_arguments(args: list[str], _) -> None:
    """
    Ensures two non-empty arguments are provided: username and phone number.

    Args:
        args (list[str]): args[0] = username, args[1] = phone number.
        _ (Any): Placeholder for contacts dictionary, unused here.

    Raises:
        ValidationError: If arguments are missing or empty.
    """
    if len(args) != 2 or len(args[0].strip()) == 0 or len(args[1].strip()) == 0:
        raise ValidationError(
            "You must provide two arguments, username and a phone number."
        )


def validate_is_one_argument_username(args: list[str], _) -> None:
    """
    Ensures a single non-empty argument (username) is provided.

    Args:
        args (list[str]): args[0] = username.
        _ (Any): Placeholder for contacts dictionary, unused here.

    Raises:
        ValidationError: If username is missing or empty.
    """
    if len(args) != 1 or len(args[0].strip()) == 0:
        raise ValidationError("You must provide username as a single argument.")


def validate_contact_not_in_contacts(args: list[str], contacts: dict) -> None:
    """
    Ensures the contact with the given username does not already exist (case-insensitive).

    Args:
        args (list[str]): args[0] = username to be checked.
        contacts (dict): Existing contacts dictionary.

    Raises:
        ValidationError: If contact already exists.
    """
    username = args[0]

    # Check for exact match (avoid unnecessary iteration if an exact match is found early)
    if username in contacts:
        raise ValidationError(f"Contact with username '{username}' already exists.")

    # Check for case-insensitive match
    for existing_username in contacts:
        if existing_username.lower() == username.lower():
            raise ValidationError(
                f"Contact with username '{username}' already exists, "
                f"but under a different name: '{existing_username}'."
            )


def validate_contacts_not_empty(_, contacts: dict) -> None:
    """
    Ensures there is at least one contact in the list.

    Args:
        _ (Any): Placeholder for args, not used.
        contacts (dict): Contacts dictionary.

    Raises:
        ValidationError: If no contacts exist.
    """
    if not contacts:
        raise ValidationError(
            "You don't have any contacts yet, but you can add one anytime."
        )


def validate_contact_name_exists(args: list[str], contacts: dict) -> None:
    """
    Ensures a contact with the provided username exists, case-insensitively.

    Args:
        args (list[str]): args[0] = username.
        contacts (dict): Contacts dictionary.

    Raises:
        ValidationError: If contact doesn't exist or name differs by case.
    """
    username = args[0]

    # Check case-insensitive match by converting both stored and input names to lowercase
    match = None
    for contact in contacts:
        if contact.lower() == username.lower():
            match = contact
            break

    if not match:
        raise ValidationError(f"Contact '{username}' not found.")

    # If there's a match with a different case, let the user know
    if match != username:
        raise ValidationError(
            f"Contact '{username}' not found, "
            f"but a contact exists under '{match}'. "
            f"Did you mean '{match}'?"
        )


def validate_contact_username_length(args: list[str], _) -> None:
    """
    Validates username against minimum and maximum allowed lengths.

    Args:
        args (list[str]): args[0] = username.
        _ (Any): Placeholder for contacts dictionary, unused.

    Raises:
        ValidationError: If username is too short or too long.
    """
    username = args[0]

    if len(username) < NAME_MIN_LENGTH:
        message_too_short = (
            f"Username '{username}' is too short "
            f"and should have at least {NAME_MIN_LENGTH} symbols."
        )
        raise ValidationError(message_too_short)

    if len(username) > NAME_MAX_LENGTH:
        truncated_username = truncate_string(
            username, max_length=15, include_suffix_in_max_length=True
        )
        message_too_long = (
            f"Username'{truncated_username}' is too long "
            f"and should have not more than {NAME_MAX_LENGTH} symbols."
        )
        raise ValidationError(message_too_long)


def validate_not_phone_duplicate(args: list[str], contacts: dict) -> None:
    """
    Ensures the new phone number is different from the existing one.

    Args:
        args (list[str]): args[0] = username, args[1] = new phone number.
        contacts (dict): Contacts dictionary.

    Raises:
        ValidationError: If phone number hasn't changed.
    """
    username, phone = args
    if contacts[username] == phone:
        raise ValidationError(f"Contact '{username}' has this phone number already.")


def validate_phone_number(args: list[str], _) -> None:
    """
    Validates phone number format: 10 digits, optionally prefixed with '+'.

    Args:
        args (list[str]): args[1] = phone number.
        _ (Any): Placeholder for contacts dictionary, unused.

    Raises:
        ValidationError: If phone number format is invalid.
    """
    phone = args[1]
    # Remove all non-digit characters for counting digits
    digits_only = re.sub(r"\D", "", phone)

    if not len(digits_only) == 10:
        raise ValidationError(
            f"Invalid phone number '{phone}'. Expected {PHONE_FORMAT_DESC_STR}."
        )

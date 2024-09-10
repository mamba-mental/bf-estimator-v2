# --- Beginning of File ---
# user_interaction.py
# Author: Tiran Ronelle Winston
# Created: September 10, 2024
# Last Modified: September 10, 2024
# Description: This script provides utility functions to interact with the user via command line inputs. 
#              It includes methods for obtaining validated inputs of different types, such as floats, integers, 
#              experience levels, dates, yes/no responses, and choices from a list.
# Usage: Import this module into your main program to utilize the input validation functions. 
#        Example: `from user_interaction import get_float_input`
# Dependencies: Python's built-in `input` function, `datetime` module
# Version: 1.0.0
# License: Apache License 2.0
# --- End of Header ---

import datetime

def get_float_input(prompt):
    """
    Prompts the user to input a floating-point number.
    Repeatedly requests input until the user enters a valid float.

    Args:
        prompt (str): The prompt message displayed to the user.

    Returns:
        float: The validated floating-point number input by the user.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            # If the input cannot be converted to a float, print an error message and retry.
            print("Invalid input. Please enter a valid float.")

def get_int_input(prompt):
    """
    Prompts the user to input an integer.
    Repeatedly requests input until the user enters a valid integer.

    Args:
        prompt (str): The prompt message displayed to the user.

    Returns:
        int: The validated integer input by the user.
    """
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            # If the input cannot be converted to an integer, print an error message and retry.
            print("Invalid input. Please enter a valid integer.")

def get_experience_level_input(prompt):
    """
    Prompts the user to select their experience level from predefined categories.
    Repeatedly requests input until the user selects a valid option.

    Args:
        prompt (str): The prompt message displayed to the user.

    Returns:
        str: The description of the selected experience level.
    """
    print(prompt)
    levels = [
        ("1", "Beginner (0-1 year)"),
        ("2", "Novice (1-2 years)"),
        ("3", "Intermediate (2-4 years)"),
        ("4", "Advanced (4-10 years)"),
        ("5", "Elite (10+ years)")
    ]
    # Display the experience level options to the user.
    for idx, (level, description) in enumerate(levels, 1):
        print(f"{idx}. {description}")
    while True:
        try:
            choice = int(input("Choose an option: ").strip())
            if 1 <= choice <= len(levels):
                return levels[choice - 1][1]
            else:
                # Print an error message if the input is not within the valid range.
                print(f"Invalid input. Please enter a number between 1 and {len(levels)}.")
        except ValueError:
            # Print an error message if the input is not an integer.
            print(f"Invalid input. Please enter a number between 1 and {len(levels)}.")

def get_date_input(prompt):
    """
    Prompts the user to input a date in the MMDDYY format.
    Repeatedly requests input until the user enters a valid date.

    Args:
        prompt (str): The prompt message displayed to the user.

    Returns:
        datetime.datetime: The validated date input by the user.
    """
    while True:
        try:
            return datetime.datetime.strptime(input(prompt), "%m%d%y")
        except ValueError:
            # If the input cannot be parsed as a date, print an error message and retry.
            print("Invalid input. Please enter a valid date in the format MMDDYY (e.g., 091524 for September 15, 2024).")

def get_yes_no_input(prompt):
    """
    Prompts the user for a yes/no input.
    Repeatedly requests input until the user enters 'y' or 'n'.

    Args:
        prompt (str): The prompt message displayed to the user.

    Returns:
        bool: True if the user inputs 'y', False if the user inputs 'n'.
    """
    while True:
        response = input(prompt).strip().lower()
        if response in ['y', 'n']:
            return response == 'y'
        else:
            # Print an error message if the input is not 'y' or 'n'.
            print("Invalid input. Please enter 'Y' for Yes or 'N' for No.")

def get_choice_input(prompt, choices_descriptions):
    """
    Prompts the user to select an option from a list of choices.
    Repeatedly requests input until the user selects a valid option.

    Args:
        prompt (str): The prompt message displayed to the user.
        choices_descriptions (list): A list of tuples, where each tuple contains a choice identifier and its description.

    Returns:
        str: The identifier of the selected choice.
    """
    print(prompt)
    # Display the available choices to the user.
    for idx, (choice, description) in enumerate(choices_descriptions, 1):
        print(f"{idx}. {choice} - {description}")
    while True:
        try:
            choice = int(input("Choose an option: ").strip())
            if 1 <= choice <= len(choices_descriptions):
                return choices_descriptions[choice - 1][0]
            else:
                # Print an error message if the input is not within the valid range.
                print(f"Invalid input. Please enter a number between 1 and {len(choices_descriptions)}.")
        except ValueError:
            # Print an error message if the input is not an integer.
            print(f"Invalid input. Please enter a number between 1 and {len(choices_descriptions)}.")

# --- Footer ---
# Status: Development
# Contact: mambamental3mil@gmail.com
# © 2024 Mamba Matrix Solutions LLC. All rights reserved.
# --- End of File ---

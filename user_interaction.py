import datetime

def get_float_input(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid float.")

def get_int_input(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def get_experience_level_input(prompt):
    print(prompt)
    levels = [
        ("1", "Beginner (0-1 year)"),
        ("2", "Novice (1-2 years)"),
        ("3", "Intermediate (2-4 years)"),
        ("4", "Advanced (4-10 years)"),
        ("5", "Elite (10+ years)")
    ]
    for idx, (level, description) in enumerate(levels, 1):
        print(f"{idx}. {description}")
    while True:
        try:
            choice = int(input("Choose an option: ").strip())
            if 1 <= choice <= len(levels):
                return levels[choice - 1][1]
            else:
                print(f"Invalid input. Please enter a number between 1 and {len(levels)}.")
        except ValueError:
            print(f"Invalid input. Please enter a number between 1 and {len(levels)}.")

def get_date_input(prompt):
    while True:
        try:
            return datetime.datetime.strptime(input(prompt), "%m%d%y")
        except ValueError:
            print("Invalid input. Please enter a valid date in the format MMDDYY (e.g., 091524 for September 15, 2024).")

def get_yes_no_input(prompt):
    while True:
        response = input(prompt).strip().lower()
        if response in ['y', 'n']:
            return response == 'y'
        else:
            print("Invalid input. Please enter 'Y' for Yes or 'N' for No.")

def get_choice_input(prompt, choices_descriptions):
    print(prompt)
    for idx, (choice, description) in enumerate(choices_descriptions, 1):
        print(f"{idx}. {choice} - {description}")
    while True:
        try:
            choice = int(input("Choose an option: ").strip())
            if 1 <= choice <= len(choices_descriptions):
                return choices_descriptions[choice - 1][0]
            else:
                print(f"Invalid input. Please enter a number between 1 and {len(choices_descriptions)}.")
        except ValueError:
            print(f"Invalid input. Please enter a number between 1 and {len(choices_descriptions)}.")

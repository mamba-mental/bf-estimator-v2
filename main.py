# main.py
# --- Beginning of File ---
# main.py
# Author: Tiran Ronelle Winston
# Created: 09/08/24
# Last Modified: 09/11/24
# Description: This script serves as the main entry point for the Weight Loss Predictor program. It handles user interaction, processes data inputs, and generates predictions for weight loss progressions based on various fitness and health parameters. The program can run in test mode using predefined test data or interactively gather user inputs for predictions.
# Usage: Run this script directly to start the Weight Loss Predictor. Use the '--test' flag to run with test data instead of interactive user input.
# Dependencies: Requires the following modules: calculations, report_generation, test_data, user_interaction, utils, os, sys, datetime, warnings, contextlib, logging
# Version: 1.2.2
# License: Apache License 2.0
# --- End of Header ---

from calculations import (
    calculate_lean_mass_preservation_scores, calculate_tdee,
    calculate_metabolic_adaptation, distribute_weight_loss,
    calculate_weekly_caloric_output, calculate_initial_daily_calories,
    predict_weight_loss)
from report_generation import print_summary, generate_comprehensive_report, save_report
from test_data import TEST_DATA
from user_interaction import (
    get_float_input, get_int_input, get_experience_level_input,
    get_date_input, get_yes_no_input, get_choice_input
)
from utils import calculate_age
import os
import sys
from datetime import datetime
import warnings
from contextlib import contextmanager
import logging

# Setup logging for debugging and tracking program execution.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Suppress specific warnings from WeasyPrint library to avoid cluttering the output.
warnings.filterwarnings("ignore", category=UserWarning, module="weasyprint")

# Suppress GLib-GIO warnings and stderr globally to prevent unnecessary warnings during execution.
os.environ['G_MESSAGES_DEBUG'] = 'none'
os.environ['G_DEBUG'] = 'fatal-warnings'

# Set environment variables for WeasyPrint and GTK libraries.
os.environ['GIO_USE_VFS'] = 'local'
os.environ['GDK_BACKEND'] = 'x11'

# Set the path for the GTK binary files.
gtk_bin_path = r"C:\\Program Files\\GTK3-Runtime Win64\\bin"
os.environ["PATH"] += os.pathsep + gtk_bin_path

@contextmanager
def suppress_stderr():
    """
    Context manager to suppress stderr output.
    This is useful to hide unwanted error messages from libraries during execution.
    """
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

def run_user_interaction(use_test_data=False, user_data=None):
    """
    Runs the main interaction loop with the user. Can either use predefined test data
    or interactively gather data from the user.

    :param use_test_data: Boolean indicating whether to use test data.
    :param user_data: Dictionary of user data if provided directly.
    :return: Tuple containing the predicted weight loss progression and initial data dictionary.
    """
    logger.debug(f"Running user interaction with use_test_data={use_test_data}, user_data={user_data}")
    
    if use_test_data:
        return process_test_data(TEST_DATA)
    elif user_data:
        return process_test_data(user_data)

    print("Welcome to the Weight Loss Predictor!")

    # Gather user input for various fitness and health parameters.
    name = input("Enter your name: ")
    current_weight = get_float_input("Enter your current weight in lbs: ")
    current_bf = get_float_input("Enter your current body fat percentage: ")
    goal_weight = get_float_input("Enter your goal weight in lbs: ")
    goal_bf = get_float_input("Enter your goal body fat percentage: ")
    start_date = get_date_input("Enter your start date (MMDDYY): ")
    end_date = get_date_input("Enter your end date (MMDDYY): ")
    dob = get_date_input("Enter your date of birth (MMDDYY): ")
    gender = input("Enter your gender (m/f): ").strip().lower()
    height_feet = get_int_input("Enter your height (feet): ")
    height_inches = get_int_input("Enter your height (inches): ")
    height_cm = (height_feet * 12 + height_inches) * 2.54
    protein_intake = get_float_input("Enter your daily protein intake in grams: ")
    activity_level = get_choice_input("Enter your activity level (1-5):", [
        ("1", "Little to no exercise"),
        ("2", "Light exercise/sports 1-3 days/week"),
        ("3", "Moderate exercise/sports 3-5 days/week"),
        ("4", "Hard exercise/sports 6-7 days a week"),
        ("5", "Very hard exercise/sports & a physical job")
    ])
    resistance_training = get_yes_no_input("Are you doing resistance training? (Y/N): ")
    is_athlete = get_yes_no_input("Are you an athlete? (Y/N): ")
    workout_type = get_choice_input("What type of workouts do you primarily do?", [
        ("1", "Bodybuilding (Strength training and muscle building)"),
        ("2", "Cardio (Cardiovascular exercises like running or cycling)"),
        ("3", "General Fitness (A mix of different exercises for overall health)")
    ])
    workout_days = get_int_input("How many days per week do you work out? ")
    job_activity = get_choice_input("Select your job activity level:", [
        ("sedentary", "Mostly sitting (e.g., desk job)"),
        ("light", "Light activity (e.g., teacher, salesperson)"),
        ("moderate", "Moderate activity (e.g., construction worker)"),
        ("active", "Very active (e.g., courier, agriculture)")
    ])
    leisure_activity = get_choice_input("Select your leisure activity level:", [
        ("sedentary", "Little to no physical activity"),
        ("light", "Light physical activity (e.g., walking, gardening)"),
        ("moderate", "Moderate physical activity (e.g., hiking, dancing)"),
        ("active", "High physical activity (e.g., sports, intense exercise)")
    ])
    experience_level = get_experience_level_input("Enter your experience level (1-5):")

    # Calculate lean mass preservation scores based on user's workout frequency, type, and experience level.
    # Assuming workout_type[0] is the code as string
    workout_type_code = int(workout_type[0])
    volume_score, intensity_score, frequency_score = calculate_lean_mass_preservation_scores(workout_days, workout_type_code)

    # Determine if the user can be classified as a bodybuilder based on workout type and experience level.
    is_bodybuilder = workout_type_code == 1 and experience_level in ['Intermediate (2-4 years)', 'Advanced (4-10 years)', 'Elite (10+ years)']

    # Prepare initial data dictionary to store all gathered inputs and calculated scores.
    initial_data = {
        'name': name,
        'current_weight': current_weight,
        'current_bf': current_bf,
        'goal_weight': goal_weight,
        'goal_bf': goal_bf,
        'start_date': start_date,
        'end_date': end_date,
        'dob': dob,
        'gender': gender,
        'height_feet': height_feet,
        'height_inches': height_inches,
        'height_cm': height_cm,
        'protein_intake': protein_intake,
        'activity_level': int(activity_level[0]),
        'resistance_training': resistance_training == 'y',
        'is_athlete': is_athlete == 'y',
        'workout_type': workout_type_code,
        'workout_days': workout_days,
        'job_activity': job_activity,
        'leisure_activity': leisure_activity,
        'experience_level': experience_level,
        'volume_score': volume_score,
        'intensity_score': intensity_score,
        'frequency_score': frequency_score,
        'is_bodybuilder': is_bodybuilder
    }

    # Add a description for the activity level based on the chosen level.
    initial_data['activity_level_description'] = get_activity_level_description(initial_data['activity_level'])

    logger.debug(f"Initial data prepared: {initial_data}")

    # Predict weight loss progression using the gathered and processed data.
    progression = predict_weight_loss(
        current_weight, current_bf, goal_weight, goal_bf, start_date, end_date,
        dob, gender, initial_data['activity_level'], height_cm, is_athlete, resistance_training,
        protein_intake, volume_score, intensity_score, frequency_score, job_activity,
        leisure_activity, experience_level, is_bodybuilder
    )

    logger.debug(f"Prediction completed. Progression length: {len(progression)}")

    return progression, initial_data

def process_test_data(data):
    logger.debug(f"Processing test data: {data}")
    
    # Map workout types
    workout_type_map = {1: "Bodybuilding", 2: "Cardio", 3: "General Fitness"}
    workout_type_code = data['workout_type']  # Assuming TEST_DATA uses integer codes
    
    # Calculate lean mass preservation scores
    volume_score, intensity_score, frequency_score = calculate_lean_mass_preservation_scores(
        data['workout_days'], workout_type_code)

    # Map experience levels
    experience_level_map = {1: "Beginner (0-1 year)", 2: "Novice (1-2 years)", 
                            3: "Intermediate (2-4 years)", 4: "Advanced (4-10 years)", 
                            5: "Elite (10+ years)"}
    experience_level = experience_level_map.get(data['experience_level'], data['experience_level'])

    # Determine if the user is a bodybuilder
    is_bodybuilder = workout_type_code == 1 and experience_level in [
        'Intermediate (2-4 years)', 'Advanced (4-10 years)', 'Elite (10+ years)']

    # Convert height to centimeters
    height_cm = (data['height_feet'] * 12 + data['height_inches']) * 2.54

    # Helper function to handle both string and datetime objects
    def parse_date(date_value):
        if isinstance(date_value, datetime):
            return date_value
        return datetime.strptime(date_value, "%m%d%y")

    # Prepare processed data dictionary
    processed_data = {
        'name': data['name'],
        'current_weight': data['current_weight'],
        'current_bf': data['current_bf'],
        'goal_weight': data['goal_weight'],
        'goal_bf': data['goal_bf'],
        'start_date': parse_date(data['start_date']),
        'end_date': parse_date(data['end_date']),
        'dob': parse_date(data['dob']),
        'gender': data['gender'],
        'height_feet': data['height_feet'],
        'height_inches': data['height_inches'],
        'height_cm': height_cm,
        'protein_intake': data['protein_intake'],
        'activity_level': int(data['activity_level']),
        'resistance_training': data['resistance_training'],
        'is_athlete': data['is_athlete'],
        'workout_type': workout_type_code,
        'workout_days': data['workout_days'],
        'job_activity': data['job_activity'],
        'leisure_activity': data['leisure_activity'],
        'experience_level': experience_level,
        'volume_score': volume_score,
        'intensity_score': intensity_score,
        'frequency_score': frequency_score,
        'is_bodybuilder': is_bodybuilder
    }

    # Add activity level description
    processed_data['activity_level_description'] = get_activity_level_description(processed_data['activity_level'])

    logger.debug(f"Processed data: {processed_data}")

    # Predict weight loss progression
    progression = predict_weight_loss(
        processed_data['current_weight'], processed_data['current_bf'],
        processed_data['goal_weight'], processed_data['goal_bf'],
        processed_data['start_date'], processed_data['end_date'],
        processed_data['dob'], processed_data['gender'],
        processed_data['activity_level'], processed_data['height_cm'],
        processed_data['is_athlete'], processed_data['resistance_training'],
        processed_data['protein_intake'], processed_data['volume_score'],
        processed_data['intensity_score'], processed_data['frequency_score'],
        processed_data['job_activity'], processed_data['leisure_activity'],
        processed_data['experience_level'], processed_data['is_bodybuilder']
    )

    logger.debug(f"Prediction completed. Progression length: {len(progression)}")

    return progression, processed_data

def get_activity_level_description(activity_level):
    """
    Provides a description for a given activity level code.

    :param activity_level: Numeric code representing the activity level.
    :return: String description of the activity level.
    """
    activity_levels = {
        1: "Little to no exercise",
        2: "Light exercise/sports 1-3 days/week",
        3: "Moderate exercise/sports 3-5 days/week",
        4: "Hard exercise/sports 6-7 days a week",
        5: "Very hard exercise/sports & a physical job"
    }
    return activity_levels.get(int(activity_level), "Unknown")

def main():
    """
    Main function that initializes the program, suppresses unwanted stderr output,
    and manages the execution flow based on user input or test mode.
    """
    with suppress_stderr():
        # Check if test mode is activated using command-line arguments.
        use_test_data = '--test' in sys.argv
        progression, initial_data = run_user_interaction(use_test_data=use_test_data)
        
        # Print summary of results to the user and capture saved file paths.
        saved_files = print_summary(progression, initial_data)
        
        # Handle the saved_files as needed.
        if saved_files:
            if 'markdown' in saved_files:
                logger.info(f"Markdown report available at: {saved_files['markdown']}")
            if 'pdf' in saved_files:
                logger.info(f"PDF report available at: {saved_files['pdf']}")
            if 'pdf_error' in saved_files:
                logger.error(f"Failed to generate PDF report: {saved_files['pdf_error']}")
        else:
            logger.info("No reports were saved.")

if __name__ == "__main__":
    main()

# --- Footer ---
# Status of last Update: Added activity_level_description to processed_data in process_test_data function
# Contact: mambamental3mil@gmail.com
# © 2024 Mamba Matrix Solutions LLC. All rights reserved.
# --- End of File ---

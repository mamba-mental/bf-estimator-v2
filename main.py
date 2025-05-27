# main.py
# --- Beginning of File ---
# main.py
# Author: Tiran Ronelle Winston
# Created: 09/08/24
# Last Modified: 01/25/25
# Description: This script serves as the main entry point for the Weight Loss Predictor program. It handles user interaction, processes data inputs, and generates predictions for weight loss progressions based on various fitness and health parameters. The program can run in test mode using predefined test data or interactively gather user inputs for predictions.
# Usage: Run this script directly to start the Weight Loss Predictor. Use the '--test' flag to run with test data instead of interactive user input.
# Dependencies: Requires the following modules: calculations, report_generation, test_data, user_interaction, utils, os, sys, datetime, warnings, contextlib, logging
# Version: 1.2.5
# License: Apache License 2.0
# --- End of Header ---
import sys
sys.path.append(r"Z:\2024.0917 - Bf-estimator-v2\122924_bf-estimator-terminal\new_prime_python_code")
from new_prime_python_code.PRIME_Calculations import predict_weight_loss, calculate_lean_mass_preservation_scores
from new_prime_python_code.PRIME_Utils import calculate_rmr, calculate_tdee, calculate_age
from new_prime_python_code.PRIME_Diet_Calculations_v2 import calculate_weekly_rate_of_fat_loss, calculate_weekly_muscle_gain
from new_prime_python_code.PRIME_Report_Generator_v3 import generate_prime_report_terminal

# from calculations import (
#     calculate_lean_mass_preservation_scores, calculate_tdee,
#     calculate_metabolic_adaptation, distribute_weight_loss,
#     calculate_weekly_caloric_output, calculate_initial_daily_calories,
#     predict_weight_loss)
# from report_generation import print_summary, generate_comprehensive_report, save_report
from test_data import TEST_DATA
from user_interaction import (
    get_float_input, get_int_input, get_experience_level_input,
    get_date_input, get_yes_no_input, get_choice_input
)
# from utils import calculate_age
import os
import sys
from datetime import datetime
import warnings
from contextlib import contextmanager
import logging

# Setup logging for debugging and tracking program execution.
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

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
    Handle user interaction for data input.
    """
    # Gather user input for various fitness and health parameters.
    print("Welcome to the Weight Loss Predictor!")
    print("=====================================")
    print("Please enter your information below:")
    print()
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
    diet_type = input("Enter diet type (keto, high_protein, balanced, high_carb): ").strip().lower()
    ped_use = input("PED use? (y/n): ").strip().lower() == 'y'
    exercise_type = input("Exercise type (resistance, cardio, hiit): ").strip().lower()
    sleep_quality = input("Sleep quality (good/poor): ").strip().lower()
    workout_type_choice = get_choice_input("What type of workouts do you primarily do?", [
        ("1", "Bodybuilding (Strength training and muscle building)"),
        ("2", "Cardio (Cardiovascular exercises like running or cycling)"),
        ("3", "General Fitness (A mix of different exercises for overall health)")
    ])
    workout_days = get_int_input("How many days per week do you work out? ")

    # Update job_activity and leisure_activity to extract the key
    job_activity_choice = get_choice_input("Select your job activity level:", [
        ("1", "Mostly sitting (e.g., desk job)"),
        ("2", "Light activity (e.g., teacher, salesperson)"),
        ("3", "Moderate activity (e.g., construction worker)"),
        ("4", "Very active (e.g., courier, agriculture)")
    ])
    job_activity = int(job_activity_choice[0])  # Convert to integer

    leisure_activity_choice = get_choice_input("Select your leisure activity level:", [
        ("1", "Little to no physical activity"),
        ("2", "Light physical activity (e.g., walking, gardening)"),
        ("3", "Moderate physical activity (e.g., hiking, dancing)"),
        ("4", "High physical activity (e.g., sports, intense exercise)")
    ])
    leisure_activity = int(leisure_activity_choice[0])  # Convert to integer

    # Get experience level as a tuple (code, description)
    experience_level_choice = get_experience_level_input("Enter your experience level (1-5):")
    experience_level_code = int(experience_level_choice[0])
    experience_level_str = experience_level_choice[1]

    # Map workout type codes to strings
    workout_type_map = {
        1: "Bodybuilding",
        2: "Cardio",
        3: "General Fitness"
    }
    workout_type_code = int(workout_type_choice[0])
    workout_type_str = workout_type_map.get(workout_type_code)
    if workout_type_str is None:
        raise ValueError("Invalid workout type code.")

    # Calculate lean mass preservation scores based on user's workout frequency, type, and experience level.
    volume_score, intensity_score, frequency_score = calculate_lean_mass_preservation_scores(workout_days, workout_type_str)

    # Determine if the user can be classified as a bodybuilder based on workout type and experience level.
    is_bodybuilder = workout_type_str == "Bodybuilding" and experience_level_str in ['Intermediate (2-4 years)', 'Advanced (4-10 years)', 'Elite (10+ years)']

    # Calculate age from date of birth
    age = calculate_age(dob, start_date)

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
        'age': age,
        'gender': gender,
        'height_feet': height_feet,
        'height_inches': height_inches,
        'height_cm': height_cm,
        'protein_intake': protein_intake,
        'activity_level': int(activity_level[0]),
        'resistance_training': resistance_training,
        'is_athlete': is_athlete,
        'workout_type': workout_type_str,
        'workout_days': workout_days,
        'job_activity': job_activity,
        'leisure_activity': leisure_activity,
        'experience_level': experience_level_str,
        'volume_score': volume_score,
        'intensity_score': intensity_score,
        'frequency_score': frequency_score,
        'is_bodybuilder': is_bodybuilder
    }

    # Add a description for the activity level based on the chosen level.
    initial_data['activity_level_description'] = get_activity_level_description(initial_data['activity_level'])

    logger.debug(f"Initial data prepared: {initial_data}")

    # Map activity level to string
    activity_level_map = {
        1: "sedentary",
        2: "light",
        3: "moderate",
        4: "active",
        5: "very active"
    }
    activity_level_str = activity_level_map.get(initial_data['activity_level'], "moderate")
    
    # Map job and leisure activity to strings
    job_activity_map = {1: "sedentary", 2: "light", 3: "moderate", 4: "active"}
    leisure_activity_map = {1: "sedentary", 2: "light", 3: "moderate", 4: "active"}
    job_activity_str = job_activity_map.get(job_activity, "light")
    leisure_activity_str = leisure_activity_map.get(leisure_activity, "light")
    
    # Predict weight loss progression using the gathered and processed data.
    progression = predict_weight_loss(
        current_weight=current_weight,
        current_bf=current_bf,
        goal_weight=goal_weight,
        goal_bf=goal_bf,
        start_date=start_date,
        end_date=end_date,
        dob=dob,
        gender=gender,
        activity_level=activity_level_str,
        height_cm=height_cm,
        is_athlete=initial_data['is_athlete'],
        daily_protein_intake=protein_intake,
        job_activity=job_activity_str,
        leisure_activity=leisure_activity_str,
        experience_level=initial_data['experience_level'],
        is_bodybuilder=is_bodybuilder,
        ped_use=ped_use,
        diet_type=diet_type,
        exercise_type=exercise_type,
        sleep_quality=sleep_quality
    )

    logger.debug(f"Prediction completed. Progression length: {len(progression)}")

    return progression, initial_data

def process_test_data(data):
    """
    Process test data for weight loss prediction.
    """
    logger.debug(f"Processing test data: {data}")

    # Map workout type codes to strings
    workout_type_map = {
        1: "Bodybuilding",
        2: "Cardio",
        3: "General Fitness"
    }

    # Get workout type string
    if isinstance(data['workout_type'], int):
        workout_type_str = workout_type_map.get(data['workout_type'])
        if workout_type_str is None:
            raise ValueError("Invalid workout type code in test data.")
    else:
        workout_type_str = data['workout_type']

    # Calculate lean mass preservation scores
    volume_score, intensity_score, frequency_score = calculate_lean_mass_preservation_scores(
        data['workout_days'], workout_type_str)

    # Map experience levels
    experience_level_map = {
        1: "Beginner (0-1 year)",
        2: "Novice (1-2 years)",
        3: "Intermediate (2-4 years)",
        4: "Advanced (4-10 years)",
        5: "Elite (10+ years)"
    }
    if isinstance(data['experience_level'], int):
        experience_level = experience_level_map.get(data['experience_level'], "Unknown")
    else:
        experience_level = data['experience_level']

    # Determine if the user is a bodybuilder
    is_bodybuilder = workout_type_str == "Bodybuilding" and experience_level in [
        'Intermediate (2-4 years)', 'Advanced (4-10 years)', 'Elite (10+ years)']

    # Convert height to centimeters
    height_cm = (data['height_feet'] * 12 + data['height_inches']) * 2.54

    # Helper function to handle both string and datetime objects
    def parse_date(date_value):
        if isinstance(date_value, datetime):
            return date_value
        return datetime.strptime(date_value, "%m%d%y")

    # Calculate age from date of birth
    start_date = parse_date(data['start_date'])
    dob = parse_date(data['dob'])
    age = calculate_age(dob, start_date)

    # Prepare processed data dictionary
    processed_data = {
        'name': data['name'],
        'current_weight': data['current_weight'],
        'current_bf': data['current_bf'],
        'goal_weight': data['goal_weight'],
        'goal_bf': data['goal_bf'],
        'start_date': start_date,
        'end_date': parse_date(data['end_date']),
        'dob': dob,
        'age': age,
        'gender': data['gender'],
        'height_feet': data['height_feet'],
        'height_inches': data['height_inches'],
        'height_cm': height_cm,
        'protein_intake': data['protein_intake'],
        'activity_level': int(data['activity_level']),
        'resistance_training': data['resistance_training'] == 'y' if isinstance(data['resistance_training'], str) else data['resistance_training'],
        'is_athlete': data['is_athlete'] == 'y' if isinstance(data['is_athlete'], str) else data['is_athlete'],
        'workout_type': workout_type_str,
        'workout_days': data['workout_days'],
        'job_activity': int(data['job_activity']) if isinstance(data['job_activity'], str) else data['job_activity'],
        'leisure_activity': int(data['leisure_activity']) if isinstance(data['leisure_activity'], str) else data['leisure_activity'],
        'experience_level': experience_level,
        'volume_score': volume_score,
        'intensity_score': intensity_score,
        'frequency_score': frequency_score,
        'is_bodybuilder': is_bodybuilder
    }

    # Add activity level description
    processed_data['activity_level_description'] = get_activity_level_description(processed_data['activity_level'])

    logger.debug(f"Processed data: {processed_data}")

    # Map activity level to string
    activity_level_map = {
        1: "sedentary",
        2: "light",
        3: "moderate",
        4: "active",
        5: "very active"
    }
    activity_level_str = activity_level_map.get(processed_data['activity_level'], "moderate")
    
    # Map job and leisure activity to strings
    job_activity_map = {1: "sedentary", 2: "light", 3: "moderate", 4: "active"}
    leisure_activity_map = {1: "sedentary", 2: "light", 3: "moderate", 4: "active"}
    job_activity_str = job_activity_map.get(processed_data['job_activity'], "light")
    leisure_activity_str = leisure_activity_map.get(processed_data['leisure_activity'], "light")
    
    # Get default values for new parameters
    diet_type = data.get('diet_type', 'balanced')
    ped_use = data.get('ped_use', False)
    exercise_type = data.get('exercise_type', 'resistance')
    sleep_quality = data.get('sleep_quality', 'good')
    
    # Predict weight loss progression
    progression = predict_weight_loss(
        current_weight=processed_data['current_weight'],
        current_bf=processed_data['current_bf'],
        goal_weight=processed_data['goal_weight'],
        goal_bf=processed_data['goal_bf'],
        start_date=processed_data['start_date'],
        end_date=processed_data['end_date'],
        dob=processed_data['dob'],
        gender=processed_data['gender'],
        activity_level=activity_level_str,
        height_cm=processed_data['height_cm'],
        is_athlete=processed_data['is_athlete'],
        daily_protein_intake=processed_data['protein_intake'],
        job_activity=job_activity_str,
        leisure_activity=leisure_activity_str,
        experience_level=processed_data['experience_level'],
        is_bodybuilder=processed_data['is_bodybuilder'],
        ped_use=ped_use,
        diet_type=diet_type,
        exercise_type=exercise_type,
        sleep_quality=sleep_quality
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
        if use_test_data:
            progression, initial_data = process_test_data(TEST_DATA)
        else:
            progression, initial_data = run_user_interaction()
        
        # Generate comprehensive PRIME report
        markdown_path, pdf_path = generate_prime_report_terminal(initial_data, progression)
        
        print(f"\n✅ Report Generation Complete!")
        print(f"📄 Markdown Report: {markdown_path}")
        if pdf_path:
            print(f"📋 PDF Report: {pdf_path}")
        else:
            print("⚠️  PDF generation failed - check dependencies")

if __name__ == "__main__":
    main()

# --- Footer ---
# Status: Development
# Contact: mambamental3mil@gmail.com
# © 2024 Mamba Matrix Solutions LLC. All rights reserved.
# --- End of File ---

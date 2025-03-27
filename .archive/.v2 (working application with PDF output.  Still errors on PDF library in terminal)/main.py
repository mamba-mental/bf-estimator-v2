# --- Beginning of File ---
# main.py
# Author: Tiran Ronelle Winston
# Created: 2024-09-10
# Last Modified: 2024-09-10
# Description: This script serves as the main entry point for the Weight Loss Predictor app. It interacts with the user to gather personal and fitness-related information, processes this data to predict weight loss progression, and generates a detailed report.
# Usage: Run this script to start the Weight Loss Predictor app. The script supports an optional '--test' flag to use predefined test data instead of user input.
# Dependencies: os, sys, datetime, weasyprint, mistune, calculations, user_interaction, report_generation, test_data, utils
# Version: 1.0.0
# License: Apache License 2.0
# --- End of Header ---

# Standard library imports
import os
import sys
from datetime import datetime
import warnings
from contextlib import contextmanager

# Suppress specific warnings from WeasyPrint
warnings.filterwarnings("ignore", category=UserWarning, module="weasyprint")

# Suppress GLib-GIO warnings and stderr globally
os.environ['G_MESSAGES_DEBUG'] = 'none'
os.environ['G_DEBUG'] = 'fatal-warnings'  # Attempt to further suppress warnings

# Set environment variables for WeasyPrint and GTK
os.environ['GIO_USE_VFS'] = 'local'
os.environ['GDK_BACKEND'] = 'x11'

# Set the GTK path
gtk_bin_path = r"C:\\Program Files\\GTK3-Runtime Win64\\bin"
os.environ["PATH"] += os.pathsep + gtk_bin_path

# Third-party imports
import mistune
import pdfkit
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

# Local application/library specific imports
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

@contextmanager
def suppress_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

def generate_pdf_report(report_data, pdf_file):
    """
    Generates a PDF report using Jinja2 template and pdfkit.

    Args:
    report_data (dict): The data to be used in the report template.
    pdf_file (str): The path where the PDF file will be saved.
    """
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('report-template.html')
    
    html_content = template.render(report_data)
    
    css_file = os.path.join('templates', 'report-template-styles.css')
    
    pdfkit.from_string(html_content, pdf_file, css=css_file)
    
    print(f"PDF report saved as {pdf_file}")

def run_user_interaction(use_test_data=False):
    """
    Handles user interaction to gather input data for weight loss prediction.

    Args:
    use_test_data (bool): If True, uses predefined test data instead of user input.

    Returns:
    tuple: A tuple containing the weight loss progression and initial user data.
    """
    if use_test_data:
        return TEST_DATA

    print("Welcome to the Weight Loss Predictor!")

    # Gather user input for various parameters
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
        ("Bodybuilding", "Strength training and muscle building"),
        ("Cardio", "Cardiovascular exercises like running or cycling"),
        ("General Fitness", "A mix of different exercises for overall health")
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
    name = input("Enter your name: ")

    # Calculate lean mass preservation scores
    volume_score, intensity_score, frequency_score = calculate_lean_mass_preservation_scores(workout_days, workout_type)

    # Determine if the user is a bodybuilder
    is_bodybuilder = workout_type == "Bodybuilding" and experience_level in ['Intermediate (2-4 years)', 'Advanced (4-10 years)', 'Elite (10+ years)']

    # Predict weight loss progression
    progression = predict_weight_loss(
        current_weight, current_bf, goal_weight, goal_bf, start_date, end_date,
        dob, gender, int(activity_level), height_cm, is_athlete, resistance_training,
        protein_intake, volume_score, intensity_score, frequency_score, job_activity,
        leisure_activity, experience_level, is_bodybuilder
    )

    # Prepare initial data dictionary
    initial_data = {
        'name': name,
        'dob': dob,
        'gender': gender,
        'height_feet': height_feet,
        'height_inches': height_inches,
        'height_cm': height_cm,
        'goal_weight': goal_weight,
        'goal_bf': goal_bf,
        'activity_level_description': ["Little to no exercise", "Light exercise/sports 1-3 days/week", "Moderate exercise/sports 3-5 days/week", "Hard exercise/sports 6-7 days a week", "Very hard exercise/sports & a physical job"][int(activity_level) - 1],
        'experience_level': experience_level,
        'protein_intake': protein_intake,
        'workout_type': workout_type,
        'workout_days': workout_days,
        'volume_score': volume_score,
        'intensity_score': intensity_score,
        'frequency_score': frequency_score,
        'resistance_training': resistance_training,
        'is_athlete': is_athlete,
        'job_activity': job_activity,
        'leisure_activity': leisure_activity,
        'is_bodybuilder': is_bodybuilder
    }

    return progression, initial_data

def process_test_data(test_data):
    """
    Processes test data to match predict_weight_loss parameters.

    Args:
    test_data (dict): Dictionary containing test data.

    Returns:
    dict: Processed test data ready for weight loss prediction.
    """
    # Map workout types
    workout_type_map = {1: "Bodybuilding", 2: "Cardio", 3: "General Fitness"}
    workout_type = workout_type_map.get(test_data['workout_type'], test_data['workout_type'])

    # Calculate lean mass preservation scores
    volume_score, intensity_score, frequency_score = calculate_lean_mass_preservation_scores(
        test_data['workout_days'], workout_type)

    # Map experience levels
    experience_level_map = {1: "Beginner (0-1 year)", 2: "Novice (1-2 years)", 
                            3: "Intermediate (2-4 years)", 4: "Advanced (4-10 years)", 
                            5: "Elite (10+ years)"}
    experience_level = experience_level_map.get(test_data['experience_level'], test_data['experience_level'])

    # Determine if the user is a bodybuilder
    is_bodybuilder = workout_type == "Bodybuilding" and experience_level in [
        'Intermediate (2-4 years)', 'Advanced (4-10 years)', 'Elite (10+ years)']

    # Map job and leisure activity levels
    job_activity_map = {1: "sedentary", 2: "light", 3: "moderate", 4: "active"}
    leisure_activity_map = {1: "sedentary", 2: "light", 3: "moderate", 4: "active"}

    # Convert height to centimeters
    height_cm = (test_data['height_feet'] * 12 + test_data['height_inches']) * 2.54

    # Prepare processed data dictionary
    processed_data = {
        'current_weight': test_data['current_weight'],
        'current_bf': test_data['current_bf'],
        'goal_weight': test_data['goal_weight'],
        'goal_bf': test_data['goal_bf'],
        'start_date': datetime.strptime(test_data['start_date'], "%m%d%y"),
        'end_date': datetime.strptime(test_data['end_date'], "%m%d%y"),
        'dob': datetime.strptime(test_data['dob'], "%m%d%y"),
        'gender': test_data['gender'],
        'activity_level': int(test_data['activity_level']),
        'height_cm': height_cm,
        'is_athlete': test_data['is_athlete'] == 'y',
        'resistance_training': test_data['resistance_training'] == 'y',
        'daily_protein_intake': test_data['protein_intake'],
        'volume_score': volume_score,
        'intensity_score': intensity_score,
        'frequency_score': frequency_score,
        'job_activity': job_activity_map.get(test_data['job_activity'], test_data['job_activity']),
        'leisure_activity': leisure_activity_map.get(test_data['leisure_activity'], test_data['leisure_activity']),
        'experience_level': experience_level,
        'is_bodybuilder': is_bodybuilder
    }

    return processed_data

def main():
    """
    Main function to run the Weight Loss Predictor application.
    """
    with suppress_stderr():
        # Check if test mode is activated
        use_test_data = '--test' in sys.argv
        if use_test_data:
            # Process test data
            test_data = run_user_interaction(use_test_data=True)
            processed_test_data = process_test_data(test_data)
            activity_level_description = [
                "Little to no exercise",
                "Light exercise/sports 1-3 days/week",
                "Moderate exercise/sports 3-5 days/week",
                "Hard exercise/sports 6-7 days a week",
                "Very hard exercise/sports & a physical job"
            ][int(test_data['activity_level']) - 1]
            initial_data = {
                **test_data, 
                'dob': processed_test_data['dob'], 
                'is_bodybuilder': processed_test_data['is_bodybuilder'],
                'height_cm': processed_test_data['height_cm'],
                'activity_level_description': activity_level_description,
                'volume_score': processed_test_data['volume_score'],
                'intensity_score': processed_test_data['intensity_score'],
                'frequency_score': processed_test_data['frequency_score'],
            }
            progression = predict_weight_loss(**processed_test_data)
        else:
            # Run normal user interaction
            progression, initial_data = run_user_interaction()
        
        # Print summary of results
        print_summary(progression, initial_data)

if __name__ == "__main__":
    main()

# --- Footer ---
# Status: Development
# Contact: mambamental3mil@gmail.com
# © 2024 Mamba Matrix Solutions LLC. All rights reserved.
# --- End of File ---
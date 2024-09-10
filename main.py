# --- Beginning of File ---
# main.py
# Author: [Author's Name]
# Created: September 10, 2024
# Last Modified: September 10, 2024
# Description: This script serves as the main entry point for a weight loss predictor program. It interacts with users to gather necessary inputs, calculates weight loss projections based on various factors, and provides a summary of the results.
# Usage: Run this script in a Python environment to start the weight loss prediction process. It prompts the user for information such as current weight, body fat percentage, and lifestyle details.
# Dependencies: user_interaction, calculations, report_generation, utils (Ensure these modules are available in the same directory or properly installed as packages)
# Version: 1.0.0
# License: Apache License 2.0
# --- End of Header ---

# Importing necessary functions from different modules to handle user input, perform calculations, and generate a summary report.
from user_interaction import (
    get_float_input, get_int_input, get_experience_level_input,
    get_date_input, get_yes_no_input, get_choice_input
)
from calculations import (
    calculate_lean_mass_preservation_scores, calculate_tdee,
    calculate_metabolic_adaptation, distribute_weight_loss,
    calculate_weekly_caloric_output, calculate_initial_daily_calories,
    predict_weight_loss
)
from report_generation import print_summary
from utils import calculate_age

# Function: run_user_interaction
# Purpose: This function handles the entire user interaction process. It collects various inputs from the user, calculates relevant metrics using the collected data, and then prepares the data for reporting.
def run_user_interaction():
    # Welcome message to the user
    print("Welcome to the Weight Loss Predictor!")
    
    # Collecting user's current weight in pounds
    current_weight = get_float_input("Enter your current weight in lbs: ")
    
    # Collecting user's current body fat percentage
    current_bf = get_float_input("Enter your current body fat percentage: ")
    
    # Collecting user's goal weight in pounds
    goal_weight = get_float_input("Enter your goal weight in lbs: ")
    
    # Collecting user's goal body fat percentage
    goal_bf = get_float_input("Enter your goal body fat percentage: ")
    
    # Collecting start and end dates for the weight loss program
    start_date = get_date_input("Enter your start date (MMDDYY): ")
    end_date = get_date_input("Enter your end date (MMDDYY): ")
    
    # Collecting user's date of birth for age calculation
    dob = get_date_input("Enter your date of birth (MMDDYY): ")
    
    # Collecting user's gender; 'm' for male, 'f' for female
    gender = input("Enter your gender (m/f): ").strip().lower()
    
    # Collecting user's height in feet and inches, converting to centimeters
    height_feet = get_int_input("Enter your height (feet): ")
    height_inches = get_int_input("Enter your height (inches): ")
    height_cm = (height_feet * 12 + height_inches) * 2.54  # Conversion to centimeters
    
    # Collecting user's daily protein intake in grams
    protein_intake = get_float_input("Enter your daily protein intake in grams: ")

    # Collecting user's activity level, offering a choice from 1 to 5
    activity_level = get_choice_input("Enter your activity level (1-5):", [
        ("1", "Little to no exercise"),
        ("2", "Light exercise/sports 1-3 days/week"),
        ("3", "Moderate exercise/sports 3-5 days/week"),
        ("4", "Hard exercise/sports 6-7 days a week"),
        ("5", "Very hard exercise/sports & a physical job")
    ])

    # Collecting yes/no input on whether the user is doing resistance training
    resistance_training = get_yes_no_input("Are you doing resistance training? (Y/N): ")
    
    # Collecting yes/no input on whether the user is an athlete
    is_athlete = get_yes_no_input("Are you an athlete? (Y/N): ")

    # Collecting user's primary workout type from given options
    workout_type = get_choice_input("What type of workouts do you primarily do?", [
        ("Bodybuilding", "Strength training and muscle building"),
        ("Cardio", "Cardiovascular exercises like running or cycling"),
        ("General Fitness", "A mix of different exercises for overall health")
    ])
    
    # Collecting number of workout days per week
    workout_days = get_int_input("How many days per week do you work out? ")

    # Collecting user's job activity level
    job_activity = get_choice_input("Select your job activity level:", [
        ("sedentary", "Mostly sitting (e.g., desk job)"),
        ("light", "Light activity (e.g., teacher, salesperson)"),
        ("moderate", "Moderate activity (e.g., construction worker)"),
        ("active", "Very active (e.g., courier, agriculture)")
    ])
    
    # Collecting user's leisure activity level
    leisure_activity = get_choice_input("Select your leisure activity level:", [
        ("sedentary", "Little to no physical activity"),
        ("light", "Light physical activity (e.g., walking, gardening)"),
        ("moderate", "Moderate physical activity (e.g., hiking, dancing)"),
        ("active", "High physical activity (e.g., sports, intense exercise)")
    ])

    # Collecting user's experience level in physical activities
    experience_level = get_experience_level_input("Enter your experience level (1-5):")

    # Calculating lean mass preservation scores based on workout details
    volume_score, intensity_score, frequency_score = calculate_lean_mass_preservation_scores(workout_days, workout_type)
    
    # Determining if the user is classified as a bodybuilder based on workout type and experience level
    is_bodybuilder = workout_type == "Bodybuilding" and experience_level in ['Intermediate (2-4 years)', 'Advanced (4-10 years)', 'Elite (10+ years)']

    # Predicting weight loss progression based on all collected data
    progression = predict_weight_loss(
        current_weight, current_bf, goal_weight, goal_bf, start_date, end_date,
        dob, gender, int(activity_level), height_cm, is_athlete, resistance_training,
        protein_intake, volume_score, intensity_score, frequency_score, job_activity,
        leisure_activity, experience_level, is_bodybuilder
    )

    # Preparing initial data dictionary for summary report generation
    initial_data = {
        'name': input("Enter your name: "),  # Collecting user's name
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

    # Returning the calculated progression and initial data for further processing
    return progression, initial_data

# Main script execution
if __name__ == "__main__":
    # Running user interaction and collecting results
    progression, initial_data = run_user_interaction()
    
    # Printing a summary report based on the user's input and calculated progression
    print_summary(progression, initial_data)

# --- Footer ---
# Status: Development
# Contact: mambamental3mil@gmail.com
# © 2024 Mamba Matrix Solutions LLC. All rights reserved.
# --- End of File ---

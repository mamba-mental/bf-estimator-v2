# main.py
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

def run_user_interaction():
    print("Welcome to the Weight Loss Predictor!")
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

    volume_score, intensity_score, frequency_score = calculate_lean_mass_preservation_scores(workout_days, workout_type)
    is_bodybuilder = workout_type == "Bodybuilding" and experience_level in ['Intermediate (2-4 years)', 'Advanced (4-10 years)', 'Elite (10+ years)']

    progression = predict_weight_loss(
        current_weight, current_bf, goal_weight, goal_bf, start_date, end_date,
        dob, gender, int(activity_level), height_cm, is_athlete, resistance_training,
        protein_intake, volume_score, intensity_score, frequency_score, job_activity,
        leisure_activity, experience_level, is_bodybuilder
    )

    initial_data = {
        'name': input("Enter your name: "),  # Add this line to get the user's name
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

if __name__ == "__main__":
    progression, initial_data = run_user_interaction()
    print_summary(progression, initial_data)
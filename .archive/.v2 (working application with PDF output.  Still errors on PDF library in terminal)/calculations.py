# --- Beginning of File ---
# calculations.py
# Author: [Your Name]
# Created: September 10, 2024
# Last Modified: September 10, 2024
# Description: This module provides various functions for calculating fitness and nutritional metrics, including muscle gain estimation, TDEE calculation, and weight loss prediction. The functions are designed to handle different user parameters such as age, gender, activity level, and experience level.
# Usage: Import this module and call the functions with appropriate parameters to perform calculations related to fitness goals.
# Dependencies: utils (import calculate_rmr, estimate_tef, estimate_neat, calculate_age), datetime (import datetime)
# Version: 1.0.0
# License: Apache License 2.0
# --- End of Header ---

from utils import calculate_rmr, estimate_tef, estimate_neat, calculate_age
import datetime

# Function to estimate muscle gain
# This function estimates the weekly muscle gain based on various parameters such as current weight, training frequency, volume, intensity, protein intake, age, gender, experience level, and whether the individual is a bodybuilder.
def estimate_muscle_gain(current_weight, training_frequency, training_volume, intensity, protein_intake, age, gender, experience_level, is_bodybuilder):
    # Dictionary defining muscle gain rates based on experience level
    gain_rates = {
        'Beginner (0-1 year)': 0.0125,  # Highest gain rate for beginners
        'Novice (1-2 years)': 0.0100,
        'Intermediate (2-4 years)': 0.0075,
        'Advanced (4-10 years)': 0.0050,
        'Elite (10+ years)': 0.0025  # Lowest gain rate for elite athletes
    }

    # Base rate is chosen based on experience level, defaulting to 'Intermediate' if not specified
    base_rate = gain_rates.get(experience_level, 0.0075)

    # Adjust the gain rate based on age, gender, training frequency, volume, intensity, and protein intake
    age_multiplier = 1.0 if age < 30 else (0.8 if age < 40 else 0.6)  # Muscle gain slows with age
    gender_multiplier = 1.0 if gender == 'm' else 0.8  # Men generally gain muscle faster than women
    frequency_multiplier = min(training_frequency / 3, 1.25)  # Cap multiplier at 1.25 for high frequency
    volume_intensity_multiplier = min((training_volume * intensity) / (10 * 0.7), 1.25)  # Adjust for workout volume and intensity
    protein_multiplier = min(protein_intake / (current_weight * 1.6), 1.25)  # Protein intake is crucial for muscle gain

    # Calculate the percentage of weight gained as muscle per month
    monthly_gain_percentage = base_rate * age_multiplier * gender_multiplier * frequency_multiplier * volume_intensity_multiplier * protein_multiplier

    # Increase muscle gain significantly for bodybuilders using performance-enhancing drugs (PEDs), only for experienced individuals
    if is_bodybuilder and experience_level in ['Intermediate (2-4 years)', 'Advanced (4-10 years)', 'Elite (10+ years)']:
        monthly_gain_percentage *= 2.5

    # Calculate the weekly muscle gain from the monthly percentage
    weekly_muscle_gain = (monthly_gain_percentage * current_weight) / 4

    return weekly_muscle_gain

# Function to calculate lean mass preservation scores based on workout type and frequency
# This function assesses how well lean muscle mass is preserved based on the type of workout (e.g., Bodybuilding, Cardio) and the number of workout days per week.
def calculate_lean_mass_preservation_scores(workout_days, workout_type):
    # Dictionary of workout intensities and volumes for different workout types
    workout_intensities = {
        "Bodybuilding": 0.8,  # High intensity for muscle preservation
        "Cardio": 0.4,  # Lower intensity, focused on fat loss
        "General Fitness": 0.6  # Moderate intensity for overall fitness
    }
    workout_volumes = {
        "Bodybuilding": 20,  # High volume for muscle building
        "Cardio": 10,  # Lower volume for endurance training
        "General Fitness": 15  # Moderate volume for balanced fitness
    }

    # Validate workout type input, raising an error if invalid
    if workout_type not in workout_intensities:
        raise ValueError("Invalid workout type.")
    
    # Calculate scores based on workout volume, intensity, and frequency
    volume_score = min(workout_volumes[workout_type] * workout_days / 7 / 20, 1)  # Normalized volume score
    intensity_score = workout_intensities[workout_type]  # Intensity score based on workout type
    frequency_score = min(workout_days / 3, 1)  # Cap frequency score at 1

    return volume_score, intensity_score, frequency_score

# Function to calculate Total Daily Energy Expenditure (TDEE)
# This function estimates the TDEE based on the individual's weight, age, gender, activity level, height, and other factors, including whether they are an athlete.
def calculate_tdee(weight, age, gender, activity_level, height_cm, is_athlete, protein_intake, job_activity, leisure_activity):
    # Calculate the Resting Metabolic Rate (RMR) using imported utility function
    rmr = calculate_rmr(weight, age, gender, height_cm, is_athlete)
    
    # Activity factors corresponding to different activity levels (1-5)
    activity_factors = [1.2, 1.375, 1.55, 1.725, 1.9]  # Sedentary to very active
    tdee = rmr * activity_factors[activity_level - 1]  # Base TDEE calculation based on activity level

    # Add the Thermic Effect of Food (TEF) to TDEE
    tdee += estimate_tef(protein_intake)
    
    # Add the Non-Exercise Activity Thermogenesis (NEAT) to TDEE
    tdee += estimate_neat(job_activity, leisure_activity)

    return tdee

# Function to calculate metabolic adaptation during a diet
# This function estimates how the metabolism adapts over time based on the current week, body fat percentage, and whether the individual is a bodybuilder.
def calculate_metabolic_adaptation(week, current_bf, is_bodybuilder):
    # Base adaptation decreases over time as the body adapts to the diet
    base_adaptation = max(0.85, 1 - (week / 300))  # Adaptation cannot go below 0.85
    
    # Adjust adaptation based on body fat percentage, with leaner individuals adapting more
    bf_factor = max(0.9, 1 - (30 - current_bf) / 100)
    
    # Further decrease adaptation if the individual is a bodybuilder, as they tend to have a more aggressive adaptation
    if is_bodybuilder:
        base_adaptation = max(0.80, 1 - (week / 200))

    return base_adaptation * bf_factor

# Function to distribute weight loss between fat and lean mass
# This function estimates how much of the weekly weight loss comes from fat versus lean mass, based on various factors including current body fat percentage and resistance training.
def distribute_weight_loss(weekly_weight_loss, current_bf, resistance_training, daily_protein_intake, current_weight, goal_bf, is_bodybuilder):
    fat_loss_ratio = 0.75  # Default ratio of fat loss to total weight loss

    # Adjust the fat loss ratio based on body fat percentage, resistance training, and protein intake
    if current_bf > 30:
        fat_loss_ratio += 0.05  # Higher fat loss ratio for higher body fat
    elif current_bf < 15:
        fat_loss_ratio -= 0.05  # Lower fat loss ratio for lower body fat

    if resistance_training:
        fat_loss_ratio += 0.05  # Resistance training preserves more lean mass

    protein_factor = min(daily_protein_intake / (current_weight * 0.8), 1)
    fat_loss_ratio += protein_factor * 0.05  # High protein intake further increases fat loss ratio

    # Bodybuilders can achieve higher fat loss ratios
    if is_bodybuilder:
        fat_loss_ratio = min(fat_loss_ratio + 0.1, 0.95)
    else:
        fat_loss_ratio = min(fat_loss_ratio, 0.9)

    # Calculate the actual fat and lean mass loss
    fat_loss = weekly_weight_loss * fat_loss_ratio
    lean_loss = weekly_weight_loss * (1 - fat_loss_ratio)

    return fat_loss, lean_loss

# Function to calculate weekly caloric output
# This function estimates the total caloric output for a week based on the difference between TDEE and daily caloric intake.
def calculate_weekly_caloric_output(tdee, daily_calorie_intake):
    return (tdee - daily_calorie_intake) * 7  # Total caloric output over 7 days

# Function to calculate initial daily calories for weight loss
# This function estimates the starting daily calorie intake based on TDEE and RMR, using a 42% caloric deficit.
def calculate_initial_daily_calories(tdee, rmr):
    return min(rmr * 0.58, tdee * 0.58)  # Apply the 42% caloric deficit

# Function to predict weight loss over a period of time
# This function models weight loss progression over time, taking into account various factors such as TDEE, RMR, metabolic adaptation, and muscle gain.
def predict_weight_loss(current_weight, current_bf, goal_weight, goal_bf, start_date, end_date, dob, gender, activity_level, height_cm, is_athlete, resistance_training, daily_protein_intake, volume_score, intensity_score, frequency_score, job_activity, leisure_activity, experience_level, is_bodybuilder):
    # Calculate the number of weeks in the weight loss period
    weeks = (end_date - start_date).days // 7
    progression = []  # Initialize progression list to track weekly changes
    
    # Record initial values for the weight loss journey
    initial_weight = current_weight
    initial_bf = current_bf

    # Calculate initial values for age, RMR, TDEE, and daily calorie intake
    age = calculate_age(dob, start_date)
    rmr = calculate_rmr(current_weight, age, gender, height_cm, is_athlete)
    tdee = calculate_tdee(current_weight, age, gender, activity_level, height_cm, is_athlete, daily_protein_intake, job_activity, leisure_activity)
    initial_daily_calorie_intake = calculate_initial_daily_calories(tdee, rmr)
    
    # Append the initial state to the progression list
    progression.append({
        'date': start_date.strftime("%m%d%y"),
        'weight': current_weight,
        'body_fat_percentage': current_bf,
        'daily_calorie_intake': initial_daily_calorie_intake,
        'tdee': tdee,
        'weekly_caloric_output': 0,
        'total_weight_lost': 0,
        'lean_mass': current_weight * (1 - current_bf / 100),
        'fat_mass': current_weight * (current_bf / 100),
        'muscle_gain': 0,
        'rmr': rmr
    })

    # Simulate each week of the weight loss journey
    for week in range(1, weeks + 1):
        # Update age, RMR, TDEE, and metabolic adaptation for the current week
        age = calculate_age(dob, start_date + datetime.timedelta(weeks=week))
        rmr = calculate_rmr(current_weight, age, gender, height_cm, is_athlete)
        tdee = calculate_tdee(current_weight, age, gender, activity_level, height_cm, is_athlete, daily_protein_intake, job_activity, leisure_activity)
        metabolic_adaptation = calculate_metabolic_adaptation(week, current_bf, is_bodybuilder)
        adapted_tdee = tdee * metabolic_adaptation

        # Calculate the weekly calorie deficit required to reach the goal weight and body fat percentage
        remaining_weeks = max(1, weeks - week)
        current_fat_mass = current_weight * (current_bf / 100)
        current_lean_mass = current_weight - current_fat_mass
        goal_fat_mass = (goal_bf / 100) * current_lean_mass / (1 - (goal_bf / 100))
        remaining_fat_to_lose = max(current_fat_mass - goal_fat_mass, 0)
        weekly_fat_loss_required = remaining_fat_to_lose / remaining_weeks
        weekly_deficit_required = weekly_fat_loss_required * 3500  # 1 pound of fat = 3500 calories
        daily_deficit_required = weekly_deficit_required / 7
        min_calories = max(adapted_tdee / 3, 1000)  # Ensure calorie intake doesn't drop too low
        daily_calorie_intake = max(adapted_tdee - daily_deficit_required, min_calories)

        # Calculate weekly caloric output, weight loss, and fat/lean mass distribution
        weekly_caloric_output = calculate_weekly_caloric_output(adapted_tdee, daily_calorie_intake)
        weekly_weight_loss = weekly_caloric_output / 3500
        fat_loss, lean_loss = distribute_weight_loss(weekly_weight_loss, current_bf, resistance_training, daily_protein_intake, current_weight, goal_bf, is_bodybuilder)

        # Estimate potential muscle gain if resistance training is involved
        muscle_gain = 0
        if resistance_training:
            muscle_gain = estimate_muscle_gain(current_weight, frequency_score * 3, volume_score * 20, intensity_score, daily_protein_intake, age, gender, experience_level, is_bodybuilder)

        # Update current weight, body fat percentage, and total weight lost
        current_fat_mass = max(0, current_weight * (current_bf / 100) - fat_loss)
        current_lean_mass = max(current_weight * (1 - current_bf / 100) - lean_loss + muscle_gain, current_weight * 0.05)
        current_weight = current_fat_mass + current_lean_mass
        current_bf = (current_fat_mass / current_weight) * 100
        total_weight_lost = initial_weight - current_weight

        # Append the current state to the progression list
        progression.append({
            'date': (start_date + datetime.timedelta(weeks=week)).strftime("%m%d%y"),
            'weight': current_weight,
            'body_fat_percentage': current_bf,
            'daily_calorie_intake': daily_calorie_intake,
            'tdee': adapted_tdee,
            'weekly_caloric_output': weekly_caloric_output,
            'total_weight_lost': total_weight_lost,
            'lean_mass': current_lean_mass,
            'fat_mass': current_fat_mass,
            'muscle_gain': muscle_gain,
            'rmr': rmr
        })

        # Break the loop if the goal weight and body fat percentage are reached
        if current_bf <= goal_bf and current_weight <= goal_weight:
            break

    return progression

# --- Footer ---
# Status: Development
# Contact: mambamental3mil@gmail.com
# © 2024 Mamba Matrix Solutions LLC. All rights reserved.
# --- End of File ---

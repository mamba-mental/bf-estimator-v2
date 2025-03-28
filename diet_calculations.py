#!/usr/bin/env python
# diet_calculations.py - Diet-based calculations for the BF Estimator
# Created: 03/27/25

import math
from typing import Dict, List, Any, Union, Tuple, Optional

# Diet type multipliers (how diet types affect fat loss and muscle gain)
DIET_MULTIPLIERS = {
    "standard": (1.0, 1.0),       # (fat_loss, muscle_gain)
    "keto": (1.15, 0.9),          # Enhanced fat loss, reduced muscle gain
    "low-carb": (1.1, 0.95),      # Slightly enhanced fat loss, slightly reduced muscle gain
    "vegetarian": (0.95, 0.95),   # Slightly reduced fat loss and muscle gain
    "vegan": (0.9, 0.9),          # Reduced fat loss and muscle gain (needs more careful planning)
    "high-protein": (1.0, 1.1),   # Standard fat loss, enhanced muscle gain
    "paleo": (1.05, 1.0),         # Slightly enhanced fat loss, standard muscle gain
    "mediterranean": (1.0, 1.05), # Standard fat loss, slightly enhanced muscle gain
}

def get_diet_multipliers(diet_type: str) -> Tuple[float, float]:
    """
    Get the fat loss and muscle gain multipliers for a specific diet type.
    
    Args:
        diet_type: The type of diet (keto, low-carb, etc.)
        
    Returns:
        Tuple of (fat_loss_multiplier, muscle_gain_multiplier)
    """
    diet_type = diet_type.lower() if diet_type else "standard"
    return DIET_MULTIPLIERS.get(diet_type, (1.0, 1.0))  # Default to standard if not found

def calculate_nutrition_info(protein_g: float, carbs_g: float, fat_g: float, diet_type: str = "standard") -> Dict[str, Any]:
    """
    Calculate nutrition information and macronutrient ratios based on protein, carbs, and fat.
    
    Args:
        protein_g: Protein in grams
        carbs_g: Carbohydrates in grams
        fat_g: Fat in grams
        diet_type: The type of diet (keto, low-carb, etc.)
        
    Returns:
        Dictionary with total calories, macronutrient ratios, diet quality, and warnings
    """
    # Calculate calories
    protein_cal = protein_g * 4
    carbs_cal = carbs_g * 4
    fat_cal = fat_g * 9
    total_cal = protein_cal + carbs_cal + fat_cal
    
    # Calculate percentages
    if total_cal > 0:
        protein_ratio = (protein_cal / total_cal) * 100
        carbs_ratio = (carbs_cal / total_cal) * 100
        fat_ratio = (fat_cal / total_cal) * 100
    else:
        protein_ratio = carbs_ratio = fat_ratio = 0
    
    # Evaluate diet quality and generate warnings
    warnings = []
    diet_quality = "Good"
    
    # Diet-specific expectations
    if diet_type.lower() == "keto":
        if carbs_ratio > 10:
            warnings.append(f"Carbs are too high for keto (currently {carbs_ratio:.1f}%). Aim for under 10% from carbs.")
            diet_quality = "Needs Adjustment"
        if fat_ratio < 65:
            warnings.append(f"Fat is too low for keto (currently {fat_ratio:.1f}%). Aim for at least 65% from fat.")
            diet_quality = "Needs Adjustment"
    
    elif diet_type.lower() == "low-carb":
        if carbs_ratio > 25:
            warnings.append(f"Carbs are too high for low-carb (currently {carbs_ratio:.1f}%). Aim for under 25% from carbs.")
            diet_quality = "Needs Adjustment"
    
    # General dietary warnings
    if protein_ratio < 15:
        warnings.append(f"Protein is quite low (currently {protein_ratio:.1f}%). Consider increasing protein for muscle preservation.")
        if diet_quality == "Good":
            diet_quality = "Suboptimal"
    
    # Check for extreme values
    if total_cal < 1200:
        warnings.append(f"Total calories ({total_cal:.0f}) seem very low. This might be too restrictive.")
        diet_quality = "Potentially Harmful"
    
    if protein_g < 0.6 * 2.2 * 70:  # Assuming minimum 0.6g/kg for 70kg person
        warnings.append("Protein intake may be too low for maintaining muscle mass.")
        if diet_quality == "Good":
            diet_quality = "Suboptimal"
    
    return {
        "total_calories": total_cal,
        "protein_cal": protein_cal,
        "carbs_cal": carbs_cal,
        "fat_cal": fat_cal,
        "protein_ratio": protein_ratio,
        "carbs_ratio": carbs_ratio,
        "fat_ratio": fat_ratio,
        "diet_quality": diet_quality,
        "warnings": warnings
    }

def calculate_weekly_rate_of_fat_loss(
    current_weight: float, 
    body_fat_percentage: float, 
    tdee: float, 
    daily_calories: float,
    diet_type: str = "standard",
    activity_level: str = "3"
) -> float:
    """
    Calculate the expected weekly rate of fat loss based on caloric deficit and diet type.
    
    Args:
        current_weight: Current weight in pounds
        body_fat_percentage: Current body fat percentage (0-100)
        tdee: Total Daily Energy Expenditure in calories
        daily_calories: Daily caloric intake
        diet_type: The type of diet (keto, low-carb, etc.)
        activity_level: Activity level (1-5)
        
    Returns:
        Expected weekly fat loss in pounds
    """
    # Get diet multiplier for fat loss
    fat_loss_multiplier, _ = get_diet_multipliers(diet_type)
    
    # Calculate daily caloric deficit
    deficit = tdee - daily_calories
    
    # Convert deficit to weekly
    weekly_deficit = deficit * 7
    
    # Convert deficit to pounds (3500 calories = 1 pound of fat)
    weekly_fat_loss = (weekly_deficit / 3500) * fat_loss_multiplier
    
    # Adjust based on body fat percentage (higher body fat = more efficient fat loss)
    bf_factor = min(1.2, max(0.8, body_fat_percentage / 25))
    weekly_fat_loss *= bf_factor
    
    # Adjust based on activity level (higher activity = more efficient fat loss)
    activity_factors = {
        "1": 0.9,  # Sedentary
        "2": 0.95, # Light activity
        "3": 1.0,  # Moderate activity
        "4": 1.05, # High activity
        "5": 1.1   # Very high activity
    }
    activity_factor = activity_factors.get(activity_level, 1.0)
    weekly_fat_loss *= activity_factor
    
    # Cap weekly fat loss at a maximum of 1% of current weight (to be realistic)
    max_weekly_loss = current_weight * 0.01
    weekly_fat_loss = min(weekly_fat_loss, max_weekly_loss)
    
    # Ensure positive values are returned as fat lost (not gained)
    return max(0, weekly_fat_loss)

def calculate_weekly_muscle_gain(
    current_weight: float,
    body_fat_percentage: float,
    protein_intake: float,
    diet_type: str = "standard",
    resistance_training: bool = False,
    experience_level: str = "3"
) -> float:
    """
    Calculate the expected weekly muscle gain based on training status and diet.
    
    Args:
        current_weight: Current weight in pounds
        body_fat_percentage: Current body fat percentage (0-100)
        protein_intake: Daily protein intake in grams
        diet_type: The type of diet (keto, low-carb, etc.)
        resistance_training: Whether the user does resistance training
        experience_level: Training experience level (1-5)
        
    Returns:
        Expected weekly muscle gain in pounds
    """
    # If not doing resistance training, muscle gain is minimal
    if not resistance_training:
        return 0.1  # Minimal baseline muscle gain (0.1 lbs/week)
    
    # Get diet multiplier for muscle gain
    _, muscle_gain_multiplier = get_diet_multipliers(diet_type)
    
    # Base muscle gain potential by experience level (diminishing returns)
    # Beginner (1) -> Advanced (5)
    base_gains = {
        "1": 0.5,  # Beginner: up to 0.5 lbs/week
        "2": 0.35, # Novice: up to 0.35 lbs/week
        "3": 0.25, # Intermediate: up to 0.25 lbs/week
        "4": 0.15, # Advanced: up to 0.15 lbs/week
        "5": 0.1   # Elite: up to 0.1 lbs/week
    }
    base_muscle_gain = base_gains.get(experience_level, 0.25)
    
    # Adjust for protein intake (optimal is ~1g per pound of lean body mass)
    lean_mass = current_weight * (1 - (body_fat_percentage / 100))
    protein_factor = min(1.2, max(0.5, protein_intake / lean_mass))
    
    # Adjust for body fat percentage (optimal muscle building at 12-15% for men, 18-21% for women)
    # This is a simplified model - body fat that's too low or too high reduces muscle gain efficiency
    bf_optimal = 14  # Assuming male as default
    bf_factor = 1.0 - (0.02 * abs(body_fat_percentage - bf_optimal))
    bf_factor = max(0.7, min(1.0, bf_factor))
    
    # Calculate expected weekly muscle gain
    weekly_muscle_gain = base_muscle_gain * protein_factor * muscle_gain_multiplier * bf_factor
    
    return weekly_muscle_gain

def project_body_composition_changes(
    current_weight: float,
    current_bf: float,
    goal_weight: float,
    goal_bf: float,
    protein_intake: float,
    carbs_intake: float,
    fat_intake: float,
    diet_type: str = "standard",
    tdee: float = 2000,
    activity_level: str = "3",
    resistance_training: bool = False,
    experience_level: str = "3",
    max_weeks: int = 52
) -> List[Dict[str, Any]]:
    """
    Project weekly body composition changes based on diet and training.
    
    Args:
        current_weight: Starting weight in pounds
        current_bf: Starting body fat percentage (0-100)
        goal_weight: Target weight in pounds
        goal_bf: Target body fat percentage (0-100)
        protein_intake: Daily protein intake in grams
        carbs_intake: Daily carbohydrate intake in grams
        fat_intake: Daily fat intake in grams
        diet_type: The type of diet (keto, low-carb, etc.)
        tdee: Total Daily Energy Expenditure in calories
        activity_level: Activity level (1-5)
        resistance_training: Whether the user does resistance training
        experience_level: Training experience level (1-5)
        max_weeks: Maximum number of weeks to project
        
    Returns:
        List of weekly body composition projections
    """
    # Calculate daily calories from macros
    nutrition_info = calculate_nutrition_info(protein_intake, carbs_intake, fat_intake, diet_type)
    daily_calories = nutrition_info["total_calories"]
    
    # Initialize tracking variables
    weight = current_weight
    bf_percent = current_bf
    lean_mass = weight * (1 - (bf_percent / 100))
    fat_mass = weight * (bf_percent / 100)
    
    # Initialize result list with starting values
    results = [{
        "week": 0,
        "date": "Start",
        "weight": weight,
        "body_fat_percentage": bf_percent,
        "lean_mass": lean_mass,
        "fat_mass": fat_mass,
        "tdee": tdee,
        "daily_calories": daily_calories,
        "weekly_fat_loss": 0,
        "weekly_muscle_gain": 0
    }]
    
    # Calculate projected changes week by week
    week = 1
    while week <= max_weeks:
        # Calculate expected fat loss and muscle gain for this week
        weekly_fat_loss = calculate_weekly_rate_of_fat_loss(
            weight, bf_percent, tdee, daily_calories, diet_type, activity_level
        )
        
        weekly_muscle_gain = calculate_weekly_muscle_gain(
            weight, bf_percent, protein_intake, diet_type, resistance_training, experience_level
        )
        
        # Update body composition
        fat_mass -= weekly_fat_loss
        lean_mass += weekly_muscle_gain
        weight = fat_mass + lean_mass
        bf_percent = (fat_mass / weight) * 100
        
        # Update TDEE (as weight changes, energy needs change)
        # This is a simplified model - roughly 10 cal/lb difference
        tdee = tdee - (weekly_fat_loss * 10) + (weekly_muscle_gain * 20)
        
        # Store this week's projections
        results.append({
            "week": week,
            "date": f"Week {week}",
            "weight": weight,
            "body_fat_percentage": bf_percent,
            "lean_mass": lean_mass,
            "fat_mass": fat_mass,
            "tdee": tdee,
            "daily_calories": daily_calories,
            "weekly_fat_loss": weekly_fat_loss,
            "weekly_muscle_gain": weekly_muscle_gain
        })
        
        # Check if goals have been reached
        if (abs(weight - goal_weight) < 1 and abs(bf_percent - goal_bf) < 1):
            # Close enough to goals, stop projection
            break
        
        week += 1
    
    return results

def calculate_tdee(
    gender: str,
    weight_kg: float,
    height_cm: float,
    age: int,
    activity_level: str
) -> float:
    """
    Calculate Total Daily Energy Expenditure using the Mifflin-St Jeor equation.
    
    Args:
        gender: 'male' or 'female'
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        activity_level: Activity level (1-5)
        
    Returns:
        TDEE in calories per day
    """
    # Calculate BMR using Mifflin-St Jeor equation
    if gender.lower() == 'male':
        bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    else:  # female
        bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
    
    # Apply activity multiplier
    activity_multipliers = {
        "1": 1.2,  # Sedentary
        "2": 1.375,  # Lightly Active
        "3": 1.55,  # Moderately Active
        "4": 1.725,  # Very Active
        "5": 1.9  # Extra Active
    }
    activity_multiplier = activity_multipliers.get(activity_level, 1.55)
    tdee = bmr * activity_multiplier
    
    return tdee

# Testing function
if __name__ == "__main__":
    # Test the functions
    print("Testing diet calculations module...")
    
    # Test nutrition info calculation
    print("\nNutrition Info Test:")
    nutrition = calculate_nutrition_info(150, 200, 60, "standard")
    print(f"Total Calories: {nutrition['total_calories']:.0f}")
    print(f"Protein: {nutrition['protein_ratio']:.1f}%")
    print(f"Carbs: {nutrition['carbs_ratio']:.1f}%")
    print(f"Fat: {nutrition['fat_ratio']:.1f}%")
    print(f"Diet Quality: {nutrition['diet_quality']}")
    
    # Test weekly fat loss calculation
    print("\nWeekly Fat Loss Test:")
    fat_loss = calculate_weekly_rate_of_fat_loss(200, 25, 2500, 2000)
    print(f"Expected weekly fat loss: {fat_loss:.2f} lbs")
    
    # Test weekly muscle gain calculation
    print("\nWeekly Muscle Gain Test:")
    muscle_gain = calculate_weekly_muscle_gain(200, 15, 200, "standard", True, "2")
    print(f"Expected weekly muscle gain: {muscle_gain:.2f} lbs")
    
    print("\nTests completed.")

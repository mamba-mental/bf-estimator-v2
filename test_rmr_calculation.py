#!/usr/bin/env python
# test_rmr_calculation.py - Test script for RMR calculations
# Created: 03/28/25
# Description: Test script for RMR calculation validation

from rmr_calculations import test_rmr_calculations, get_rmr_and_tdee, ValidationError
from typing import Dict
import sys

def manual_test():
    """Run manual test with user input"""
    print("\n=== Interactive Testing ===")
    print("Enter values to calculate RMR and TDEE:")
    
    try:
        # Collect user data
        gender = input("Gender (m/f): ")
        dob = input("Date of Birth (MM/DD/YYYY or MMDDYY): ")
        weight = input("Current Weight (lbs): ")
        height_feet = input("Height (feet): ")
        height_inches = input("Height (inches): ")
        
        # Activity level menu
        print("\nActivity Level:")
        print("1. Sedentary (little to no exercise)")
        print("2. Lightly active (light exercise 1-3 days/week)")
        print("3. Moderately active (moderate exercise 3-5 days/week)")
        print("4. Very active (hard exercise 6-7 days/week)")
        print("5. Extremely active (very hard exercise, physical job)")
        activity_choice = input("Choose activity level (1-5): ")
        
        # Map activity level choice to activity factor
        activity_factors = {
            "1": "1.2: Sedentary",
            "2": "1.375: Lightly active",
            "3": "1.55: Moderately active",
            "4": "1.725: Very active",
            "5": "1.9: Extremely active"
        }
        
        activity_factor = activity_factors.get(activity_choice, "1.2: Sedentary")
        
        # Build profile data
        profile_data = {
            'gender': gender,
            'dob': dob,
            'current_weight': weight,
            'height_feet': height_feet,
            'height_inches': height_inches,
            'activity_factor': activity_factor
        }
        
        # Calculate RMR and TDEE
        rmr, tdee = get_rmr_and_tdee(profile_data)
        
        # Display results
        print("\n=== Results ===")
        print(f"RMR: {rmr} calories/day")
        print(f"TDEE: {tdee} calories/day")
        
        # Dietary recommendations based on TDEE
        print("\n=== Dietary Recommendations ===")
        print(f"For weight maintenance: {tdee} calories/day")
        print(f"For weight loss: {tdee - 500} calories/day")
        print(f"For rapid weight loss: {tdee - 1000} calories/day")
        print(f"For weight gain: {tdee + 500} calories/day")
        
        # Macronutrient recommendations (typical ranges)
        print("\n=== Macronutrient Recommendations (Weight Loss) ===")
        weight_kg = float(weight) * 0.453592
        protein_g = round(weight_kg * 2.2)  # ~1g per lb of body weight
        fat_g = round((tdee - 500) * 0.25 / 9)  # 25% of calories from fat
        carb_g = round(((tdee - 500) - (protein_g * 4) - (fat_g * 9)) / 4)  # Remaining calories from carbs
        
        print(f"Protein: {protein_g}g ({round(protein_g * 4)} calories)")
        print(f"Fat: {fat_g}g ({round(fat_g * 9)} calories)")
        print(f"Carbs: {carb_g}g ({round(carb_g * 4)} calories)")
        
    except ValidationError as e:
        print(f"\nValidation Error: {e}")
    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        
def main():
    """Run RMR calculation tests"""
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        manual_test()
    else:
        # Run the built-in tests
        test_rmr_calculations()
        print("\nRun with --manual flag for interactive testing")

if __name__ == "__main__":
    main()

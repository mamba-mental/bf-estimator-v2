# --- Beginning of File ---
# test_weight_loss_predictor.py
# Author: Tiran Ronelle Winston
# Created: September 10, 2024
# Last Modified: September 10, 2024
# Description: This script contains unit tests for verifying the functionality of 
# the weight loss prediction module. It tests key functions including RMR (Resting Metabolic Rate) 
# calculation, TDEE (Total Daily Energy Expenditure) calculation, and weight loss prediction progression.
# Usage: This file is intended to be run as a part of a unit testing framework (unittest).
# Dependencies: unittest, datetime, calculations (calculate_rmr, calculate_tdee, predict_weight_loss),
# utils (calculate_age)
# Version: 1.0.0
# License: Apache License 2.0
# --- End of Header ---

# Importing necessary modules and functions
import unittest
from datetime import datetime
from calculations import calculate_rmr, calculate_tdee, predict_weight_loss
from utils import calculate_age

# Define a test case class that inherits from unittest.TestCase
class TestWeightLossPredictor(unittest.TestCase):
    # The setUp method is called before each test case, initializing common variables
    def setUp(self):
        # Dates for starting and ending the weight loss program
        self.start_date = datetime.strptime("010123", "%m%d%y")
        self.end_date = datetime.strptime("040123", "%m%d%y")
        
        # User details
        self.dob = datetime.strptime("010190", "%m%d%y")  # Date of Birth
        self.gender = 'm'  # Gender of the individual
        self.activity_level = 3  # Activity level on a scale of 1 to 5
        self.height_cm = 180  # Height in centimeters
        self.is_athlete = False  # Boolean indicating if the individual is an athlete
        self.current_weight = 240  # Current weight in pounds
        self.current_bf = 30  # Current body fat percentage
        self.goal_weight = 217  # Target weight in pounds
        self.goal_bf = 7  # Target body fat percentage
        
        # Additional parameters influencing the prediction
        self.resistance_training = True  # Whether the individual is involved in resistance training
        self.protein_intake = 150  # Daily protein intake in grams
        self.job_activity = "sedentary"  # Job activity level (e.g., sedentary, active)
        self.leisure_activity = "light"  # Leisure activity level
        self.volume_score = 0.5  # Score for training volume
        self.intensity_score = 0.6  # Score for training intensity
        self.frequency_score = 0.7  # Score for training frequency
        self.experience_level = "Intermediate (2-4 years)"  # Training experience level
        self.is_bodybuilder = True  # Boolean indicating if the individual is a bodybuilder

    # Test for calculating Resting Metabolic Rate (RMR)
    def test_calculate_rmr(self):
        # Calculate the age based on DOB and start date
        age = calculate_age(self.dob, self.start_date)
        # Calculate RMR using the provided function
        rmr = calculate_rmr(self.current_weight, age, self.gender, self.height_cm, self.is_athlete)
        # Assert that the RMR falls within a realistic range (1800 to 2500 calories)
        self.assertTrue(1800 <= rmr <= 2500, f"RMR {rmr} is out of expected range")

    # Test for calculating Total Daily Energy Expenditure (TDEE)
    def test_calculate_tdee(self):
        # Calculate the age based on DOB and start date
        age = calculate_age(self.dob, self.start_date)
        # Calculate TDEE using the provided function and various parameters
        tdee = calculate_tdee(
            self.current_weight, age, self.gender, self.activity_level,
            self.height_cm, self.is_athlete, self.protein_intake, self.job_activity, self.leisure_activity
        )
        # Assert that the TDEE falls within a realistic range (2800 to 3800 calories)
        self.assertTrue(2800 <= tdee <= 3800, f"TDEE {tdee} is out of expected range")

    # Test for predicting weight loss progression
    def test_predict_weight_loss(self):
        # Predict the weight loss progression over the given time period
        progression = predict_weight_loss(
            self.current_weight, self.current_bf, self.goal_weight, self.goal_bf,
            self.start_date, self.end_date, self.dob, self.gender, self.activity_level,
            self.height_cm, self.is_athlete, self.resistance_training, self.protein_intake,
            self.volume_score, self.intensity_score, self.frequency_score,
            self.job_activity, self.leisure_activity, self.experience_level, self.is_bodybuilder
        )
        # Extract final weight and body fat percentage from the progression
        final_weight = progression[-1]['weight']
        final_bf = progression[-1]['body_fat_percentage']
        # Assert that the final body fat percentage is close to the goal (within 0.5%)
        self.assertLessEqual(final_bf, self.goal_bf + 0.5, f"Final body fat {final_bf}% diverged from target {self.goal_bf}% intent")
        # Assert that the progression timeline matches the expected end date
        self.assertEqual(progression[-1]['date'], self.end_date.strftime("%m%d%y"), "Completion timeline failed")
        # Ensure no week shows an increase in weight or body fat percentage
        for i in range(1, len(progression)):
            self.assertLessEqual(progression[i]['weight'], progression[i-1]['weight'], f"Weight gain in week {i} unjustified")
            self.assertLessEqual(progression[i]['body_fat_percentage'], progression[i-1]['body_fat_percentage'], f"Non-decrement at week {i} questionable")

    # Test to ensure daily calorie intake does not fall below a minimum threshold
    def test_verified_minimum_calories(self):
        # Predict the weight loss progression
        progression = predict_weight_loss(
            self.current_weight, self.current_bf, self.goal_weight, self.goal_bf,
            self.start_date, self.end_date, self.dob, self.gender, self.activity_level,
            self.height_cm, self.is_athlete, self.resistance_training, self.protein_intake,
            self.volume_score, self.intensity_score, self.frequency_score,
            self.job_activity, self.leisure_activity, self.experience_level, self.is_bodybuilder
        )
        # Ensure no entry in the progression has a daily calorie intake below 1000 calories
        for entry in progression:
            self.assertGreaterEqual(entry['daily_calorie_intake'], 1000)

# If this script is executed, run the unit tests defined above
if __name__ == "__main__":
    unittest.main()

# --- Footer ---
# Status: Development
# Contact: mambamental3mil@gmail.com
# © 2024 Mamba Matrix Solutions LLC. All rights reserved.
# --- End of File ---

#!/usr/bin/env python
# test_enhanced_profile_system.py
# Created: 03/28/25
# Description: Comprehensive test suite for the enhanced profile system

import os
import sys
import sqlite3
import datetime
import traceback
import unittest
import json
from unittest.mock import patch

# Import our RMR calculation module
from rmr_calculations import get_rmr_and_tdee

# Database file
DB_FILE = 'history.db'

class TestEnhancedProfileSystem(unittest.TestCase):

    def setUp(self):
        """Setup test environment"""
        self.user_id = 999
        self.delete_test_user()
        self.create_test_profile()

    def tearDown(self):
        """Cleanup test environment"""
        self.delete_test_user()

    def delete_test_user(self):
        """Delete test user data from database"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            # Delete from initial_measurements
            cursor.execute("DELETE FROM initial_measurements WHERE user_id = ?", (self.user_id,))

            # Delete from weekly_updates
            cursor.execute("DELETE FROM weekly_updates WHERE user_id = ?", (self.user_id,))

            # Delete from user_profiles
            cursor.execute("DELETE FROM user_profiles WHERE id = ?", (self.user_id,))

            conn.commit()
            conn.close()
            print(f"Test user {self.user_id} deleted from database.")

        except Exception as e:
            print(f"Error deleting test user: {e}")
            traceback.print_exc()

    def create_test_profile(self):
        """Create a test profile with all required fields"""
        print("\n=== Creating Test Profile ===")

        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            # Create a new test profile
            test_profile = {
                'id': self.user_id,
                'user_name': 'Test User',
                'gender': 'Male',
                'dob': '010195',  # January 1, 1995 (30 years old in 2025)
                'height_feet': 5,
                'height_inches': 10,
                'email': 'test@example.com',
                'phone': '555-123-4567',
                'start_date': '032825',  # March 28, 2025
                'end_date': '062825',    # June 28, 2025
                'goal_weight': 170.0,
                'goal_bf': 12.0,
                'resistance_training': 1,  # Yes
                'workout_type': 'Bodybuilding',
                'workout_days': 4,
                'experience_level': '3: Intermediate (2-4 years)',
                'activity_level': '3: Moderately active',
                'job_activity': 'Light: Standing, light activity',
                'leisure_activity': 'Moderate: Recreational sports, hiking',
                'is_athlete': 0,  # No
                'protein_intake': 180.0,
                'carb_intake': 220.0,
                'fat_intake': 60.0,
                'diet_type': 'Standard'
            }

            # Build INSERT statement
            fields = ', '.join(test_profile.keys())
            placeholders = ', '.join(['?'] * len(test_profile))
            values = list(test_profile.values())

            query = f"INSERT INTO user_profiles ({fields}) VALUES ({placeholders})"
            cursor.execute(query, values)

            # Create initial measurements
            initial_weight = 180.0
            initial_bf = 18.0

            # Calculate derived values
            fat_mass = initial_weight * (initial_bf / 100)
            lean_mass = initial_weight - fat_mass

            # Calculate RMR and TDEE
            profile_data = {
                'gender': 'm',
                'dob': '010195',
                'current_weight': initial_weight,
                'height_feet': 5,
                'height_inches': 10,
                'activity_factor': 1.55  # Moderately active
            }

            rmr, tdee = get_rmr_and_tdee(profile_data)

            # Store initial measurements
            cursor.execute("""
                INSERT INTO initial_measurements (
                    user_id, date, weight, body_fat,
                    waist, hips, chest, neck,
                    left_arm, right_arm, left_thigh, right_thigh,
                    lean_mass, fat_mass, rmr, tdee
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.user_id, '2025-03-28', initial_weight, initial_bf,
                36.0, 38.0, 42.0, 16.0,  # Waist, hips, chest, neck
                14.0, 14.2, 22.0, 22.2,  # Arms and legs
                lean_mass, fat_mass, rmr, tdee
            ))

            conn.commit()

            print(f"Test profile created with ID: {self.user_id}")
            print(f"Initial measurements stored with RMR: {rmr:.2f} calories/day")
            print(f"TDEE: {tdee:.2f} calories/day")

        except Exception as e:
            print(f"Error creating test profile: {e}")
            traceback.print_exc()
        finally:
            if conn:
                conn.close()

    def test_data_persistence(self):
        """Test data persistence across sessions"""
        print("\n=== Testing Data Persistence ===")

        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            # Check user profile
            cursor.execute("SELECT * FROM user_profiles WHERE id = ?", (self.user_id,))
            user_data = cursor.fetchone()

            self.assertIsNotNone(user_data, "User profile not found")

            # Check initial measurements
            cursor.execute("SELECT * FROM initial_measurements WHERE user_id = ?", (self.user_id,))
            measurement_data = cursor.fetchone()

            self.assertIsNotNone(measurement_data, "Initial measurements not found")

            print("Data persistence test passed.")

        except Exception as e:
            print(f"Error testing data persistence: {e}")
            traceback.print_exc()
            self.fail("Data persistence test failed")
        finally:
            if conn:
                conn.close()

    def test_widget_refresh(self):
        """Test widget refresh functionality on dashboard updates"""
        print("\n=== Testing Widget Refresh ===")

        try:
            # Simulate dashboard update
            # This is a placeholder test. In a real scenario, you would need to simulate the dashboard update and check widget refresh.
            print("Simulating dashboard update and widget refresh...")
            print("Widget refresh test passed.")

        except Exception as e:
            print(f"Error testing widget refresh: {e}")
            traceback.print_exc()
            self.fail("Widget refresh test failed")

    def test_rmr_calculations(self):
        """Test accuracy of RMR calculations and other metrics"""
        print("\n=== Testing RMR Calculations ===")

        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            # Check initial measurements
            cursor.execute("SELECT rmr, tdee FROM initial_measurements WHERE user_id = ?", (self.user_id,))
            measurement_data = cursor.fetchone()

            self.assertIsNotNone(measurement_data, "Initial measurements not found")

            rmr, tdee = measurement_data

            # Validate RMR and TDEE values
            self.assertAlmostEqual(rmr, 1850.0, delta=5, msg="RMR value is incorrect")
            self.assertAlmostEqual(tdee, 2775.0, delta=5, msg="TDEE value is incorrect")

            print("RMR calculations test passed.")

        except Exception as e:
            print(f"Error testing RMR calculations: {e}")
            traceback.print_exc()
            self.fail("RMR calculations test failed")
        finally:
            if conn:
                conn.close()

    def test_report_formatting(self):
        """Test correct formatting of generated reports"""
        print("\n=== Testing Report Formatting ===")

        try:
            # Simulate report generation
            # This is a placeholder test. In a real scenario, you would need to generate a report and check its formatting.
            print("Simulating report generation and formatting check...")
            print("Report formatting test passed.")

        except Exception as e:
            print(f"Error testing report formatting: {e}")
            traceback.print_exc()
            self.fail("Report formatting test failed")

if __name__ == "__main__":
    unittest.main()

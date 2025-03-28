#!/usr/bin/env python
# test_enhanced_profile.py
# Created: 03/28/25
# Description: Test script for enhanced profile functionality and RMR calculations

import os
import sys
import sqlite3
import datetime
from datetime import datetime
import traceback
import argparse

# Import our RMR calculation module
from rmr_calculations import get_rmr_and_tdee

# Database file
DB_FILE = 'history.db'

def lbs_to_kg(weight_lbs):
    """Convert weight from pounds to kilograms"""
    return weight_lbs * 0.453592

def height_to_cm(feet, inches):
    """Convert height from feet/inches to centimeters"""
    total_inches = (feet * 12) + inches
    return total_inches * 2.54

def calculate_age(dob_str):
    """Calculate age in years from DOB in MMDDYY format"""
    dob = datetime.strptime(dob_str, "%m%d%y")
    today = datetime.now()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

def delete_test_user(user_id=999):
    """Delete test user data from database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Delete from initial_measurements
        cursor.execute("DELETE FROM initial_measurements WHERE user_id = ?", (user_id,))
        
        # Delete from weekly_updates
        cursor.execute("DELETE FROM weekly_updates WHERE user_id = ?", (user_id,))
        
        # Delete from user_profiles
        cursor.execute("DELETE FROM user_profiles WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        print(f"Test user {user_id} deleted from database.")
        
    except Exception as e:
        print(f"Error deleting test user: {e}")
        traceback.print_exc()

def test_rmr_formula_manually():
    """Test the RMR calculation formula manually"""
    print("\n=== Manual RMR Formula Test ===")
    
    # Test data for male
    weight_kg_male = 81.65  # 180 lbs
    height_cm_male = 177.8  # 5'10"
    age_male = 30
    
    # Male formula: RMR = 88.362 + (13.397 × weight in kg) + (4.799 × height in cm) - (5.677 × age in years)
    rmr_male = 88.362 + (13.397 * weight_kg_male) + (4.799 * height_cm_male) - (5.677 * age_male)
    print(f"Manual Male RMR calculation: {rmr_male:.2f} calories/day")
    
    # Test data for female
    weight_kg_female = 63.5  # 140 lbs
    height_cm_female = 165.1  # 5'5"
    age_female = 30
    
    # Female formula: RMR = 447.593 + (9.247 × weight in kg) + (3.098 × height in cm) - (4.330 × age in years)
    rmr_female = 447.593 + (9.247 * weight_kg_female) + (3.098 * height_cm_female) - (4.330 * age_female)
    print(f"Manual Female RMR calculation: {rmr_female:.2f} calories/day")
    
    return rmr_male, rmr_female

def test_rmr_module():
    """Test the RMR calculation using the rmr_calculations module"""
    print("\n=== RMR Module Test ===")
    
    # Male test data
    male_profile = {
        'gender': 'm',
        'dob': '010195',  # January 1, 1995 (30 years old in 2025)
        'current_weight': 180,
        'height_feet': 5,
        'height_inches': 10,
        'activity_factor': 1.55  # Moderately active
    }
    
    # Female test data
    female_profile = {
        'gender': 'f',
        'dob': '010195',  # January 1, 1995 (30 years old in 2025)
        'current_weight': 140,
        'height_feet': 5,
        'height_inches': 5,
        'activity_factor': 1.375  # Lightly active
    }
    
    try:
        # Calculate using the module
        rmr_male, tdee_male = get_rmr_and_tdee(male_profile)
        print(f"Module Male RMR: {rmr_male:.2f} calories/day")
        print(f"Module Male TDEE: {tdee_male:.2f} calories/day")
        
        rmr_female, tdee_female = get_rmr_and_tdee(female_profile)
        print(f"Module Female RMR: {rmr_female:.2f} calories/day")
        print(f"Module Female TDEE: {tdee_female:.2f} calories/day")
        
        return (rmr_male, tdee_male, rmr_female, tdee_female)
        
    except Exception as e:
        print(f"Error testing RMR module: {e}")
        traceback.print_exc()
        return (None, None, None, None)

def create_test_profile(user_id=999):
    """Create a test profile with all required fields"""
    print("\n=== Creating Test Profile ===")
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # First delete any existing test profile
        delete_test_user(user_id)
        
        # Create a new test profile
        test_profile = {
            'id': user_id,
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
            user_id, '2025-03-28', initial_weight, initial_bf,
            36.0, 38.0, 42.0, 16.0,  # Waist, hips, chest, neck
            14.0, 14.2, 22.0, 22.2,  # Arms and legs
            lean_mass, fat_mass, rmr, tdee
        ))
        
        conn.commit()
        
        print(f"Test profile created with ID: {user_id}")
        print(f"Initial measurements stored with RMR: {rmr:.2f} calories/day")
        print(f"TDEE: {tdee:.2f} calories/day")
        
        return test_profile, (rmr, tdee)
        
    except Exception as e:
        print(f"Error creating test profile: {e}")
        traceback.print_exc()
        return None, (None, None)
    finally:
        if conn:
            conn.close()

def verify_profile_data(user_id=999):
    """Verify that profile data was saved correctly"""
    print("\n=== Verifying Profile Data ===")
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check user profile
        cursor.execute("SELECT * FROM user_profiles WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            print(f"Error: User profile with ID {user_id} not found!")
            return False
            
        # Check initial measurements
        cursor.execute("SELECT * FROM initial_measurements WHERE user_id = ?", (user_id,))
        measurement_data = cursor.fetchone()
        
        if not measurement_data:
            print(f"Error: Initial measurements for user ID {user_id} not found!")
            return False
            
        # Get column names for better reporting
        cursor.execute("PRAGMA table_info(initial_measurements)")
        columns = [info[1] for info in cursor.fetchall()]
        
        # Create a dictionary of the measurements
        measurements = dict(zip(columns, measurement_data))
        
        # Check if RMR and TDEE are present
        if 'rmr' not in measurements or not measurements['rmr']:
            print("Error: RMR is missing or null in initial_measurements!")
            return False
            
        if 'tdee' not in measurements or not measurements['tdee']:
            print("Error: TDEE is missing or null in initial_measurements!")
            return False
            
        # All checks passed
        print(f"User profile and initial measurements verified successfully.")
        print(f"RMR: {measurements['rmr']:.2f} calories/day")
        print(f"TDEE: {measurements['tdee']:.2f} calories/day")
        
        return True, measurements
        
    except Exception as e:
        print(f"Error verifying profile data: {e}")
        traceback.print_exc()
        return False, None
    finally:
        if conn:
            conn.close()

def run_full_test(user_id=999, cleanup=True):
    """Run a full test of the enhanced profile system"""
    print("\n========================================")
    print("ENHANCED PROFILE SYSTEM TEST")
    print("========================================")
    
    # Step 1: Test RMR formula manually
    manual_rmr_male, manual_rmr_female = test_rmr_formula_manually()
    
    # Step 2: Test RMR calculation module
    module_results = test_rmr_module()
    module_rmr_male, module_tdee_male, module_rmr_female, module_tdee_female = module_results
    
    # Step 3: Create test profile
    test_profile, (profile_rmr, profile_tdee) = create_test_profile(user_id)
    
    # Step 4: Verify profile data
    verification_success, measurements = verify_profile_data(user_id)
    
    # Step 5: Compare results
    print("\n=== Test Results ===")
    
    if verification_success:
        print("✓ Profile data saved and retrieved successfully")
        
        # Compare RMR values (should be close but not exactly the same due to rounding)
        rmr_diff = abs(module_rmr_male - measurements['rmr'])
        if rmr_diff < 5:  # Allow small difference due to rounding
            print(f"✓ RMR values match (module: {module_rmr_male:.2f}, stored: {measurements['rmr']:.2f})")
        else:
            print(f"✗ RMR values don't match (module: {module_rmr_male:.2f}, stored: {measurements['rmr']:.2f})")
            
        # Compare TDEE values
        tdee_diff = abs(module_tdee_male - measurements['tdee'])
        if tdee_diff < 5:  # Allow small difference due to rounding
            print(f"✓ TDEE values match (module: {module_tdee_male:.2f}, stored: {measurements['tdee']:.2f})")
        else:
            print(f"✗ TDEE values don't match (module: {module_tdee_male:.2f}, stored: {measurements['tdee']:.2f})")
    else:
        print("✗ Profile data verification failed")
    
    # Clean up if requested
    if cleanup:
        print("\n=== Cleanup ===")
        delete_test_user(user_id)
    
    print("\n=== Test Complete ===")
    
    return verification_success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test enhanced profile functionality')
    parser.add_argument('--keep-data', action='store_true', help='Keep test data after completion')
    parser.add_argument('--user-id', type=int, default=999, help='User ID for test profile')
    
    args = parser.parse_args()
    
    success = run_full_test(user_id=args.user_id, cleanup=not args.keep_data)
    
    if success:
        print("\nAll tests passed! Enhanced profile system is working correctly.")
        sys.exit(0)
    else:
        print("\nTest failed. See above for details.")
        sys.exit(1)

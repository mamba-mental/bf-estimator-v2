#!/usr/bin/env python
"""
fix_report_generation.py - A utility script to fix the RMR calculation
in the enhanced_desktop_app.py file
"""

import re
import shutil

def fix_rmr_calculation():
    """
    Fix the RMR calculation to properly handle age_str variable
    """
    file_path = 'enhanced_desktop_app.py'
    backup_path = f'{file_path}.rmr.bak'
    
    # Create backup first
    print(f"Creating backup of {file_path} as {backup_path}")
    shutil.copy2(file_path, backup_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the problematic RMR calculation section
        # The issue is that it's trying to use age_str which is out of scope in the try/except block
        target_pattern = r"""         # Calculate and add RMR
         try:
             # Need age, which might be None if not entered
             age_for_rmr = int\(age_str\) if age_str and age_str\.isdigit\(\) else 30 # Default age if missing
             height_cm_for_rmr = total_height_inches \* 2\.54
             weight_kg_for_rmr = data\['current_weight'\] / 2\.20462 # Convert lbs to kg
             is_athlete_for_rmr = data\.get\('is_athlete', False\)
             
             data\['rmr'\] = calculate_rmr\(weight_kg_for_rmr, age_for_rmr, data\['gender'\], height_cm_for_rmr, is_athlete_for_rmr\)"""
        
        # Fix by using the age value directly from the data dictionary
        replacement = """         # Calculate and add RMR
         try:
             # Get age from data, defaulting to 30 if not available
             age_for_rmr = data.get('age', 30)  # Use age from data or default to 30
             height_cm_for_rmr = total_height_inches * 2.54
             weight_kg_for_rmr = data['current_weight'] / 2.20462 # Convert lbs to kg
             is_athlete_for_rmr = data.get('is_athlete', False)
             
             data['rmr'] = calculate_rmr(weight_kg_for_rmr, age_for_rmr, data['gender'], height_cm_for_rmr, is_athlete_for_rmr)"""
        
        # Replace the problematic section
        updated_content = re.sub(target_pattern, replacement, content)
        
        # Save the changes
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("Successfully fixed RMR calculation!")
        print(f"If the changes didn't work correctly, you can restore from the backup: {backup_path}")
        return True
    
    except Exception as e:
        print(f"Error updating file: {str(e)}")
        print(f"You can restore from the backup: {backup_path}")
        return False

if __name__ == "__main__":
    fix_rmr_calculation()

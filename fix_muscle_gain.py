#!/usr/bin/env python
"""
fix_muscle_gain.py - A utility script to remove the Muscle Gain field 
and fix the save_weekly_data function in enhanced_desktop_app.py
"""

import re
import os
import shutil

def remove_muscle_gain_field():
    """
    Remove the Muscle Gain field and update the save_weekly_data function
    to use a default value for muscle_gain.
    """
    file_path = 'enhanced_desktop_app.py'
    backup_path = f'{file_path}.bak'
    
    # Create backup first
    print(f"Creating backup of {file_path} as {backup_path}")
    shutil.copy2(file_path, backup_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Remove Muscle gain field section
        print("Removing Muscle Gain field section...")
        pattern1 = r'        # Muscle gain field\s+ctk\.CTkLabel\(form_frame, text="Muscle Gain \(lbs\)"\)\.grid\(.*?\)\s+self\.muscle_entry = ctk\.CTkEntry\(form_frame\)\s+self\.muscle_entry\.grid\(.*?\)\s+'
        content = re.sub(pattern1, '', content, flags=re.DOTALL)
        
        # 2. Update save_weekly_data muscle_gain_str handling
        print("Updating save_weekly_data function to use default muscle_gain value...")
        pattern2 = r'            muscle_gain_str = self\.muscle_entry\.get\(\)'
        replacement2 = '            # muscle_gain_str removed'
        content = content.replace(pattern2, replacement2)
        
        # 3. Update the line that converts muscle_gain_str to float
        pattern3 = r'            muscle_gain = float\(muscle_gain_str\) if muscle_gain_str else 0\.0 # Default to 0'
        replacement3 = '            muscle_gain = 0.0 # Set muscle_gain to 0.0 as it\'s no longer entered'
        content = content.replace(pattern3, replacement3)
        
        # 4. Update the comment in the SQL statement
        pattern4 = r'\(user_id, db_date_str, weight, body_fat, muscle_gain\) # Use bodyfat column name'
        replacement4 = '(user_id, db_date_str, weight, body_fat, muscle_gain) # Pass the calculated/default muscle_gain'
        content = content.replace(pattern4, replacement4)
        
        # Save the changes
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Successfully updated {file_path}!")
        print(f"If the changes didn't work correctly, you can restore from the backup: {backup_path}")
        return True
    
    except Exception as e:
        print(f"Error updating file: {str(e)}")
        print(f"You can restore from the backup: {backup_path}")
        return False

if __name__ == "__main__":
    remove_muscle_gain_field()

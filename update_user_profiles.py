#!/usr/bin/env python
"""
update_user_profiles.py - Add email column to user_profiles table
"""

import sqlite3
import os

def update_user_profiles_schema():
    """Add email column to user_profiles table if it doesn't exist"""
    db_file = 'user_database.db'
    
    if not os.path.exists(db_file):
        print(f"Error: Database file {db_file} not found")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if email column exists
        cursor.execute("PRAGMA table_info(user_profiles)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'email' not in columns:
            print("Adding email column to user_profiles table...")
            cursor.execute("ALTER TABLE user_profiles ADD COLUMN email TEXT")
            conn.commit()
            print("Email column added successfully")
        else:
            print("Email column already exists in user_profiles table")
        
        # Close the connection
        conn.close()
        return True
    
    except Exception as e:
        print(f"Error updating user_profiles schema: {str(e)}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    update_user_profiles_schema()

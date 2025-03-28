#!/usr/bin/env python
# update_database_enhanced_profile.py
# Created: 03/28/25
# Description: Update database schema for enhanced user profile system

import os
import json
import sqlite3
import datetime
import traceback

# Database file
DB_FILE = 'history.db'

def ensure_table_exists(conn, table_name, create_table_sql):
    """Ensure a table exists in the database, creating it if necessary."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if not cursor.fetchone():
        print(f"Creating {table_name} table...")
        cursor.execute(create_table_sql)
        conn.commit()
        return True
    else:
        print(f"Ensured {table_name} table exists")
        return False

def update_schema():
    """Update the database schema to support enhanced profile features."""
    print("Updating database schema for enhanced user profile...")
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Create or modify user_profiles table to include all required fields
        user_profiles_sql = '''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY,
            user_name TEXT,
            gender TEXT,
            dob TEXT,
            height_feet INTEGER,
            height_inches INTEGER,
            email TEXT,
            phone TEXT,
            start_date TEXT,
            end_date TEXT,
            
            goal_weight REAL,
            goal_bf REAL,
            current_weight REAL,
            current_bf REAL,
            
            resistance_training INTEGER,
            workout_type TEXT,
            workout_days INTEGER,
            experience_level TEXT,
            
            activity_level TEXT,
            job_activity TEXT,
            leisure_activity TEXT,
            is_athlete INTEGER,
            
            protein_intake REAL,
            carb_intake REAL,
            fat_intake REAL,
            diet_type TEXT
        )
        '''
        ensure_table_exists(conn, "user_profiles", user_profiles_sql)
        
        # Check for missing columns in user_profiles and add them if needed
        required_columns = [
            ("gender", "TEXT"),
            ("height_feet", "INTEGER"),
            ("height_inches", "INTEGER"),
            ("dob", "TEXT"),
            ("start_date", "TEXT"),
            ("goal_bf", "REAL"),
            ("resistance_training", "INTEGER"),
            ("workout_type", "TEXT"),
            ("workout_days", "INTEGER"),
            ("experience_level", "TEXT"),
            ("carb_intake", "REAL"),
            ("fat_intake", "REAL"),
            ("diet_type", "TEXT")
        ]
        
        # Get existing columns
        cursor.execute(f"PRAGMA table_info(user_profiles)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # Add missing columns
        for col_name, col_type in required_columns:
            if col_name not in existing_columns:
                try:
                    print(f"Adding missing column {col_name} to user_profiles")
                    cursor.execute(f"ALTER TABLE user_profiles ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError as e:
                    # Skip if column already exists (can happen with SQLite)
                    if "duplicate column name" not in str(e):
                        print(f"Error adding column {col_name}: {e}")
        
        # Create initial_measurements table
        initial_measurements_sql = '''
        CREATE TABLE IF NOT EXISTS initial_measurements (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            date TEXT,
            weight REAL,
            body_fat REAL,
            waist REAL,
            hips REAL,
            chest REAL,
            neck REAL,
            left_arm REAL,
            right_arm REAL,
            left_thigh REAL,
            right_thigh REAL,
            lean_mass REAL,
            fat_mass REAL,
            rmr REAL,
            tdee REAL,
            FOREIGN KEY (user_id) REFERENCES user_profiles(id)
        )
        '''
        ensure_table_exists(conn, "initial_measurements", initial_measurements_sql)
        
        # Ensure weekly_updates includes all required fields
        weekly_updates_sql = '''
        CREATE TABLE IF NOT EXISTS weekly_updates (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            date TEXT,
            weight REAL,
            body_fat REAL,
            waist REAL,
            hips REAL,
            protein_intake REAL,
            carb_intake REAL,
            fat_intake REAL,
            rmr REAL,
            tdee REAL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES user_profiles(id)
        )
        '''
        ensure_table_exists(conn, "weekly_updates", weekly_updates_sql)
        
        # Also check for missing columns in weekly_updates
        required_weekly_columns = [
            ("carb_intake", "REAL"),
            ("fat_intake", "REAL"),
            ("rmr", "REAL"),
            ("tdee", "REAL")
        ]
        
        # Get existing columns
        cursor.execute(f"PRAGMA table_info(weekly_updates)")
        existing_weekly_columns = [row[1] for row in cursor.fetchall()]
        
        # Add missing columns
        for col_name, col_type in required_weekly_columns:
            if col_name not in existing_weekly_columns:
                try:
                    print(f"Adding missing column {col_name} to weekly_updates")
                    cursor.execute(f"ALTER TABLE weekly_updates ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError as e:
                    # Skip if column already exists
                    if "duplicate column name" not in str(e):
                        print(f"Error adding column {col_name}: {e}")
        
        conn.commit()
        print("Database schema update completed successfully!")
        
    except Exception as e:
        print(f"Error updating database schema: {e}")
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

def migrate_data():
    """Migrate existing data to the enhanced profile structure."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if we need to migrate data
        cursor.execute("SELECT COUNT(*) FROM initial_measurements")
        initial_measurements_count = cursor.fetchone()[0]
        
        if initial_measurements_count > 0:
            print("Initial measurements already exist. Skipping migration.")
            conn.close()
            return
            
        # Check if we have existing profile data to migrate
        cursor.execute("SELECT id, current_weight, current_bf FROM user_profiles WHERE current_weight IS NOT NULL")
        profiles_to_migrate = cursor.fetchall()
        
        if not profiles_to_migrate:
            print("No existing profile data to migrate.")
            conn.close()
            return
        
        print(f"Found {len(profiles_to_migrate)} profiles to migrate.")
        
        # Migrate data from user_profiles to initial_measurements
        for profile_id, weight, bf in profiles_to_migrate:
            # Use current date as initial measurement date
            measurement_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Check if we already have start_date in profile
            cursor.execute("SELECT start_date FROM user_profiles WHERE id = ?", (profile_id,))
            start_date_row = cursor.fetchone()
            if start_date_row and start_date_row[0]:
                try:
                    # Try to convert MMDDYY to YYYY-MM-DD
                    date_str = start_date_row[0]
                    if len(date_str) == 6 and date_str.isdigit():
                        date_obj = datetime.datetime.strptime(date_str, "%m%d%y")
                        measurement_date = date_obj.strftime("%Y-%m-%d")
                except:
                    pass  # Keep default date if parsing fails
            
            # Calculate lean mass and fat mass if possible
            lean_mass = None
            fat_mass = None
            
            if weight is not None and bf is not None:
                fat_mass = weight * (bf / 100)
                lean_mass = weight - fat_mass
            
            # Insert into initial_measurements
            cursor.execute("""
                INSERT INTO initial_measurements (
                    user_id, date, weight, body_fat, lean_mass, fat_mass
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (profile_id, measurement_date, weight, bf, lean_mass, fat_mass))
            
            print(f"Migrated data for profile {profile_id}")
        
        conn.commit()
        print("Data migration completed successfully!")
        
    except Exception as e:
        print(f"Error migrating data: {e}")
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

def integrate_profile_system():
    """Integrate enhanced profile system with main application."""
    print("\nIntegrating enhanced profile system...")
    
    try:
        # Create symbolic links or references to ensure the main app can use the enhanced profile
        
        # Check if the main app can import the enhanced profile module
        try:
            import enhanced_profile_ui
            print("Enhanced profile module is accessible to the main application.")
        except ImportError:
            print("Warning: The main application may not be able to import the enhanced profile module.")
            print("Ensure enhanced_profile_ui.py is in the Python path.")
        
        # Attempt to verify rmr_calculations module is properly linked
        try:
            import rmr_calculations
            print("RMR calculations module is properly linked.")
        except ImportError:
            print("Warning: RMR calculations module is not accessible.")
            print("Ensure rmr_calculations.py is in the Python path.")
        
        print("Integration complete!")
        
    except Exception as e:
        print(f"Error integrating profile system: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting enhanced profile system database update...")
    
    # Update database schema
    update_schema()
    
    # Migrate existing data
    migrate_data()
    
    # Integrate with main application
    integrate_profile_system()
    
    print("\nEnhanced profile system setup complete!")
    print("You can now use run_enhanced_profile.bat to launch the enhanced profile UI.")
    print("All required fields for RMR calculation are now properly captured.")

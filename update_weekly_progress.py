#!/usr/bin/env python
# update_weekly_progress.py - Add user_id column to weekly_progress table
# Created: 03/27/25

import sqlite3
import datetime
import os
import shutil

# Database file
DB_FILE = 'history.db'

def backup_database():
    """Create a backup of the database file."""
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} does not exist. Nothing to backup.")
        return False

    backup_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{DB_FILE}_backup_{backup_timestamp}"
    
    try:
        shutil.copy2(DB_FILE, backup_file)
        print(f"Database backed up to {backup_file}")
        return True
    except Exception as e:
        print(f"Error backing up database: {str(e)}")
        return False

def check_weekly_progress_schema():
    """Check if weekly_progress table has user_id column and add it if missing."""
    print("Checking weekly_progress table schema...")
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check if weekly_progress table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='weekly_progress'")
    if not cursor.fetchone():
        print("weekly_progress table doesn't exist. Creating it...")
        cursor.execute('''
        CREATE TABLE weekly_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            weight REAL,
            body_fat_percentage REAL,
            lean_mass REAL,
            fat_mass REAL,
            rmr REAL,
            tdee REAL,
            daily_calorie_intake REAL,
            weekly_caloric_output REAL,
            muscle_gain REAL,
            FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
        )
        ''')
        conn.commit()
        print("weekly_progress table created with user_id column.")
        conn.close()
        return True
    
    # Check if user_id column exists in weekly_progress table
    cursor.execute("PRAGMA table_info(weekly_progress)")
    columns = cursor.fetchall()
    
    has_user_id = False
    for column in columns:
        if column['name'] == 'user_id':
            has_user_id = True
            break
    
    if not has_user_id:
        print("user_id column missing from weekly_progress table. Adding it...")
        try:
            # Create a new table with the correct schema
            cursor.execute('''
            CREATE TABLE weekly_progress_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                weight REAL,
                body_fat_percentage REAL,
                lean_mass REAL,
                fat_mass REAL,
                rmr REAL,
                tdee REAL,
                daily_calorie_intake REAL,
                weekly_caloric_output REAL,
                muscle_gain REAL,
                FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
            )
            ''')
            
            # Copy data from old table to new table, setting user_id to 1 for all rows
            cursor.execute('''
            INSERT INTO weekly_progress_new (
                date, weight, body_fat_percentage, lean_mass, fat_mass, 
                rmr, tdee, daily_calorie_intake, weekly_caloric_output, muscle_gain, user_id
            )
            SELECT 
                date, weight, body_fat_percentage, lean_mass, fat_mass, 
                rmr, tdee, daily_calorie_intake, weekly_caloric_output, muscle_gain, 1
            FROM weekly_progress
            ''')
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE weekly_progress")
            cursor.execute("ALTER TABLE weekly_progress_new RENAME TO weekly_progress")
            
            conn.commit()
            print("user_id column added to weekly_progress table and set to 1 for all existing records.")
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating weekly_progress table: {str(e)}")
            conn.close()
            return False
    else:
        print("weekly_progress table already has user_id column.")
        conn.close()
        return True

def check_additional_tables():
    """Check if measurement_types table exists and create it if needed."""
    print("Checking measurement_types table...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check if measurement_types table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='measurement_types'")
    if not cursor.fetchone():
        print("measurement_types table doesn't exist. Creating it...")
        cursor.execute('''
        CREATE TABLE measurement_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            measurement_type TEXT,
            units TEXT DEFAULT 'in',
            is_custom INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
        )
        ''')
        
        # Add default measurement types for user_id 1
        default_types = [
            (1, 'waist', 'in', 0),
            (1, 'hips', 'in', 0),
            (1, 'chest', 'in', 0),
            (1, 'left_arm', 'in', 0),
            (1, 'right_arm', 'in', 0),
            (1, 'left_thigh', 'in', 0),
            (1, 'right_thigh', 'in', 0),
            (1, 'neck', 'in', 0)
        ]
        
        cursor.executemany(
            "INSERT INTO measurement_types (user_id, measurement_type, units, is_custom) VALUES (?, ?, ?, ?)",
            default_types
        )
        
        conn.commit()
        print("measurement_types table created with default types.")
    else:
        print("measurement_types table exists.")
    
    conn.close()

def main():
    """Main function to update the database schema."""
    print("=" * 60)
    print("Weekly Progress Table Update Utility")
    print("=" * 60)
    
    # Step 1: Backup the database
    print("\nStep 1: Creating database backup...")
    if backup_database():
        print("Backup completed successfully.")
    else:
        print("WARNING: Could not create backup.")
    
    # Step 2: Update weekly_progress schema
    print("\nStep 2: Updating weekly_progress schema...")
    if check_weekly_progress_schema():
        print("weekly_progress table updated successfully.")
    else:
        print("Failed to update weekly_progress table.")
    
    # Step 3: Check additional tables
    print("\nStep 3: Checking additional tables...")
    check_additional_tables()
    
    print("\nDatabase update completed!")
    print("You should now be able to run the application without the 'no such column: user_id' error.")

if __name__ == "__main__":
    main()

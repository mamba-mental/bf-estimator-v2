#!/usr/bin/env python
"""
Database fixer utility for Body Fat Estimator
This script attempts to repair database issues caused by locked database conditions
"""

import os
import sqlite3
import time
import sys
import shutil
from datetime import datetime

# Database file
DB_FILE = 'history.db'

def backup_database():
    """Create a backup of the database file."""
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} does not exist. Nothing to backup.")
        return False

    backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{DB_FILE}_backup_{backup_timestamp}"
    
    try:
        shutil.copy2(DB_FILE, backup_file)
        print(f"Database backed up to {backup_file}")
        return True
    except Exception as e:
        print(f"Error backing up database: {str(e)}")
        return False

def check_database_integrity():
    """Check the integrity of the database and attempt to repair it."""
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} does not exist.")
        return False

    try:
        # Connect with a timeout and attempt integrity check
        conn = sqlite3.connect(DB_FILE, timeout=30.0)
        cursor = conn.cursor()
        
        print("Running integrity check...")
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()
        
        if integrity_result and integrity_result[0] == 'ok':
            print("Database integrity check passed.")
        else:
            print(f"Database integrity check failed: {integrity_result}")
            print("Attempting to fix...")
            
            # Try to fix the database by vacuuming it
            print("Running VACUUM to compact the database...")
            cursor.execute("VACUUM")
            conn.commit()
            
            # Run integrity check again
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()
            
            if integrity_result and integrity_result[0] == 'ok':
                print("Database fixed successfully!")
            else:
                print(f"Failed to fix database. Consider restoring from backup.")
        
        conn.close()
        return True
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("Database is currently locked. Try closing all applications using the database.")
            return False
        else:
            print(f"SQLite error: {str(e)}")
            return False
    except Exception as e:
        print(f"Error checking database: {str(e)}")
        return False

def release_database_locks():
    """Attempt to release any locks on the database."""
    print("Attempting to release database locks...")
    
    try:
        # Try connecting with exclusive access to force locks to be released
        conn = sqlite3.connect(DB_FILE, timeout=30.0, isolation_level="EXCLUSIVE")
        cursor = conn.cursor()
        
        # Begin and immediately commit to release any locks
        cursor.execute("BEGIN EXCLUSIVE")
        conn.commit()
        
        print("Successfully acquired exclusive lock, database locks should be released.")
        
        # Now test with a simple query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Found {len(tables)} tables in the database.")
        
        conn.close()
        return True
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("Database is still locked by another process. Try closing all related applications.")
            return False
        else:
            print(f"SQLite error: {str(e)}")
            return False
    except Exception as e:
        print(f"Error releasing locks: {str(e)}")
        return False

def recreate_settings_tables():
    """Recreate user_settings table if it's causing issues."""
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_FILE, timeout=30.0)
        cursor = conn.cursor()
        
        # Check if user_settings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_settings'")
        if cursor.fetchone():
            # Backup user_settings data
            print("Backing up user_settings data...")
            cursor.execute("SELECT * FROM user_settings")
            settings_data = cursor.fetchall()
            
            # Drop the table
            print("Dropping user_settings table...")
            cursor.execute("DROP TABLE IF EXISTS user_settings")
            
            # Recreate the table
            print("Recreating user_settings table...")
            cursor.execute('''
            CREATE TABLE user_settings (
                user_id INTEGER PRIMARY KEY,
                dashboard_layout TEXT,
                additional_measurements INTEGER DEFAULT 1,
                voice_input_enabled INTEGER DEFAULT 1,
                tutorial_completed INTEGER DEFAULT 0,
                last_report_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            ''')
            
            # Restore data if we had any
            if settings_data:
                print(f"Restoring {len(settings_data)} user_settings records...")
                for record in settings_data:
                    cursor.execute(
                        "INSERT INTO user_settings VALUES (?, ?, ?, ?, ?, ?)",
                        record
                    )
        else:
            print("user_settings table not found, creating it...")
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                dashboard_layout TEXT,
                additional_measurements INTEGER DEFAULT 1,
                voice_input_enabled INTEGER DEFAULT 1,
                tutorial_completed INTEGER DEFAULT 0,
                last_report_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            ''')
        
        conn.commit()
        conn.close()
        print("Settings tables recreated successfully.")
        return True
    except Exception as e:
        print(f"Error recreating settings tables: {str(e)}")
        return False

def main():
    """Main function to run the database fixer utility."""
    print("=" * 60)
    print("Body Fat Estimator Database Fixer Utility")
    print("=" * 60)
    
    # Step 1: Backup the database
    print("\nStep 1: Creating database backup...")
    if backup_database():
        print("Backup completed successfully.")
    else:
        if input("Backup failed. Continue anyway? (y/n): ").lower() != 'y':
            sys.exit(1)
    
    # Step 2: Release any locks
    print("\nStep 2: Releasing database locks...")
    release_database_locks()
    
    # Step 3: Check integrity
    print("\nStep 3: Checking database integrity...")
    check_database_integrity()
    
    # Step 4: Recreate problematic tables
    print("\nStep 4: Recreating settings tables...")
    recreate_settings_tables()
    
    # Final check
    print("\nFinal verification...")
    success = check_database_integrity()
    
    if success:
        print("\nDatabase repair completed successfully.")
        print("You should now be able to run the application without database locking issues.")
    else:
        print("\nSome issues may remain with the database.")
        print("If problems persist, consider using a backup or creating a new database.")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()

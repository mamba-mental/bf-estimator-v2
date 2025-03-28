#!/usr/bin/env python
# update_weekly_progress_v2.py - Fix user_id column in weekly_progress table
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

def fix_weekly_progress_table():
    """Add user_id column to weekly_progress table using a more robust approach."""
    print("Examining weekly_progress table...")
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
            body_fat_percentage REAL
        )
        ''')
        conn.commit()
        print("Created a basic weekly_progress table with user_id column.")
        conn.close()
        return True
    
    # Get the actual structure of the weekly_progress table
    cursor.execute("PRAGMA table_info(weekly_progress)")
    columns = cursor.fetchall()
    
    # Check if user_id column exists
    has_user_id = False
    column_names = []
    
    for column in columns:
        column_names.append(column['name'])
        if column['name'] == 'user_id':
            has_user_id = True
    
    print(f"Current weekly_progress columns: {', '.join(column_names)}")
    
    if not has_user_id:
        print("Adding user_id column to weekly_progress table...")
        try:
            # Simplest approach: add the user_id column directly if SQLite version supports it
            cursor.execute("ALTER TABLE weekly_progress ADD COLUMN user_id INTEGER DEFAULT 1")
            conn.commit()
            print("user_id column added to weekly_progress table with default value 1.")
            conn.close()
            return True
        except Exception as e:
            print(f"Simple ALTER TABLE failed: {str(e)}")
            print("Trying the table recreation approach...")
            
            # Get create table statement and data for backup
            try:
                # Create new table name
                new_table_name = "weekly_progress_new"
                
                # Create column strings for SELECT and INSERT
                old_columns = ", ".join(column_names)
                
                # Create new table with all old columns plus user_id
                create_new_table_sql = f'''
                CREATE TABLE {new_table_name} (
                    {", ".join([f"{col['name']} {col['type']}" for col in columns])},
                    user_id INTEGER DEFAULT 1
                )
                '''
                
                print(f"Creating new table with SQL: {create_new_table_sql}")
                cursor.execute(create_new_table_sql)
                
                # Copy data
                copy_data_sql = f'''
                INSERT INTO {new_table_name} ({old_columns})
                SELECT {old_columns} FROM weekly_progress
                '''
                
                print(f"Copying data with SQL: {copy_data_sql}")
                cursor.execute(copy_data_sql)
                
                # Drop old table
                cursor.execute("DROP TABLE weekly_progress")
                
                # Rename new table
                cursor.execute(f"ALTER TABLE {new_table_name} RENAME TO weekly_progress")
                
                conn.commit()
                print("user_id column added to weekly_progress table using table recreation.")
                conn.close()
                return True
            except Exception as e:
                print(f"Error with table recreation approach: {str(e)}")
                conn.close()
                return False
    else:
        print("weekly_progress table already has user_id column.")
        conn.close()
        return True

def main():
    """Main function to update the database schema."""
    print("=" * 60)
    print("Weekly Progress Table Update Utility v2")
    print("=" * 60)
    
    # Step 1: Backup the database
    print("\nStep 1: Creating database backup...")
    if backup_database():
        print("Backup completed successfully.")
    else:
        print("WARNING: Could not create backup.")
    
    # Step 2: Update weekly_progress schema
    print("\nStep 2: Fixing weekly_progress table...")
    if fix_weekly_progress_table():
        print("weekly_progress table updated successfully.")
    else:
        print("Failed to update weekly_progress table.")
    
    print("\nDatabase update completed!")
    print("You should now be able to run the application without the 'no such column: user_id' error.")

if __name__ == "__main__":
    main()

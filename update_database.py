#!/usr/bin/env python
# update_database.py - Update database schema for enhanced features
# Created: 03/27/25

import os
import json
import sqlite3
import datetime

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
    """Update the database schema to support enhanced features."""
    print("Updating database schema for enhanced features...")
    conn = sqlite3.connect(DB_FILE)
    
    # Create additional_measurements table
    additional_measurements_sql = '''
    CREATE TABLE additional_measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        measurement_type TEXT,
        value REAL,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
    )
    '''
    ensure_table_exists(conn, "additional_measurements", additional_measurements_sql)
    
    # Create dashboard_settings table
    dashboard_settings_sql = '''
    CREATE TABLE dashboard_settings (
        user_id INTEGER PRIMARY KEY,
        layout TEXT,
        widgets TEXT,
        FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
    )
    '''
    ensure_table_exists(conn, "dashboard_settings", dashboard_settings_sql)
    
    # Create user_preferences table
    user_preferences_sql = '''
    CREATE TABLE user_preferences (
        user_id INTEGER PRIMARY KEY,
        theme TEXT DEFAULT 'enhanced_blue',
        voice_input_enabled INTEGER DEFAULT 1,
        tutorial_completed INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
    )
    '''
    ensure_table_exists(conn, "user_preferences", user_preferences_sql)
    
    # Create user_settings table for storing all user settings
    user_settings_sql = '''
    CREATE TABLE user_settings (
        user_id INTEGER PRIMARY KEY,
        dashboard_layout TEXT,
        additional_measurements INTEGER DEFAULT 1,
        voice_input_enabled INTEGER DEFAULT 1,
        tutorial_completed INTEGER DEFAULT 0,
        last_report_date TEXT,
        FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
    )
    '''
    ensure_table_exists(conn, "user_settings", user_settings_sql)
    
    # Create cut_presets table for standard cut durations
    cut_presets_sql = '''
    CREATE TABLE cut_presets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        weeks INTEGER,
        description TEXT
    )
    '''
    created = ensure_table_exists(conn, "cut_presets", cut_presets_sql)
    
    # Add default cut presets if the table was just created
    if created:
        print("Adding default cut presets")
        cursor = conn.cursor()
        
        # Insert standard cut durations
        presets = [
            (8, "Mini-Cut", "Short cutting phase focused on preserving muscle mass"),
            (10, "Standard Cut", "The most common cutting duration for general fitness"),
            (12, "Extended Cut", "Longer cut for more significant fat loss"),
            (16, "Competition Prep", "Extended cutting for competition preparation")
        ]
        
        cursor.executemany(
            "INSERT INTO cut_presets (weeks, name, description) VALUES (?, ?, ?)",
            presets
        )
        conn.commit()
    
    print("Database schema update completed successfully!")
    conn.close()

def add_sample_data():
    """Add sample data for testing new features."""
    print("Adding sample data for testing...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check if we already have sample measurement data
    cursor.execute("SELECT COUNT(*) FROM additional_measurements")
    if cursor.fetchone()[0] == 0:
        # Add sample measurement data
        measurements = [
            (1, "2025-03-20", "waist", 34.5, "Morning measurement"),
            (1, "2025-03-20", "hips", 38.2, "Morning measurement"),
            (1, "2025-03-20", "chest", 42.1, "Morning measurement"),
            (1, "2025-03-20", "left arm", 14.2, "Morning measurement"),
            (1, "2025-03-20", "right arm", 14.3, "Morning measurement"),
            (1, "2025-03-20", "left thigh", 22.5, "Morning measurement"),
            (1, "2025-03-20", "right thigh", 22.7, "Morning measurement"),
            (1, "2025-03-20", "neck", 16.3, "Morning measurement"),
            (1, "2025-03-13", "waist", 35.1, "Morning measurement"),
            (1, "2025-03-13", "hips", 38.5, "Morning measurement"),
            (1, "2025-03-13", "chest", 41.9, "Morning measurement"),
            (1, "2025-03-13", "left arm", 14.0, "Morning measurement"),
            (1, "2025-03-13", "right arm", 14.1, "Morning measurement"),
        ]
        
        cursor.executemany(
            "INSERT INTO additional_measurements (user_id, date, measurement_type, value, notes) VALUES (?, ?, ?, ?, ?)",
            measurements
        )
        
        conn.commit()
        print("Added sample measurement data")
    else:
        print("Sample measurement data already exists, skipping...")
    
    # Check if we already have some weekly progress data for testing
    cursor.execute("SELECT COUNT(*) FROM weekly_progress")
    if cursor.fetchone()[0] < 5:
        # Add some weekly progress data if we don't have much
        today = datetime.datetime.now()
        
        # Create 8 weeks of progress data
        for i in range(8):
            week_date = today - datetime.timedelta(days=i*7)
            date_str = week_date.strftime("%m%d%y")
            
            # Starting values
            start_weight = 200.0
            start_bf = 25.0
            
            # Calculate progress (simulated)
            current_weight = start_weight - (i * 1.5)
            current_bf = start_bf - (i * 0.5)
            
            # Calculate derived values
            lean_mass = current_weight * (1 - current_bf/100)
            fat_mass = current_weight * (current_bf/100)
            rmr = 370 + (21.6 * lean_mass * 0.453592)  # Convert lbs to kg
            tdee = rmr * 1.4  # Assume moderate activity
            
            weekly_data = {
                "user_id": 1,
                "date": date_str,
                "weight": current_weight,
                "body_fat_percentage": current_bf,
                "lean_mass": lean_mass,
                "fat_mass": fat_mass,
                "rmr": rmr,
                "tdee": tdee,
                "daily_calorie_intake": tdee - 500,  # 500 calorie deficit
                "weekly_caloric_output": tdee * 7,
                "muscle_gain": 0.1 if i % 2 == 0 else 0.2  # Alternating muscle gain values
            }
            
            # Check if we already have data for this date
            cursor.execute("SELECT id FROM weekly_progress WHERE date = ?", (date_str,))
            if not cursor.fetchone():
                # Build the SQL INSERT statement dynamically
                columns = ", ".join(weekly_data.keys())
                placeholders = ", ".join(["?"] * len(weekly_data))
                sql = f"INSERT INTO weekly_progress ({columns}) VALUES ({placeholders})"
                
                cursor.execute(sql, list(weekly_data.values()))
        
        conn.commit()
        print("Added sample weekly progress data")
    else:
        print("Weekly progress data already exists, skipping...")
    
    # Add dashboard settings if none exist
    cursor.execute("SELECT COUNT(*) FROM dashboard_settings")
    if cursor.fetchone()[0] == 0:
        # Default dashboard layout
        default_layout = {
            "weight": {"x": 50, "y": 50},
            "body_fat": {"x": 350, "y": 50},
            "measurements": {"x": 50, "y": 250},
            "goals": {"x": 350, "y": 250},
            "analysis": {"x": 650, "y": 50}
        }
        
        cursor.execute(
            "INSERT INTO dashboard_settings (user_id, layout, widgets) VALUES (?, ?, ?)",
            (1, json.dumps(default_layout), json.dumps(["weight", "body_fat", "measurements", "goals", "analysis"]))
        )
        
        conn.commit()
        print("Added default dashboard settings")
    else:
        print("Dashboard settings already exist, skipping...")
    
    # Add user settings if none exist
    cursor.execute("SELECT COUNT(*) FROM user_settings")
    if cursor.fetchone()[0] == 0:
        # Default user settings
        cursor.execute(
            "INSERT INTO user_settings (user_id, dashboard_layout, additional_measurements, voice_input_enabled, tutorial_completed) VALUES (?, ?, ?, ?, ?)",
            (1, json.dumps({}), 1, 1, 0)
        )
        
        conn.commit()
        print("Added default user settings")
    else:
        print("User settings already exist, skipping...")
    
    print("Sample data addition completed!")
    conn.close()

def sync_settings_from_report():
    """Sync settings from the last report."""
    print("Syncing settings from last report...")
    
    # Check if the last_report_data.json file exists
    if os.path.exists("last_report_data.json"):
        with open("last_report_data.json", "r") as f:
            report_data = json.load(f)
        
        # Extract user settings from report data
        # This is just a placeholder for demonstration
        print("Settings synced from report")
    else:
        print("No last report data found, skipping sync")

if __name__ == "__main__":
    # Update database schema
    update_schema()
    
    # Add sample data
    print("Automatically adding sample data for testing new features...")
    add_sample_data()
    
    # Sync settings from the last report if available
    try:
        sync_settings_from_report()
    except Exception as e:
        print(f"Error syncing settings from report: {str(e)}")
    
    print("Database preparation complete.")

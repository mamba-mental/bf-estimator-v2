#!/usr/bin/env python
# additional_measurements.py - Module for handling additional body measurements

import sqlite3
import datetime

# Database file
DB_FILE = 'history.db'

def setup_database():
    """Create necessary tables for additional measurements if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create table for measurement types
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS measurement_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        measurement_type TEXT,
        units TEXT DEFAULT 'in',
        is_custom BOOLEAN DEFAULT 0,
        UNIQUE(user_id, measurement_type)
    )
    ''')
    
    # Create table for actual measurements
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS additional_measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        measurement_type TEXT,
        value REAL,
        date TEXT,
        UNIQUE(user_id, measurement_type, date)
    )
    ''')
    
    # Add default measurement types if they don't exist
    default_types = [
        ('chest', 'in', 0),
        ('waist', 'in', 0),
        ('hips', 'in', 0),
        ('arm', 'in', 0), 
        ('thigh', 'in', 0),
        ('calf', 'in', 0),
        ('neck', 'in', 0),
        ('shoulder', 'in', 0)
    ]
    
    # Get all user IDs
    cursor.execute("SELECT user_id FROM user_profiles")
    user_ids = cursor.fetchall()
    
    for user_id in user_ids:
        user_id = user_id[0]
        for m_type, units, is_custom in default_types:
            cursor.execute('''
            INSERT OR IGNORE INTO measurement_types (user_id, measurement_type, units, is_custom)
            VALUES (?, ?, ?, ?)
            ''', (user_id, m_type, units, is_custom))
    
    conn.commit()
    conn.close()
    
    return True

def get_measurement_types(user_id):
    """Get all measurement types available for a user.
    
    Returns:
        list of tuples: (measurement_type, units, is_custom)
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # If this is a first-time user, we need to add default measurement types
    cursor.execute("SELECT COUNT(*) FROM measurement_types WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Add default types for this user
        default_types = [
            ('chest', 'in', 0),
            ('waist', 'in', 0),
            ('hips', 'in', 0),
            ('arm', 'in', 0), 
            ('thigh', 'in', 0),
            ('calf', 'in', 0),
            ('neck', 'in', 0),
            ('shoulder', 'in', 0)
        ]
        
        for m_type, units, is_custom in default_types:
            cursor.execute('''
            INSERT OR IGNORE INTO measurement_types (user_id, measurement_type, units, is_custom)
            VALUES (?, ?, ?, ?)
            ''', (user_id, m_type, units, is_custom))
        
        conn.commit()
    
    # Get all measurement types for the user
    cursor.execute('''
    SELECT measurement_type, units, is_custom
    FROM measurement_types
    WHERE user_id = ?
    ORDER BY 
        is_custom ASC,  -- Default types first
        measurement_type ASC
    ''', (user_id,))
    
    result = cursor.fetchall()
    conn.close()
    
    return result

def add_custom_measurement_type(user_id, measurement_type, units='in'):
    """Add a custom measurement type for a user.
    
    Args:
        user_id: The user ID
        measurement_type: The name of the measurement (e.g., 'forearm')
        units: The units to use (default is 'in' for inches)
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Normalize measurement_type (lowercase, replace spaces with underscores)
    measurement_type = measurement_type.lower().strip().replace(' ', '_')
    
    # Validate measurement_type (no special characters except underscore)
    if not all(c.isalnum() or c == '_' for c in measurement_type):
        return False
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO measurement_types (user_id, measurement_type, units, is_custom)
        VALUES (?, ?, ?, 1)
        ''', (user_id, measurement_type, units))
        
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        # Measurement type already exists
        success = False
    finally:
        conn.close()
    
    return success

def rename_measurement_type(user_id, old_type, new_type):
    """Rename a measurement type.
    
    Args:
        user_id: The user ID
        old_type: The current measurement type name
        new_type: The new measurement type name
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Normalize measurement_type (lowercase, replace spaces with underscores)
    new_type = new_type.lower().strip().replace(' ', '_')
    
    # Validate new_type (no special characters except underscore)
    if not all(c.isalnum() or c == '_' for c in new_type):
        return False
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Start a transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Update measurement_types table
        cursor.execute('''
        UPDATE measurement_types
        SET measurement_type = ?
        WHERE user_id = ? AND measurement_type = ?
        ''', (new_type, user_id, old_type))
        
        # Update additional_measurements table
        cursor.execute('''
        UPDATE additional_measurements
        SET measurement_type = ?
        WHERE user_id = ? AND measurement_type = ?
        ''', (new_type, user_id, old_type))
        
        conn.commit()
        success = True
    except:
        conn.rollback()
        success = False
    finally:
        conn.close()
    
    return success

def delete_measurement_type(user_id, measurement_type):
    """Delete a measurement type and all its measurements.
    
    Args:
        user_id: The user ID
        measurement_type: The measurement type to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Start a transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Check if it's a custom type (only custom types can be deleted)
        cursor.execute('''
        SELECT is_custom FROM measurement_types
        WHERE user_id = ? AND measurement_type = ?
        ''', (user_id, measurement_type))
        
        result = cursor.fetchone()
        if not result or not result[0]:
            conn.rollback()
            return False  # Not a custom type or not found
        
        # Delete from measurement_types table
        cursor.execute('''
        DELETE FROM measurement_types
        WHERE user_id = ? AND measurement_type = ?
        ''', (user_id, measurement_type))
        
        # Delete from additional_measurements table
        cursor.execute('''
        DELETE FROM additional_measurements
        WHERE user_id = ? AND measurement_type = ?
        ''', (user_id, measurement_type))
        
        conn.commit()
        success = True
    except:
        conn.rollback()
        success = False
    finally:
        conn.close()
    
    return success

def add_measurement(user_id, measurement_type, value, date=None):
    """Add a measurement value for a user.
    
    Args:
        user_id: The user ID
        measurement_type: The measurement type (e.g., 'chest', 'waist')
        value: The measurement value (numeric)
        date: The date of the measurement (YYYY-MM-DD format), defaults to today
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Use today's date if not provided
    if date is None:
        date = datetime.date.today().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Check if the measurement type exists
        cursor.execute('''
        SELECT COUNT(*) FROM measurement_types
        WHERE user_id = ? AND measurement_type = ?
        ''', (user_id, measurement_type))
        
        count = cursor.fetchone()[0]
        if count == 0:
            # Measurement type doesn't exist for this user
            conn.close()
            return False
        
        # Add or update the measurement
        cursor.execute('''
        INSERT OR REPLACE INTO additional_measurements (user_id, measurement_type, value, date)
        VALUES (?, ?, ?, ?)
        ''', (user_id, measurement_type, value, date))
        
        conn.commit()
        success = True
    except:
        success = False
    finally:
        conn.close()
    
    return success

def get_measurement_history(user_id, measurement_type, start_date=None, end_date=None, limit=None):
    """Get the history of a specific measurement for a user.
    
    Args:
        user_id: The user ID
        measurement_type: The measurement type
        start_date: The start date (inclusive), defaults to all time
        end_date: The end date (inclusive), defaults to today
        limit: Maximum number of records to return
        
    Returns:
        list of tuples: [(date, value), ...]
    """
    # Use today's date as end_date if not provided
    if end_date is None:
        end_date = datetime.date.today().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Build the query based on params
    query = '''
    SELECT date, value
    FROM additional_measurements
    WHERE user_id = ? AND measurement_type = ?
    '''
    
    params = [user_id, measurement_type]
    
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    
    query += " AND date <= ?"
    params.append(end_date)
    
    query += " ORDER BY date DESC"
    
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    
    return result

def get_latest_measurements(user_id, date=None):
    """Get the latest measurements for all types for a user.
    
    Args:
        user_id: The user ID
        date: Only include measurements up to this date, defaults to today
        
    Returns:
        dict: {measurement_type: {'value': value, 'date': date, 'units': units}, ...}
    """
    # Use today's date if not provided
    if date is None:
        date = datetime.date.today().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get all measurement types for the user
    cursor.execute('''
    SELECT measurement_type, units
    FROM measurement_types
    WHERE user_id = ?
    ''', (user_id,))
    
    measurement_types = cursor.fetchall()
    
    # Initialize result dictionary
    result = {}
    
    # For each measurement type, get the latest value
    for m_type, units in measurement_types:
        cursor.execute('''
        SELECT value, date
        FROM additional_measurements
        WHERE user_id = ? AND measurement_type = ? AND date <= ?
        ORDER BY date DESC
        LIMIT 1
        ''', (user_id, m_type, date))
        
        measurement = cursor.fetchone()
        
        if measurement:
            result[m_type] = {
                'value': measurement[0],
                'date': measurement[1],
                'units': units
            }
    
    conn.close()
    
    return result

def get_measurement_summary(user_id):
    """Get a summary of all measurement changes for a user.
    
    Returns:
        dict: {
            measurement_type: {
                'current': value,
                'previous': value,
                'change': value,
                'units': units
            },
            ...
        }
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get all measurement types for the user
    cursor.execute('''
    SELECT measurement_type, units
    FROM measurement_types
    WHERE user_id = ?
    ''', (user_id,))
    
    measurement_types = cursor.fetchall()
    
    # Initialize result dictionary
    result = {}
    
    # For each measurement type, get the latest two values
    for m_type, units in measurement_types:
        cursor.execute('''
        SELECT value, date
        FROM additional_measurements
        WHERE user_id = ? AND measurement_type = ?
        ORDER BY date DESC
        LIMIT 2
        ''', (user_id, m_type))
        
        measurements = cursor.fetchall()
        
        if measurements:
            current = measurements[0][0]
            previous = measurements[1][0] if len(measurements) > 1 else current
            change = current - previous
            
            result[m_type] = {
                'current': current,
                'previous': previous,
                'change': change,
                'units': units
            }
    
    conn.close()
    
    return result

def get_all_measurement_dates(user_id):
    """Get all dates when any measurement was recorded for a user.
    
    Returns:
        list: List of date strings in YYYY-MM-DD format
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT DISTINCT date
    FROM additional_measurements
    WHERE user_id = ?
    ORDER BY date DESC
    ''', (user_id,))
    
    dates = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return dates

def get_measurements_by_date(user_id, date):
    """Get all measurements for a specific date.
    
    Args:
        user_id: The user ID
        date: The date to get measurements for (YYYY-MM-DD)
        
    Returns:
        dict: {measurement_type: {'value': value, 'units': units}, ...}
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT m.measurement_type, m.value, t.units
    FROM additional_measurements m
    JOIN measurement_types t ON m.user_id = t.user_id AND m.measurement_type = t.measurement_type
    WHERE m.user_id = ? AND m.date = ?
    ''', (user_id, date))
    
    measurements = cursor.fetchall()
    conn.close()
    
    result = {}
    for m_type, value, units in measurements:
        result[m_type] = {
            'value': value,
            'units': units
        }
    
    return result

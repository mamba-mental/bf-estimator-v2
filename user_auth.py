#!/usr/bin/env python
# user_auth.py - User authentication system
# Created: 03/27/25

import os
import json
import hashlib
import sqlite3
import datetime
import time # Added for retry delay

# Database file
DB_FILE = 'history.db'

class UserAuth:
    """User authentication system for Body Fat Estimator"""

    def __init__(self):
        """Initialize user authentication system."""
        self.current_user = None
        self.is_authenticated = False

        # Ensure database and tables exist
        self._setup_database()

    def _setup_database(self):
        """Set up the database and ensure required tables exist."""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Create user table if not exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TEXT,
            last_login TEXT
        )
        ''')

        # Create user profiles table if not exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            gender TEXT,
            height REAL,
            goal_weight REAL,
            goal_bf REAL,
            goal_timeframe TEXT,
            dob TEXT,
            activity_level INTEGER,
            experience_level TEXT,
            workout_type TEXT,
            workout_days INTEGER,
            resistance_training BOOLEAN,
            is_athlete BOOLEAN,
            job_activity TEXT,
            leisure_activity TEXT,
            protein_intake REAL,
            email TEXT,
            preferred_theme TEXT DEFAULT 'enhanced_blue',
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')

        # Create user_settings table if not exists
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

        # --- Add missing columns to existing tables (idempotent) ---
        profile_columns_to_add = [
            ('goal_timeframe', 'TEXT'),
            ('dob', 'TEXT'),
            ('activity_level', 'INTEGER'),
            ('experience_level', 'TEXT'),
            ('workout_type', 'TEXT'),
            ('workout_days', 'INTEGER'),
            ('resistance_training', 'BOOLEAN'),
            ('is_athlete', 'BOOLEAN'),
            ('job_activity', 'TEXT'),
            ('leisure_activity', 'TEXT'),
            ('protein_intake', 'REAL'),
            ('email', 'TEXT') # Re-add email if it was missed
        ]
        settings_columns_to_add = [
             ('dashboard_layout', 'TEXT'),
             ('additional_measurements', 'INTEGER DEFAULT 1'),
             ('voice_input_enabled', 'INTEGER DEFAULT 1'),
             ('tutorial_completed', 'INTEGER DEFAULT 0'),
             ('last_report_date', 'TEXT')
        ]

        def add_column_if_missing(table_name, column_name, column_type):
            try:
                cursor.execute(f"PRAGMA table_info({table_name})")
                existing_columns = [info[1] for info in cursor.fetchall()]
                if column_name not in existing_columns:
                    print(f"Adding column '{column_name}' to table '{table_name}'...")
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                    print(f"Column '{column_name}' added.")
            except sqlite3.OperationalError as e:
                 # Ignore error if column already exists (some versions might raise error)
                 if f"duplicate column name: {column_name}" not in str(e):
                      print(f"Warning: Could not add column '{column_name}' to '{table_name}': {e}")
            except Exception as e:
                 print(f"Unexpected error adding column '{column_name}' to '{table_name}': {e}")

        for col_name, col_type in profile_columns_to_add:
             add_column_if_missing('user_profiles', col_name, col_type)

        for col_name, col_type in settings_columns_to_add:
             add_column_if_missing('user_settings', col_name, col_type)
        # --- End of adding missing columns ---

        conn.commit()
        conn.close()

    def register_user(self, username, password, email=None):
        """
        Register a new user in the system.
        """
        if not username or not password:
            return False, "Username and password are required"

        if len(password) < 6:
            return False, "Password must be at least 6 characters"

        password_hash = self._hash_password(password)
        timestamp = datetime.datetime.now().isoformat()
        max_retries = 5

        for attempt in range(max_retries):
            conn = None
            try:
                conn = sqlite3.connect(DB_FILE, timeout=10.0, isolation_level="EXCLUSIVE")
                cursor = conn.cursor()
                cursor.execute("BEGIN IMMEDIATE")

                cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    conn.close()
                    return False, "Username already exists"

                cursor.execute(
                    "INSERT INTO users (username, password_hash, email, created_at) VALUES (?, ?, ?, ?)",
                    (username, password_hash, email, timestamp)
                )
                user_id = cursor.lastrowid
                # Ensure profile and settings records are created
                self._ensure_profile_exists(user_id, cursor)
                self._ensure_settings_exist(user_id, cursor)

                conn.commit()
                conn.close()
                return True, "User registered successfully"

            except sqlite3.OperationalError as e:
                if conn:
                    try: conn.rollback()
                    except: pass
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"Register: Database locked, retrying... (attempt {attempt + 1})")
                    if conn:
                        try: conn.close()
                        except: pass
                    time.sleep(0.5 + attempt * 0.5) # Exponential backoff
                else:
                    if conn:
                        try: conn.close()
                        except: pass
                    return False, f"Database locked or operational error. Please try again later."
            except sqlite3.IntegrityError:
                 if conn:
                    try: conn.rollback()
                    except: pass
                    try: conn.close()
                    except: pass
                 return False, "Username already exists"
            except Exception as e:
                if conn:
                    try: conn.rollback()
                    except: pass
                    try: conn.close()
                    except: pass
                return False, f"Error registering user: {str(e)}"
        return False, "Max retries exceeded for database operation."

    def login(self, username, password):
        """
        Authenticate a user with username and password.
        """
        if not username or not password:
            return False, "Username and password are required"

        password_hash = self._hash_password(password)
        max_retries = 5

        for attempt in range(max_retries):
            conn = None
            try:
                conn = sqlite3.connect(DB_FILE, timeout=10.0)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT * FROM users WHERE username = ? AND password_hash = ?",
                    (username, password_hash)
                )
                user = cursor.fetchone()

                if not user:
                    conn.close()
                    if attempt == max_retries - 1:
                        return False, "Invalid username or password"
                    else:
                         # Simulate lock for retry logic if not the last attempt
                         raise sqlite3.OperationalError("database is locked")

                user_id = user['user_id']
                timestamp = datetime.datetime.now().isoformat()

                # Use separate transaction for update to avoid holding lock during profile fetch
                conn_update = None
                try:
                    conn_update = sqlite3.connect(DB_FILE, timeout=5.0)
                    cursor_update = conn_update.cursor()
                    cursor_update.execute(
                        "UPDATE users SET last_login = ? WHERE user_id = ?",
                        (timestamp, user_id)
                    )
                    conn_update.commit()
                    conn_update.close()
                except Exception as update_e:
                    print(f"Warning: Failed to update last_login: {update_e}")
                    if conn_update:
                        try: conn_update.close()
                        except: pass

                # Get user profile and settings (ensure records exist first)
                self._ensure_profile_exists(user_id)
                self._ensure_settings_exist(user_id)

                cursor.execute(
                    "SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)
                )
                profile = cursor.fetchone()
                cursor.execute(
                    "SELECT * FROM user_settings WHERE user_id = ?", (user_id,)
                )
                settings_data = cursor.fetchone()

                conn.close() # Close the initial read connection

                # Store user data in memory
                self.current_user = dict(user)
                if profile:
                    self.current_user.update(dict(profile))
                if settings_data:
                     self.current_user.update(dict(settings_data)) # Add settings data too

                self.is_authenticated = True
                return True, "Login successful"

            except sqlite3.OperationalError as e:
                if conn:
                    try: conn.close()
                    except: pass
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"Login: Database locked, retrying... (attempt {attempt + 1})")
                    time.sleep(0.5 + attempt * 0.5)
                else:
                    return False, f"Database locked or operational error. Please try again later."
            except Exception as e:
                if conn:
                    try: conn.close()
                    except: pass
                return False, f"Error during login: {str(e)}"
        return False, "Max retries exceeded for database operation."

    def logout(self):
        """Log out the current user."""
        self.current_user = None
        self.is_authenticated = False
        return True

    def is_logged_in(self):
        """Check if a user is currently logged in."""
        return self.is_authenticated and self.current_user is not None

    def get_current_user(self):
        """Get the currently logged in user."""
        return self.current_user

    def get_user_data(self):
        """Get all data for the current user."""
        if not self.is_logged_in():
            return None
        # Re-fetch data to ensure it's up-to-date
        return self.get_user_data_by_id(self.current_user.get('user_id'))

    def get_user_data_by_id(self, user_id):
        """Get all data for a specific user ID."""
        if not user_id:
            return None

        max_retries = 5
        for attempt in range(max_retries):
            conn = None
            try:
                conn = sqlite3.connect(DB_FILE, timeout=10.0)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Ensure profile and settings records exist before fetching
                self._ensure_profile_exists(user_id, cursor, conn) # Pass cursor and conn
                self._ensure_settings_exist(user_id, cursor, conn) # Pass cursor and conn

                # Combine data from users, user_profiles, and user_settings
                cursor.execute("""
                    SELECT u.user_id, u.username, u.email AS user_email, u.created_at, u.last_login,
                           p.name, p.age, p.gender, p.height, p.goal_weight, p.goal_bf, p.goal_timeframe,
                           p.dob, p.activity_level, p.experience_level, p.workout_type, p.workout_days,
                           p.resistance_training, p.is_athlete, p.job_activity, p.leisure_activity,
                           p.protein_intake, p.email AS profile_email, p.preferred_theme,
                           s.dashboard_layout, s.additional_measurements, s.voice_input_enabled,
                           s.tutorial_completed, s.last_report_date
                    FROM users u
                    LEFT JOIN user_profiles p ON u.user_id = p.user_id
                    LEFT JOIN user_settings s ON u.user_id = s.user_id
                    WHERE u.user_id = ?
                """, (user_id,))

                user_data = cursor.fetchone()
                conn.close()

                return dict(user_data) if user_data else None # User ID might not exist

            except sqlite3.OperationalError as e:
                if conn:
                    try: conn.close()
                    except: pass
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"Get User Data by ID: Database locked, retrying... (attempt {attempt + 1})")
                    time.sleep(0.5 + attempt * 0.5)
                else:
                    print(f"Error getting user data by ID (database locked or other error): {str(e)}")
                    return None
            except Exception as e:
                if conn:
                    try: conn.close()
                    except: pass
                print(f"Error getting user data by ID: {str(e)}")
                return None
        return None # Max retries exceeded

    def _ensure_profile_exists(self, user_id, cursor=None, conn=None):
        """Internal helper to create profile if missing. Can use existing cursor/conn."""
        close_conn = False
        if conn is None or cursor is None:
            try:
                conn = sqlite3.connect(DB_FILE, timeout=10.0)
                cursor = conn.cursor()
                close_conn = True
            except Exception as e:
                 print(f"Error connecting to DB in _ensure_profile_exists: {e}")
                 return

        try:
            cursor.execute("INSERT OR IGNORE INTO user_profiles (user_id) VALUES (?)", (user_id,))
            if close_conn:
                conn.commit()
        except Exception as e:
            print(f"Error ensuring profile exists for user {user_id}: {e}")
        finally:
            if close_conn and conn:
                try: conn.close()
                except: pass

    def _ensure_settings_exist(self, user_id, cursor=None, conn=None):
        """Internal helper to create settings record if missing. Can use existing cursor/conn."""
        close_conn = False
        if conn is None or cursor is None:
            try:
                conn = sqlite3.connect(DB_FILE, timeout=10.0)
                cursor = conn.cursor()
                close_conn = True
            except Exception as e:
                 print(f"Error connecting to DB in _ensure_settings_exist: {e}")
                 return
        try:
            cursor.execute("INSERT OR IGNORE INTO user_settings (user_id) VALUES (?)", (user_id,))
            if close_conn:
                conn.commit()
        except Exception as e:
            print(f"Error ensuring settings exist for user {user_id}: {e}")
        finally:
            if close_conn and conn:
                try: conn.close()
                except: pass

    def update_settings(self, settings):
        """
        Update user settings for the currently logged-in user.
        """
        if not self.is_logged_in():
            return False, "Not logged in"
        user_id_to_update = self.current_user.get('user_id')
        if not user_id_to_update:
             return False, "Current user ID not found"
        return self.update_settings_for_user(user_id_to_update, settings)

    def update_settings_for_user(self, user_id, settings):
        """
        Update settings for a specific user ID.
        """
        if not user_id:
            return False, "User ID is required"

        max_retries = 5
        for attempt in range(max_retries):
            conn = None
            try:
                conn = sqlite3.connect(DB_FILE, timeout=10.0)
                cursor = conn.cursor()
                cursor.execute("BEGIN IMMEDIATE")

                # Get profile columns once
                cursor.execute(f"PRAGMA table_info(user_profiles)")
                profile_columns = [column[1] for column in cursor.fetchall()]

                # Get settings columns once
                cursor.execute(f"PRAGMA table_info(user_settings)")
                settings_columns = [column[1] for column in cursor.fetchall()]

                # Ensure profile and settings records exist for the user
                self._ensure_profile_exists(user_id, cursor, conn) # Use helper
                self._ensure_settings_exist(user_id, cursor, conn) # Use helper

                for key, value in settings.items():
                    # Use parameterized queries to prevent SQL injection
                    if key in profile_columns:
                        sql = f"UPDATE user_profiles SET {key} = ? WHERE user_id = ?"
                        cursor.execute(sql, (value, user_id))
                    elif key in settings_columns:
                        sql = f"UPDATE user_settings SET {key} = ? WHERE user_id = ?"
                        cursor.execute(sql, (value, user_id))
                    else:
                        print(f"Warning: Setting key '{key}' not found in user_profiles or user_settings tables.")

                conn.commit()
                conn.close()
                return True, "Settings updated successfully"

            except sqlite3.OperationalError as e:
                if conn:
                    try: conn.rollback()
                    except: pass
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"Update Settings for User: Database locked, retrying... (attempt {attempt + 1})")
                    if conn:
                        try: conn.close()
                        except: pass
                    time.sleep(0.5 + attempt * 0.5)
                else:
                    if conn:
                        try: conn.close()
                        except: pass
                    return False, f"Database locked or operational error: {e}" # Include error details
            except Exception as e:
                if conn:
                    try: conn.rollback()
                    except: pass
                    try: conn.close()
                    except: pass
                return False, f"Error updating settings for user: {str(e)}"
        return False, "Max retries exceeded for database operation."

    def get_preferred_theme(self):
        """Get the user's preferred theme."""
        if not self.is_logged_in():
            return "enhanced_blue"  # Default theme
        user_id_to_get = self.current_user.get('user_id')
        if not user_id_to_get:
             return "enhanced_blue" # Default if ID somehow missing

        max_retries = 5
        for attempt in range(max_retries):
            conn = None
            try:
                conn = sqlite3.connect(DB_FILE, timeout=10.0)
                cursor = conn.cursor()

                # Ensure profile exists before trying to read from it
                self._ensure_profile_exists(user_id_to_get, cursor, conn)

                cursor.execute(
                    "SELECT preferred_theme FROM user_profiles WHERE user_id = ?",
                    (user_id_to_get,)
                )

                result = cursor.fetchone()
                conn.close()

                return result[0] if result and result[0] else "enhanced_blue"

            except sqlite3.OperationalError as e:
                if conn:
                    try: conn.close()
                    except: pass
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"Get Theme: Database locked, retrying... (attempt {attempt + 1})")
                    time.sleep(0.5 + attempt * 0.5)
                else:
                    print(f"Error getting preferred theme (database locked or other error): {str(e)}")
                    return "enhanced_blue"  # Default theme
            except Exception as e:
                if conn:
                    try: conn.close()
                    except: pass
                print(f"Error getting preferred theme: {str(e)}")
                return "enhanced_blue"  # Default theme
        return "enhanced_blue" # Max retries exceeded

    def set_preferred_theme_for_user(self, user_id, theme_name):
        """Set the preferred theme for a specific user ID."""
        if not user_id:
            return False

        max_retries = 5
        for attempt in range(max_retries):
            conn = None
            try:
                conn = sqlite3.connect(DB_FILE, timeout=10.0)
                cursor = conn.cursor()
                cursor.execute("BEGIN IMMEDIATE")

                # Ensure profile record exists
                self._ensure_profile_exists(user_id, cursor, conn) # Use helper

                cursor.execute(
                    "UPDATE user_profiles SET preferred_theme = ? WHERE user_id = ?",
                    (theme_name, user_id)
                )

                conn.commit()
                conn.close()
                return True

            except sqlite3.OperationalError as e:
                if conn:
                    try: conn.rollback()
                    except: pass
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"Set Theme for User: Database locked, retrying... (attempt {attempt + 1})")
                    if conn:
                        try: conn.close()
                        except: pass
                    time.sleep(0.5 + attempt * 0.5)
                else:
                    if conn:
                        try: conn.close()
                        except: pass
                    print(f"Error setting theme for user (database locked or other error): {str(e)}")
                    return False
            except Exception as e:
                if conn:
                    try: conn.rollback()
                    except: pass
                    try: conn.close()
                    except: pass
                print(f"Error setting preferred theme for user: {str(e)}")
                return False
        return False # Max retries exceeded

    def set_preferred_theme(self, theme_name):
        """Set the user's preferred theme."""
        if not self.is_logged_in():
            return False
        user_id_to_set = self.current_user.get('user_id')
        if not user_id_to_set:
             return False

        success = self.set_preferred_theme_for_user(user_id_to_set, theme_name)
        if success and self.current_user:
             self.current_user['preferred_theme'] = theme_name # Update local cache
        return success

    def _hash_password(self, password):
        """
        Hash a password for storage.
        """
        return hashlib.sha256(password.encode()).hexdigest()

if __name__ == "__main__":
    # Test the authentication system
    auth = UserAuth()

    # Register a test user
    success, message = auth.register_user("testuser", "password123")
    print(f"Register: {success}, {message}")

    # Login with the test user
    success, message = auth.login("testuser", "password123")
    print(f"Login: {success}, {message}")

    # Check if logged in
    print(f"Logged in: {auth.is_logged_in()}")

    # Get user data
    print(f"User data: {auth.get_user_data()}")

    # Logout
    auth.logout()
    print(f"After logout - Logged in: {auth.is_logged_in()}")

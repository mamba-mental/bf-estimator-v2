import sqlite3

DB_FILE = 'history.db'

def add_muscle_gain_column():
    """Adds the muscle_gain column to the weekly_progress table if it doesn't exist."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(weekly_progress)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'muscle_gain' not in columns:
            print("Adding column 'muscle_gain' to table 'weekly_progress'...")
            # Add the column, allowing NULL values initially or defaulting to 0
            cursor.execute("ALTER TABLE weekly_progress ADD COLUMN muscle_gain REAL DEFAULT 0") 
            conn.commit()
            print("Column 'muscle_gain' added successfully.")
        else:
            print("Column 'muscle_gain' already exists in 'weekly_progress'.")
            
    except sqlite3.Error as e:
        print(f"Database error adding muscle_gain column: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_muscle_gain_column()
    print("Database schema update attempt finished.")

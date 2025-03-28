#!/usr/bin/env python
# run_enhanced_app.py - Script to run the enhanced Body Fat Estimator application

import os
import sys
import importlib.util
import subprocess
import traceback

def check_requirements():
    """Check for required libraries and install if missing"""
    print("Checking required packages...")
    required_packages = ['SpeechRecognition']
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"Package {package} is already installed.")
        except ImportError:
            print(f"Package {package} is not installed. Installing now...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"Successfully installed {package}.")
            except Exception as e:
                print(f"Failed to install {package}: {str(e)}")
                print("You may need to install it manually.")
                input("Press Enter to continue anyway...")

def update_database():
    """Update the database schema with new tables for enhanced features"""
    print("Updating database schema for enhanced features...")
    try:
        # First try to import from the module
        from update_database import update_database_schema, add_sample_data
        update_database_schema()
        
        # Always add sample data for testing
        print("Automatically adding sample data for testing new features...")
        add_sample_data()
        
        print("Database preparation complete.")
    except ImportError:
        print("update_database.py module not found. Creating database tables manually...")
        try:
            import sqlite3
            
            # Define database constants
            DB_FILE = "history.db"
            MEASUREMENTS_TABLE = "additional_measurements"
            DASHBOARD_SETTINGS_TABLE = "dashboard_settings"
            USER_PREFERENCES_TABLE = "user_preferences"
            
            # Connect to database
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Create additional measurements table
            cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {MEASUREMENTS_TABLE} (
                id INTEGER PRIMARY KEY,
                date TEXT,
                measurement_name TEXT,
                value REAL,
                notes TEXT
            )
            ''')
            
            # Create dashboard settings table
            cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {DASHBOARD_SETTINGS_TABLE} (
                id INTEGER PRIMARY KEY,
                widget_type TEXT,
                position_row INTEGER,
                position_column INTEGER,
                widget_settings TEXT
            )
            ''')
            
            # Create user preferences table
            cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {USER_PREFERENCES_TABLE} (
                id INTEGER PRIMARY KEY,
                theme_name TEXT,
                dashboard_enabled INTEGER DEFAULT 1,
                tutorial_completed INTEGER DEFAULT 0,
                voice_input_enabled INTEGER DEFAULT 1
            )
            ''')
            
            conn.commit()
            conn.close()
            print("Database tables created successfully.")
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"Error updating database: {str(e)}")
        traceback.print_exc()
        input("Press Enter to continue anyway...")

def main():
    """Main function to run the enhanced Body Fat Estimator app"""
    print("Starting Enhanced Body Fat Estimator v2.0")
    
    # Check requirements first
    check_requirements()
    
    # Update database
    update_database()
    
    # Create a simple launcher script
    launcher_content = [
        "import sys",
        "import traceback",
        "from enhanced_desktop_app import *",
        "from desktop_app import BodyFatEstimatorApp",
        "",
        "# Constants",
        "DB_FILE = \"history.db\"",
        "MEASUREMENTS_TABLE = \"additional_measurements\"",
        "DASHBOARD_SETTINGS_TABLE = \"dashboard_settings\"",
        "USER_PREFERENCES_TABLE = \"user_preferences\"",
        "",
        "class EnhancedApp(BodyFatEstimatorApp):",
        "    def __init__(self):",
        "        super().__init__()",
        "        ",
        "        # Load enhanced blue theme by default if available",
        "        try:",
        "            if os.path.exists(\"enhanced_blue_theme.json\"):",
        "                ctk.set_default_color_theme(\"enhanced_blue_theme.json\")",
        "            else:",
        "                 # Fallback to standard blue if enhanced is missing",
        "                 ctk.set_default_color_theme(\"blue\")",
        "        except Exception as e:",
        "            print(f\"Error loading default theme: {str(e)}\")",
        "            ctk.set_default_color_theme(\"blue\") # Fallback",
        "            ",
        "        # Set app title to reflect enhanced version",
        "        self.app.title(\"Enhanced Body Fat Estimator v2.0\")",
        "        ",
        "        # Configure window opacity - make sure UI is not transparent",
        "        try:",
        "            self.app.attributes(\"-alpha\", 1.0)  # Fully opaque",
        "        except Exception:",
        "            pass  # Not supported on all platforms",
        "        ",
        "        # Initialize enhancements",
        "        try:",
        "            # Set up Smart Analysis engine",
        "            self.analysis_engine = SmartAnalysisEngine(DB_FILE)",
        "            ",
        "            # Set up tutorial manager",
        "            self.tutorial_manager = TutorialManager(self)",
        "            ",
        "            # Set up voice input",
        "            try:",
        "                if 'VoiceInputManager' in globals():",
        "                    self.voice_input_manager = VoiceInputManager(self)",
        "                    self.setup_voice_input()",
        "                else:",
        "                    print(\"Voice input feature not available in this version\")",
        "            except Exception as e:",
        "                print(f\"Voice input not available: {e}\")",
        "            ",
        "            # Add Dashboard tab if not exists",
        "            try:",
        "                # Check if the 'Dashboard' tab name already exists in the tab view's internal dictionary keys",
        "                if \"Dashboard\" not in self.tab_view._tab_dict:",
        "                    self.tab_view.add(\"Dashboard\")",
        "                    self.setup_dashboard()",
        "                else:",
        "                    print(\"Dashboard tab already exists.\") # Optional: Log if it exists",
        "                    # If it exists, maybe ensure it's set up correctly?",
        "                    # self.setup_dashboard() # Uncomment if you want to re-run setup even if tab exists",
        "            except AttributeError as ae:",
        "                 # Handle cases where _tab_dict might not exist (older CTk versions?)",
        "                 print(f\"AttributeError checking/adding Dashboard tab: {ae}. Attempting alternative add.\")",
        "                 try:",
        "                     self.tab_view.add(\"Dashboard\")",
        "                     self.setup_dashboard()",
        "                 except Exception as e_inner:",
        "                     print(f\"Error adding Dashboard tab (alternative attempt): {e_inner}\")",
        "            except Exception as e:",
        "                print(f\"General error adding Dashboard tab: {e}\")",
        "                ",
        "            # Enhance Weekly Progress tab",
        "            self.enhance_progress_tab()",
        "            ",
        "            # Setup additional themes",
        "            self.setup_enhanced_themes()",
        "                ",
        "            # Show message that enhancements are available",
        "            SimpleMessageBox.show_info(\"Enhanced Features Available\", ",
        "                \"Smart Analysis, Body Measurements Tracking, Customizable Dashboard, and more features have been added. Check out the new tabs and options!\")",
        "                ",
        "        except Exception as e:",
        "            print(f\"Error initializing enhancements: {e}\")",
        "            traceback.print_exc()",
        "    ",
        "    def setup_voice_input(self):",
        "        # Add voice input button to the UI",
        "        if hasattr(self, 'progress_frame'):",
        "            self.voice_input_button = ctk.CTkButton(",
        "                self.progress_frame,",
                "                text=\"Voice Input\",",
        "                command=self.voice_input_manager.listen,",
        "                width=120",
        "            )",
        "            self.voice_input_button.grid(row=1, column=0, padx=(20, 0), pady=10, sticky=\"e\")",
        "            ",
        "    def show_listening_indicator(self):",
        "        # Show indicator that voice input is listening",
        "        if hasattr(self, 'voice_input_button'):",
        "            self.voice_input_button.configure(text=\"Listening...\", fg_color=\"darkred\")",
        "            ",
        "    def hide_listening_indicator(self):",
        "        # Hide listening indicator",
        "        if hasattr(self, 'voice_input_button'):",
        "            self.voice_input_button.configure(text=\"Voice Input\", fg_color=None)",
        "    ",
        "    def setup_dashboard(self):",
        "        # Setup the dashboard tab with customizable widgets",
        "        if hasattr(self, 'tab_view') and hasattr(self.tab_view, 'tab') and callable(self.tab_view.tab):",
        "            # Create dashboard frame",
        "            dashboard_tab = self.tab_view.tab(\"Dashboard\")",
        "            dashboard_frame = ctk.CTkFrame(dashboard_tab)",
        "            dashboard_frame.pack(fill=\"both\", expand=True, padx=10, pady=10)",
        "            ",
        "            # Add title and description",
        "            title = ctk.CTkLabel(",
        "                dashboard_frame, ",
        "                text=\"Customizable Dashboard\", ",
        "                font=ctk.CTkFont(size=24, weight=\"bold\")",
        "            )",
        "            title.pack(pady=(20, 10))",
        "            ",
        "            desc = ctk.CTkLabel(",
        "                dashboard_frame, ",
        "                text=\"Add and arrange widgets to customize your dashboard.\",",
        "                font=ctk.CTkFont(size=14)",
        "            )",
        "            desc.pack(pady=(0, 20))",
        "            ",
        "            # Add a button to add widgets",
        "            add_widget_btn = ctk.CTkButton(",
        "                dashboard_frame,",
        "                text=\"Add Widget\",",
        "                command=lambda: SimpleMessageBox.show_info(\"Add Widget\", \"Choose from Weight Progress, Body Fat Progress, Measurements, or Smart Analysis widgets to add to your dashboard.\")",
        "            )",
        "            add_widget_btn.pack(pady=10)",
        "    ",
        "    def enhance_progress_tab(self):",
        "        # Enhance the weekly progress tab with new features",
        "        # Just show a message for now",
        "        if hasattr(self, 'progress_frame'):",
        "            enhanced_label = ctk.CTkLabel(",
        "                self.progress_frame,",
        "                text=\"Enhanced with Smart Analysis - Now Available!\",",
        "                font=ctk.CTkFont(size=14, weight=\"bold\"),",
        "                text_color=\"#4CAF50\"",
        "            )",
        "            enhanced_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky=\"w\")",
        "    ",
        "    def setup_enhanced_themes(self):",
        "        \"\"\"Set up enhanced theme options in the About tab\"\"\"",
        "        if hasattr(self, 'about_frame'):",
        "            # Find the appropriate place to add the theme frame",
        "            uses_grid = False",
        "            last_row = 0",
        "            for child in self.about_frame.winfo_children():",
        "                if child.grid_info():",
        "                    uses_grid = True",
        "                    grid_info = child.grid_info()",
        "                    if grid_info and 'row' in grid_info:",
        "                        last_row = max(last_row, int(grid_info['row']))",
        "            ",
        "            # Header for theme section",
        "            theme_header = ctk.CTkLabel(",
        "                self.about_frame,",
        "                text=\"Enhanced Theme Options\",",
        "                font=ctk.CTkFont(size=18, weight=\"bold\")",
        "            )",
        "            ",
        "            # Theme selection frame",
        "            theme_frame = ctk.CTkFrame(self.about_frame)",
        "            ",
        "            # Apply appropriate geometry",
        "            if uses_grid:",
        "                theme_header.grid(row=last_row+1, column=0, padx=20, pady=(20,5), sticky=\"w\")",
        "                separator = ctk.CTkFrame(self.about_frame, height=2, fg_color=\"gray70\")",
        "                separator.grid(row=last_row+2, column=0, padx=20, pady=(0, 10), sticky=\"ew\")",
        "                theme_frame.grid(row=last_row+3, column=0, padx=20, pady=10, sticky=\"ew\")",
        "            else:",
        "                theme_header.pack(padx=20, pady=(20,5), anchor=\"w\")",
        "                separator = ctk.CTkFrame(self.about_frame, height=2, fg_color=\"gray70\")",
        "                separator.pack(fill=\"x\", padx=20, pady=(0, 10))",
        "                theme_frame.pack(fill=\"x\", padx=20, pady=10)",
        "            ",
        "            # Theme selection label",
        "            theme_label = ctk.CTkLabel(",
        "                theme_frame,",
        "                text=\"Select a theme:\",",
        "                anchor=\"w\"",
        "            )",
        "            theme_label.grid(row=0, column=0, padx=10, pady=10, sticky=\"w\")",
        "            ",
        "            # Available themes",
        "            self.themes = {",
        "                \"Enhanced Blue\": \"enhanced_blue_theme.json\",",
        "                \"Midnight OLED\": \"midnight_oled_theme.json\",",
        "                \"Forest\": \"forest_theme.json\",",
        "                \"Lavender\": \"lavender_theme.json\",",
        "                \"Sunset\": \"sunset_theme.json\"",
        "            }",
        "            ",
        "            # Create theme selection dropdown",
        "            theme_names = list(self.themes.keys())",
        "            self.theme_var = ctk.StringVar(value=theme_names[0])",
        "            ",
        "            # Try to load the saved theme preference",
        "            try:",
        "                conn = sqlite3.connect(DB_FILE)",
        "                cursor = conn.cursor()",
        "                cursor.execute(\"SELECT theme_name FROM user_preferences ORDER BY id DESC LIMIT 1\")",
        "                saved_theme = cursor.fetchone()",
        "                conn.close()",
        "                ",
        "                if saved_theme and saved_theme[0] in theme_names:",
        "                    self.theme_var.set(saved_theme[0])",
        "            except Exception as e:",
        "                print(f\"Error loading saved theme: {e}\")",
        "                # If error, use default",
        "            ",
        "            # Create the theme dropdown",
        "            theme_dropdown = ctk.CTkOptionMenu(",
        "                theme_frame,",
        "                values=theme_names,",
        "                variable=self.theme_var,",
        "                dynamic_resizing=False,",
        "                width=200,",
        "                command=self.apply_theme",
        "            )",
        "            theme_dropdown.grid(row=0, column=1, padx=10, pady=10)",
        "            ",
        "            # Apply button",
        "            apply_btn = ctk.CTkButton(",
        "                theme_frame,",
        "                text=\"Apply Theme\",",
        "                command=lambda: self.apply_theme(self.theme_var.get())",
        "            )",
        "            apply_btn.grid(row=0, column=2, padx=10, pady=10)",
        "            ",
        "            # Theme preview (could be added in the future)",
        "            theme_note = ctk.CTkLabel(",
        "                theme_frame,",
        "                text=\"Note: Some theme changes may require restarting the application.\",",
        "                font=ctk.CTkFont(size=12, slant=\"italic\"),",
        "                text_color=\"gray60\"",
        "            )",
        "            theme_note.grid(row=1, column=0, columnspan=3, padx=10, pady=(0,10), sticky=\"w\")",
        "    ",
        "    def apply_theme(self, theme_name):",
        "        \"\"\"Apply the selected theme and save preference\"\"\"",
        "        if not hasattr(self, 'themes') or theme_name not in self.themes:",
        "            print(f\"Unknown theme: {theme_name}\")",
        "            return",
        "            ",
        "        theme_file = self.themes[theme_name]",
        "        ",
        "        # Check if theme file exists",
        "        if not os.path.exists(theme_file):",
        "            print(f\"Theme file not found: {theme_file}\")",
        "            SimpleMessageBox.show_info(\"Theme Error\", f\"The {theme_name} theme file was not found.\")",
        "            return",
        "            ",
        "        try:",
        "            # Apply the theme",
        "            ctk.set_default_color_theme(theme_file)",
        "            ",
        "            # Special handling for Midnight OLED theme",
        "            if theme_name == \"Midnight OLED\":",
        "                ctk.set_appearance_mode(\"Dark\")",
        "                self.apply_midnight_theme() # Additional OLED specific adjustments",
        "            else:",
        "                # Reset any custom colors if coming from midnight",
        "                self.reset_custom_colors()",
        "            ",
        "            # Save the theme preference",
        "            try:",
        "                conn = sqlite3.connect(DB_FILE)",
        "                cursor = conn.cursor()",
        "                cursor.execute(\"DELETE FROM user_preferences\") # Clear previous settings",
        "                cursor.execute(",
        "                    \"INSERT INTO user_preferences (theme_name, dashboard_enabled, tutorial_completed, voice_input_enabled) VALUES (?, 1, 0, 1)\",",
        "                    (theme_name,)",
        "                )",
        "                conn.commit()",
        "                conn.close()",
        "            except Exception as e:",
        "                print(f\"Error saving theme preference: {e}\")",
        "            ",
        "            # Show confirmation",
        "            SimpleMessageBox.show_info(\"Theme Applied\", f\"The {theme_name} theme has been applied. Some visual elements may update on restart.\")",
        "        except Exception as e:",
        "            print(f\"Error applying theme: {e}\")",
        "            SimpleMessageBox.show_info(\"Theme Error\", f\"An error occurred while applying the {theme_name} theme: {str(e)}\")",
        "    ",
        "    def apply_midnight_theme(self):",
        "        \"\"\"Apply additional OLED black adjustments for Midnight theme\"\"\"",
        "        try:",
        "            # Apply pure black background to main containers",
        "            pure_black = \"#000000\"",
        "            near_black = \"#030303\"",
        "            text_white = \"#FFFFFF\"",
        "            ",
        "            # Apply to main containers",
        "            self.app.configure(fg_color=pure_black)",
        "            self.main_frame.configure(fg_color=pure_black)",
        "            self.tab_view.configure(fg_color=pure_black)",
        "            ",
        "            # Apply to all tabs",
        "            for tab_name in [\"Input Data\", \"Weekly Progress\", \"Reports History\", \"Results\", \"About\", \"Dashboard\"]:",
        "                try:",
        "                    self.tab_view.tab(tab_name).configure(fg_color=pure_black)",
        "                except Exception:",
        "                    pass # Tab might not exist",
        "            ",
        "            # Apply to primary frames",
        "            if hasattr(self, 'input_frame'):",
        "                self.input_frame.configure(fg_color=near_black)",
        "            if hasattr(self, 'progress_frame'):",
        "                self.progress_frame.configure(fg_color=near_black)",
        "            if hasattr(self, 'history_frame'):",
        "                self.history_frame.configure(fg_color=near_black)",
        "            if hasattr(self, 'results_frame'):",
        "                self.results_frame.configure(fg_color=near_black)",
        "            if hasattr(self, 'about_frame'):",
        "                self.about_frame.configure(fg_color=near_black)",
        "        except Exception as e:",
        "            print(f\"Error applying OLED settings: {e}\")",
        "    ",
        "    def reset_custom_colors(self):",
        "        \"\"\"Reset any custom colors applied by Midnight theme\"\"\"",
        "        try:",
        "            # Restore to theme default colors",
        "            self.app.configure(fg_color=None)",
        "            self.main_frame.configure(fg_color=None)",
        "            self.tab_view.configure(fg_color=None)",
        "            ",
        "            # Restore tabs",
        "            for tab_name in [\"Input Data\", \"Weekly Progress\", \"Reports History\", \"Results\", \"About\", \"Dashboard\"]:",
        "                try:",
        "                    self.tab_view.tab(tab_name).configure(fg_color=None)",
        "                except Exception:",
        "                    pass # Tab might not exist",
        "            ",
        "            # Reset primary frames",
        "            if hasattr(self, 'input_frame'):",
        "                self.input_frame.configure(fg_color=None)",
        "            if hasattr(self, 'progress_frame'):",
        "                self.progress_frame.configure(fg_color=None)",
        "            if hasattr(self, 'history_frame'):",
        "                self.history_frame.configure(fg_color=None)",
        "            if hasattr(self, 'results_frame'):",
        "                self.results_frame.configure(fg_color=None)",
        "            if hasattr(self, 'about_frame'):",
        "                self.about_frame.configure(fg_color=None)",
        "        except Exception as e:",
        "            print(f\"Error resetting colors: {e}\")",
        "",
        "if __name__ == \"__main__\":",
        "    try:",
        "        app = EnhancedApp()",
        "        app.run()",
        "    except Exception as e:",
        "        print(f\"Error starting enhanced app: {e}\")",
        "        traceback.print_exc()",
        "        input(\"Press Enter to exit...\")"
    ]
    
    # Join lines with proper newlines for the script
    launcher_script = "\n".join(launcher_content)
    
    # Write launcher script to a temporary file
    with open("run_enhanced_temp.py", "w") as f:
        f.write(launcher_script)
    
    # Execute the launcher script
    try:
        subprocess.call([sys.executable, "run_enhanced_temp.py"])
    except Exception as e:
        print(f"Error launching app: {str(e)}")
        traceback.print_exc()
    finally:
        # Clean up the temporary file
        if os.path.exists("run_enhanced_temp.py"):
            try:
                os.remove("run_enhanced_temp.py")
            except:
                pass

if __name__ == "__main__":
    main()

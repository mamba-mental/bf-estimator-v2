#!/usr/bin/env python
# settings_tab.py - User settings management for Body Fat Estimator
import os
import json
import sqlite3
import customtkinter as ctk
from tkinter import filedialog
from datetime import datetime

class SettingsTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.user_id = app.current_user_id
        self.settings = {}
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        self.container = ctk.CTkFrame(self.parent)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Theme Selection
        self.theme_frame = ctk.CTkFrame(self.container)
        self.theme_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(self.theme_frame, text="Appearance", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.theme_var = ctk.StringVar(value="system")
        theme_options = ["Light", "Dark", "System Default", "Midnight OLED", "Forest", "Sunset"]
        self.theme_menu = ctk.CTkOptionMenu(self.theme_frame, variable=self.theme_var, values=theme_options)
        self.theme_menu.pack(pady=5)
        
        # Notification Preferences
        self.notify_frame = ctk.CTkFrame(self.container)
        self.notify_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(self.notify_frame, text="Notifications", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.email_notify = ctk.CTkCheckBox(self.notify_frame, text="Email Notifications")
        self.email_notify.pack(side="left", padx=5)
        self.sms_notify = ctk.CTkCheckBox(self.notify_frame, text="SMS Notifications")
        self.sms_notify.pack(side="left", padx=5)
        
        # Account Management
        self.account_frame = ctk.CTkFrame(self.container)
        self.account_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(self.account_frame, text="Account", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.name_entry = ctk.CTkEntry(self.account_frame, placeholder_text="Full Name")
        self.name_entry.pack(pady=5, fill="x")
        self.email_entry = ctk.CTkEntry(self.account_frame, placeholder_text="Email")
        self.email_entry.pack(pady=5, fill="x")
        self.phone_entry = ctk.CTkEntry(self.account_frame, placeholder_text="Phone")
        self.phone_entry.pack(pady=5, fill="x")
        
        # Data Management
        self.data_frame = ctk.CTkFrame(self.container)
        self.data_frame.pack(fill="x", pady=10)
        ctk.CTkButton(self.data_frame, text="Export Data", command=self.export_data).pack(side="left", padx=5)
        ctk.CTkButton(self.data_frame, text="Import Data", command=self.import_data).pack(side="left", padx=5)
        
        # Save Button
        ctk.CTkButton(self.container, text="Save Settings", command=self.save_settings).pack(pady=20)

    def load_settings(self):
        conn = sqlite3.connect('history.db')
        try:
            cursor = conn.cursor()
            # Load user profile data
            cursor.execute('''SELECT user_name, email, phone, theme, notify_email, notify_sms 
                           FROM user_profiles WHERE id = ?''', (self.user_id,))
            profile_data = cursor.fetchone()
            
            if profile_data:
                self.name_entry.insert(0, profile_data[0])
                self.email_entry.insert(0, profile_data[1])
                self.phone_entry.insert(0, profile_data[2])
                self.theme_var.set(profile_data[3])
                self.email_notify.select() if profile_data[4] else self.email_notify.deselect()
                self.sms_notify.select() if profile_data[5] else self.sms_notify.deselect()
                
            # Load export settings
            cursor.execute('''SELECT export_path, last_backup FROM user_settings WHERE user_id = ?''', (self.user_id,))
            export_data = cursor.fetchone()
            if export_data:
                self.settings['export_path'] = export_data[0]
                self.settings['last_backup'] = export_data[1]
                
        except sqlite3.Error as e:
            print(f"Error loading settings: {e}")
        finally:
            conn.close()

    def save_settings(self):
        conn = sqlite3.connect('history.db')
        try:
            cursor = conn.cursor()
            # Update user profile
            cursor.execute('''UPDATE user_profiles SET
                           user_name = ?, email = ?, phone = ?, theme = ?, 
                           notify_email = ?, notify_sms = ?
                           WHERE id = ?''', (
                               self.name_entry.get(),
                               self.email_entry.get(),
                               self.phone_entry.get(),
                               self.theme_var.get(),
                               1 if self.email_notify.get() else 0,
                               1 if self.sms_notify.get() else 0,
                               self.user_id
                           ))
            # Update user settings
            cursor.execute('''INSERT OR REPLACE INTO user_settings 
                           (user_id, export_path, last_backup)
                           VALUES (?, ?, ?)''', (
                               self.user_id,
                               self.settings.get('export_path', ''),
                               self.settings.get('last_backup', '')
                           ))
            conn.commit()
            self.parent.show_success("Settings saved successfully!")
            self.apply_theme()
        except sqlite3.Error as e:
            print(f"Error saving settings: {e}")
            conn.rollback()
        finally:
            conn.close()

    def apply_theme(self):
        theme = self.theme_var.get().lower()
        if theme == "system default":
            ctk.set_appearance_mode("system")
        else:
            ctk.set_appearance_mode(theme)

    def export_data(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            try:
                conn = sqlite3.connect('history.db')
                export_data = {
                    'profile': conn.execute('''SELECT * FROM user_profiles WHERE id = ?''', 
                                          (self.user_id,)).fetchone(),
                    'measurements': conn.execute('''SELECT * FROM initial_measurements 
                                                  WHERE user_id = ?''', (self.user_id,)).fetchall(),
                    'weekly_updates': conn.execute('''SELECT * FROM weekly_updates 
                                                    WHERE user_id = ?''', (self.user_id,)).fetchall()
                }
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                self.settings['export_path'] = file_path
                self.settings['last_backup'] = datetime.now().isoformat()
                self.save_settings()
                self.parent.show_success(f"Data exported successfully to {file_path}")
            except Exception as e:
                self.parent.show_error(f"Export failed: {str(e)}")

    def import_data(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            try:
                with open(file_path) as f:
                    import_data = json.load(f)
                
                conn = sqlite3.connect('history.db')
                # Update profile
                conn.execute('''UPDATE user_profiles SET 
                             user_name=?, email=?, phone=?, theme=?, 
                             notify_email=?, notify_sms=? WHERE id=?''', 
                             (*import_data['profile'][1:7], self.user_id))
                # Clear existing data
                conn.execute('DELETE FROM initial_measurements WHERE user_id = ?', (self.user_id,))
                conn.execute('DELETE FROM weekly_updates WHERE user_id = ?', (self.user_id,))
                # Import new data
                conn.executemany('''INSERT INTO initial_measurements 
                                 VALUES (?,?,?,?,?,?,?,?,?,?)''', 
                                 import_data['measurements'])
                conn.executemany('''INSERT INTO weekly_updates 
                                 VALUES (?,?,?,?,?,?,?,?,?,?)''', 
                                 import_data['weekly_updates'])
                conn.commit()
                self.load_settings()
                self.parent.show_success("Data imported successfully!")
            except Exception as e:
                self.parent.show_error(f"Import failed: {str(e)}")

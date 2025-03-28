#!/usr/bin/env python
# weekly_updates_ui.py - Weekly Updates Form for Body Fat Estimator
# Created: 03/28/25
# Description: Implementation of weekly updates form for the Body Fat Estimator app

import os
import sys
import sqlite3
import customtkinter as ctk
from datetime import datetime
from tkinter import filedialog
import traceback

class WeeklyUpdatesUI:
    """Class to handle weekly updates form and data collection"""

    def __init__(self, app_instance, input_frame, variables_dict):
        """
        Initialize the weekly updates UI manager

        Args:
            app_instance: The parent app instance
            input_frame: The frame where the input form is placed
            variables_dict: The dictionary to store form variables
        """
        self.app = app_instance
        self.input_frame = input_frame
        self.variables = variables_dict
        self.tooltips = {}  # To store tooltips

    def create_section_header(self, text, row, col, colspan=2):
        """Create a section header with title and separator"""
        # Title
        header = ctk.CTkLabel(
            self.input_frame,
            text=text,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.grid(row=row, column=col, columnspan=colspan, padx=10, pady=(15, 5), sticky="w")

        # Separator
        separator = ctk.CTkFrame(self.input_frame, height=2, fg_color="gray70")
        separator.grid(row=row+1, column=col, columnspan=colspan, padx=10, pady=(0, 10), sticky="ew")
        return row + 2  # Return the next available row

    def create_form_field(self, name, label, data_type, row, col, tooltip=None):
        """Create a form field with label and entry"""
        frame = ctk.CTkFrame(self.input_frame)
        frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)

        # Label
        lbl = ctk.CTkLabel(frame, text=label, width=150, anchor="w")
        lbl.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Create variable of appropriate type
        if data_type == "float":
            var = ctk.DoubleVar()
        elif data_type == "int":
            var = ctk.IntVar()
        else:
            var = ctk.StringVar()

        # Entry field
        entry = ctk.CTkEntry(frame, textvariable=var, width=200)
        entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Store variable
        self.variables[name] = var

        # Add tooltip if provided
        if tooltip:
            self.create_tooltip(entry, tooltip)

        return row + 1  # Return the next available row

    def create_dropdown(self, name, label, options, row, col, tooltip=None):
        """Create a dropdown field with label"""
        frame = ctk.CTkFrame(self.input_frame)
        frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)

        # Label
        lbl = ctk.CTkLabel(frame, text=label, width=150, anchor="w")
        lbl.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Variable
        var = ctk.StringVar()

        # Dropdown - Ensure options are strings
        str_options = [str(opt) for opt in options]
        dropdown = ctk.CTkOptionMenu(frame, variable=var, values=str_options)
        dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        if str_options:
             dropdown.set(str_options[0])  # Set default value

        # Store variable
        self.variables[name] = var

        # Add tooltip if provided
        if tooltip:
            self.create_tooltip(dropdown, tooltip)

        return row + 1  # Return the next available row

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""

        # Create tooltip window
        def show_tooltip(event=None):
            tooltip = ctk.CTkToplevel(widget)
            tooltip.attributes('-topmost', True)  # Ensure tooltip stays on top
            tooltip.overrideredirect(True)  # Remove window decorations

            # Create label with tooltip text
            label = ctk.CTkLabel(
                tooltip,
                text=text,
                wraplength=300,
                justify="left",
                corner_radius=6,
                fg_color="#333333",
                text_color="#FFFFFF"
            )
            label.pack(padx=5, pady=5)

            # Position tooltip near widget
            x = widget.winfo_rootx() + widget.winfo_width()
            y = widget.winfo_rooty()
            tooltip.geometry(f"+{x}+{y}")

            # Store tooltip reference and schedule destruction
            self.tooltips[widget] = tooltip
            widget.after(3000, lambda: destroy_tooltip(tooltip))

        def destroy_tooltip(tooltip):
            if tooltip.winfo_exists():
                tooltip.destroy()

        def leave_tooltip(event=None):
            if widget in self.tooltips and self.tooltips[widget].winfo_exists():
                self.tooltips[widget].destroy()
                del self.tooltips[widget]

        # Bind events
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", leave_tooltip)

    def setup_weekly_updates_form(self, start_row=0):
        """Setup weekly updates form fields"""
        row = start_row

        # Section header
        row = self.create_section_header("Weekly Updates", row, 0, 2)

        # Current weight
        row = self.create_form_field("current_weight", "Current Weight (lbs)", "float", row, 0,
            tooltip="Your current weight")

        # Current body fat percentage
        row = self.create_form_field("current_bf", "Current Body Fat (%)", "float", row, 1,
            tooltip="Your current body fat percentage")

        # Protein intake
        row = self.create_form_field("protein_intake", "Protein Intake (g)", "float", row+1, 0,
            tooltip="Your average daily protein intake in grams")

        # Carbohydrate intake
        row = self.create_form_field("carb_intake", "Carbohydrate Intake (g)", "float", row, 1,
            tooltip="Your average daily carbohydrate intake in grams")

        # Fat intake
        row = self.create_form_field("fat_intake", "Fat Intake (g)", "float", row+1, 0,
            tooltip="Your average daily fat intake in grams")

        # Notes
        row = self.create_form_field("notes", "Notes", "str", row, 1,
            tooltip="Any challenges, wins, or feedback")

        # Date picker
        row = self.create_form_field("update_date", "Date", "str", row+1, 0,
            tooltip="Select the date for this update")

        # Photo upload
        row = self.create_photo_upload(row, 1)

        return row  # Return the final row number

    def create_photo_upload(self, row, col):
        """Create a photo upload field"""
        frame = ctk.CTkFrame(self.input_frame)
        frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)

        # Label
        lbl = ctk.CTkLabel(frame, text="Upload Photo", width=150, anchor="w")
        lbl.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Variable
        var = ctk.StringVar()

        # Button to open file dialog
        def open_file_dialog():
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
            var.set(file_path)

        button = ctk.CTkButton(frame, text="Browse", command=open_file_dialog)
        button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Store variable
        self.variables["photo_path"] = var

        return row + 1  # Return the next available row

    def get_weekly_updates_data(self):
        """Get all weekly updates data as a dictionary"""
        data = {}
        for name, var in self.variables.items():
            value = var.get()
            if name in ['current_weight', 'current_bf', 'protein_intake', 'carb_intake', 'fat_intake']:
                data[name] = float(value) if value else 0.0
            else:
                data[name] = str(value)

        return data

    def save_weekly_updates(self, user_id):
        """Save weekly updates data to database"""
        try:
            # Connect to database
            conn = sqlite3.connect("history.db")
            cursor = conn.cursor()

            # Get data
            data = self.get_weekly_updates_data()

            # Set current time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Insert new entry
            cursor.execute("""
                INSERT INTO weekly_updates (
                user_id, date, weight, body_fat, protein_intake, carb_intake, fat_intake, notes, photo_path, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                data.get('update_date', current_time),
                data.get('current_weight', 0.0),
                data.get('current_bf', 0.0),
                data.get('protein_intake', 0.0),
                data.get('carb_intake', 0.0),
                data.get('fat_intake', 0.0),
                data.get('notes', ''),
                data.get('photo_path', ''),
                current_time
            ))

            conn.commit()
            conn.close()
            print("Weekly updates saved successfully")

        except Exception as e:
            print(f"Error saving weekly updates: {e}")
            traceback.print_exc()

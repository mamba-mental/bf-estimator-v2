#!/usr/bin/env python
# dashboard_integration.py - Integration module for dashboard and settings components
# Created: 03/27/25

import customtkinter as ctk
import sqlite3
import os
import json
from typing import Optional, Dict, Any, List, Callable, Union

# Import dashboard widgets
from dashboard_widgets import (
    WeightTrackingWidget,
    BodyFatWidget,
    SmartAnalysisWidget,
    MeasurementsWidget,
    GoalsProgressWidget
)

# Import settings tab
from settings_tab import SettingsTab

# Constants
DB_FILE = "history.db"
USER_PREFS_TABLE = "user_preferences"
DASHBOARD_SETTINGS_TABLE = "dashboard_settings"

class DashboardManager:
    """Manager class for the dashboard tab and widgets"""
    
    def __init__(self, app_instance=None):
        self.app_instance = app_instance
        self.dashboard_tab = None
        self.widgets = {}
        self.widget_frames = {}
        self.enabled = True
        self.analysis_engine = None
    
    def create_dashboard_tab(self, tab_view, tab_name="Dashboard"):
        """Create and set up the dashboard tab with widgets"""
        # Create the dashboard tab if it doesn't exist
        if tab_name not in tab_view._tab_dict:
            self.dashboard_tab = tab_view.add(tab_name)
        else:
            self.dashboard_tab = tab_view.tab(tab_name)
        
        # Main dashboard frame
        main_frame = ctk.CTkFrame(self.dashboard_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header section
        header_frame = ctk.CTkFrame(main_frame, height=40, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        refresh_all_btn = ctk.CTkButton(
            header_frame,
            text="Refresh All",
            command=self.refresh_all_widgets,
            width=120,
            height=30
        )
        refresh_all_btn.pack(side="right", padx=10)
        
        # Create grid layout for widgets
        grid_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=10, pady=10)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.columnconfigure(2, weight=1)
        grid_frame.rowconfigure(0, weight=1)
        grid_frame.rowconfigure(1, weight=1)
        
        # Add widgets
        self.create_widgets(grid_frame)
        
        return self.dashboard_tab
    
    def create_widgets(self, parent_frame):
        """Create and arrange dashboard widgets"""
        # Load widget settings from database
        widget_settings = self.load_widget_settings()
        
        # Layout is 3x2 grid (6 widgets maximum)
        # -----------------------
        # | Weight | BodyFat | Smart  |
        # | Track  | %       | Analysis|
        # -----------------------
        # | Measure| Goals & | Diet   |
        # | ments  | Progress| Analysis|
        # -----------------------
        
        # Widget creation with default placement
        widget_classes = {
            "Weight Tracking": (WeightTrackingWidget, 0, 0),
            "Body Fat %": (BodyFatWidget, 0, 1),
            "Smart Analysis": (SmartAnalysisWidget, 0, 2),
            "Measurements": (MeasurementsWidget, 1, 0),
            "Goals & Progress": (GoalsProgressWidget, 1, 1),
            "Diet Analysis": (self.create_diet_analysis_widget, 1, 2)
        }
        
        # Process enabled widgets
        for name, (widget_class, row, col) in widget_classes.items():
            # Skip if disabled in settings
            if name in widget_settings and not widget_settings[name]:
                continue
            
            # Create widget
            if callable(widget_class):
                # For custom widget creation functions
                widget = widget_class(parent_frame)
            else:
                # For standard widget classes
                widget = widget_class(parent_frame)
            
            # Configure grid placement
            widget.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Store reference
            self.widgets[name] = widget
    
    def create_diet_analysis_widget(self, parent):
        """Create a diet analysis widget for nutritional information"""
        widget = ctk.CTkFrame(parent, fg_color="#2B2B2B", corner_radius=10)
        
        # Header frame with title
        header_frame = ctk.CTkFrame(widget, fg_color="#1A1A1A", corner_radius=5, height=35)
        header_frame.pack(fill="x", padx=1, pady=(1, 5))
        header_frame.pack_propagate(False)
        
        # Title label
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Diet Analysis", 
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.pack(side="left", padx=10, pady=5)
        
        # Content frame
        content_frame = ctk.CTkFrame(widget, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Current macros
        macros_label = ctk.CTkLabel(
            content_frame,
            text="Current Macronutrients:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        macros_label.pack(anchor="w", pady=(10, 5))
        
        # Macro breakdown
        self.protein_label = ctk.CTkLabel(
            content_frame, 
            text="Protein: -- g (--% of calories)",
            font=ctk.CTkFont(size=14)
        )
        self.protein_label.pack(anchor="w", pady=2)
        
        self.carb_label = ctk.CTkLabel(
            content_frame, 
            text="Carbs: -- g (--% of calories)",
            font=ctk.CTkFont(size=14)
        )
        self.carb_label.pack(anchor="w", pady=2)
        
        self.fat_label = ctk.CTkLabel(
            content_frame, 
            text="Fat: -- g (--% of calories)",
            font=ctk.CTkFont(size=14)
        )
        self.fat_label.pack(anchor="w", pady=2)
        
        self.total_calories_label = ctk.CTkLabel(
            content_frame, 
            text="Total: -- calories",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.total_calories_label.pack(anchor="w", pady=(5, 15))
        
        # Diet type
        self.diet_type_label = ctk.CTkLabel(
            content_frame, 
            text="Diet Type: --",
            font=ctk.CTkFont(size=14)
        )
        self.diet_type_label.pack(anchor="w", pady=2)
        
        # Diet quality
        self.diet_quality_label = ctk.CTkLabel(
            content_frame, 
            text="Diet Quality: --",
            font=ctk.CTkFont(size=14)
        )
        self.diet_quality_label.pack(anchor="w", pady=2)
        
        # Diet effect
        self.diet_effects_label = ctk.CTkLabel(
            content_frame, 
            text="Effects: --",
            font=ctk.CTkFont(size=14, slant="italic"),
            wraplength=200
        )
        self.diet_effects_label.pack(anchor="w", pady=(5, 10))
        
        # Refresh button
        refresh_button = ctk.CTkButton(
            widget, 
            text="Refresh", 
            command=self.refresh_diet_widget,
            width=120,
            height=28
        )
        refresh_button.pack(side="bottom", pady=(5, 10))
        
        # Store references
        self.diet_widget_elements = {
            "protein": self.protein_label,
            "carbs": self.carb_label,
            "fat": self.fat_label,
            "calories": self.total_calories_label,
            "diet_type": self.diet_type_label,
            "diet_quality": self.diet_quality_label,
            "effects": self.diet_effects_label,
        }
        
        return widget
    
    def refresh_diet_widget(self):
        """Refresh the diet analysis widget with current data"""
        try:
            # Get latest diet data from database
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Get diet information from user profile
            cursor.execute("""
                SELECT protein_intake, carb_intake, fat_intake, diet_type 
                FROM user_profiles 
                ORDER BY user_id DESC 
                LIMIT 1
            """)
            diet_data = cursor.fetchone()
            
            if diet_data:
                protein, carbs, fat, diet_type = diet_data
                
                # Calculate calories
                protein_cal = protein * 4
                carbs_cal = carbs * 4
                fat_cal = fat * 9
                total_cal = protein_cal + carbs_cal + fat_cal
                
                # Calculate percentages
                protein_pct = (protein_cal / total_cal * 100) if total_cal > 0 else 0
                carbs_pct = (carbs_cal / total_cal * 100) if total_cal > 0 else 0
                fat_pct = (fat_cal / total_cal * 100) if total_cal > 0 else 0
                
                # Update labels
                self.diet_widget_elements["protein"].configure(text=f"Protein: {protein} g ({protein_pct:.1f}% of calories)")
                self.diet_widget_elements["carbs"].configure(text=f"Carbs: {carbs} g ({carbs_pct:.1f}% of calories)")
                self.diet_widget_elements["fat"].configure(text=f"Fat: {fat} g ({fat_pct:.1f}% of calories)")
                self.diet_widget_elements["calories"].configure(text=f"Total: {total_cal:.0f} calories")
                self.diet_widget_elements["diet_type"].configure(text=f"Diet Type: {diet_type.title() if diet_type else 'Standard'}")
                
                # Evaluate diet quality
                quality = self.evaluate_diet_quality(protein, carbs, fat, diet_type)
                self.diet_widget_elements["diet_quality"].configure(text=f"Diet Quality: {quality}")
                
                # Diet effects
                effects = self.get_diet_effects(diet_type)
                self.diet_widget_elements["effects"].configure(text=f"Effects: {effects}")
                
            else:
                # Default values if no diet data
                self.diet_widget_elements["protein"].configure(text="Protein: Not set")
                self.diet_widget_elements["carbs"].configure(text="Carbs: Not set")
                self.diet_widget_elements["fat"].configure(text="Fat: Not set")
                self.diet_widget_elements["calories"].configure(text="Total: Not calculated")
                self.diet_widget_elements["diet_type"].configure(text="Diet Type: Not set")
                self.diet_widget_elements["diet_quality"].configure(text="Diet Quality: Not evaluated")
                self.diet_widget_elements["effects"].configure(text="Effects: Not available")
            
            conn.close()
            
        except Exception as e:
            print(f"Error refreshing diet widget: {e}")
            for key, label in self.diet_widget_elements.items():
                label.configure(text=f"{key.replace('_', ' ').title()}: Error")
    
    def evaluate_diet_quality(self, protein, carbs, fat, diet_type):
        """Evaluate diet quality based on macros and type"""
        try:
            # Calculate calories
            protein_cal = protein * 4
            carbs_cal = carbs * 4
            fat_cal = fat * 9
            total_cal = protein_cal + carbs_cal + fat_cal
            
            # Calculate percentages
            protein_pct = (protein_cal / total_cal * 100) if total_cal > 0 else 0
            carbs_pct = (carbs_cal / total_cal * 100) if total_cal > 0 else 0
            fat_pct = (fat_cal / total_cal * 100) if total_cal > 0 else 0
            
            # Check against diet type expectations
            if diet_type and diet_type.lower() == 'keto':
                if carbs_pct > 10:
                    return "Needs Adjustment (Too High Carbs)"
                elif fat_pct < 60:
                    return "Needs Adjustment (Too Low Fat)"
                elif protein_pct < 20:
                    return "Needs Adjustment (Too Low Protein)"
                else:
                    return "Good (Keto-Aligned)"
            
            elif diet_type and diet_type.lower() == 'low-carb':
                if carbs_pct > 25:
                    return "Needs Adjustment (Too High Carbs)"
                elif protein_pct < 20:
                    return "Needs Adjustment (Too Low Protein)"
                else:
                    return "Good (Low-Carb Aligned)"
            
            else:  # Standard diet
                # Check for balanced diet
                if protein_pct < 15:
                    return "Low Protein"
                elif fat_pct > 40:
                    return "High Fat"
                elif carbs_pct < 30:
                    return "Low Carbs"
                else:
                    return "Balanced"
        
        except Exception as e:
            print(f"Error evaluating diet quality: {e}")
            return "Not Evaluated"
    
    def get_diet_effects(self, diet_type):
        """Get description of diet effects based on type"""
        if not diet_type:
            return "Standard diet with balanced energy distribution"
            
        diet_type = diet_type.lower()
        
        if diet_type == 'keto':
            return "Enhanced fat loss, slightly reduced muscle gain potential"
        elif diet_type == 'low-carb':
            return "Moderate fat loss enhancement, minimal impact on muscle gain"
        elif diet_type == 'vegetarian':
            return "Standard fat loss, may require careful protein planning"
        elif diet_type == 'vegan':
            return "May need supplementation for optimal muscle preservation"
        else:
            return "Standard balance of fat loss and muscle preservation"
    
    def load_widget_settings(self):
        """Load widget settings from database"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Check if dashboard settings table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{DASHBOARD_SETTINGS_TABLE}'")
            if not cursor.fetchone():
                conn.close()
                return {name: True for name in [
                    "Weight Tracking", "Body Fat %", "Smart Analysis", 
                    "Measurements", "Goals & Progress", "Diet Analysis"
                ]}
            
            # Get dashboard enabled status and widget settings
            cursor.execute(f"SELECT dashboard_enabled, widgets FROM {DASHBOARD_SETTINGS_TABLE} ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                self.enabled, widgets_json = result
                self.enabled = bool(self.enabled)
                
                if widgets_json:
                    try:
                        widget_settings = json.loads(widgets_json)
                        return {name: bool(enabled) for name, enabled in widget_settings.items()}
                    except json.JSONDecodeError:
                        pass
            
            conn.close()
            
        except Exception as e:
            print(f"Error loading widget settings: {e}")
        
        # Default settings if any error or no settings found
        return {name: True for name in [
            "Weight Tracking", "Body Fat %", "Smart Analysis", 
            "Measurements", "Goals & Progress", "Diet Analysis"
        ]}
    
    def refresh_all_widgets(self):
        """Refresh all dashboard widgets"""
        for name, widget in self.widgets.items():
            if hasattr(widget, 'refresh_data'):
                widget.refresh_data()
            elif name == "Diet Analysis":
                self.refresh_diet_widget()
    
    def set_analysis_engine(self, engine):
        """Set the analysis engine for smart analysis"""
        self.analysis_engine = engine
        
        # Update smart analysis widget if it exists
        if "Smart Analysis" in self.widgets:
            smart_widget = self.widgets["Smart Analysis"]
            if hasattr(smart_widget, 'analysis_callback'):
                smart_widget.analysis_callback = self.analysis_engine.generate_analysis


class AppIntegration:
    """Integration class for dashboard and settings components"""
    
    def __init__(self, app_instance):
        self.app_instance = app_instance
        self.dashboard_manager = DashboardManager(app_instance)
        self.settings_tab = None
    
    def add_dashboard_tab(self, tab_view):
        """Add dashboard tab to the application"""
        return self.dashboard_manager.create_dashboard_tab(tab_view)
    
    def add_settings_tab(self, tab_view):
        """Add settings tab to the application"""
        settings_tab_view = tab_view.add("Settings")
        self.settings_tab = SettingsTab(settings_tab_view, self.app_instance)
        return settings_tab_view
    
    def initialize_tabs(self, tab_view):
        """Initialize both dashboard and settings tabs"""
        self.add_dashboard_tab(tab_view)
        self.add_settings_tab(tab_view)
    
    def refresh_dashboard(self):
        """Refresh all dashboard widgets"""
        self.dashboard_manager.refresh_all_widgets()
    
    def set_analysis_engine(self, engine):
        """Set the analysis engine for smart insights"""
        self.dashboard_manager.set_analysis_engine(engine)


# Test function
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Dashboard and Settings Test")
    app.geometry("1000x600")
    
    # Create tab view
    tab_view = ctk.CTkTabview(app)
    tab_view.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create integrator
    integrator = AppIntegration(app)
    integrator.initialize_tabs(tab_view)
    
    app.mainloop()

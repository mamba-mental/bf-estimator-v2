#!/usr/bin/env python
# enhanced_report_generator.py
# Created: 03/28/25
# Description: Enhanced report generation with AI analysis and visualizations

import os
import datetime
import json
import base64
import io
import traceback
import sqlite3
import numpy as np
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# Set up paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FOLDER = os.path.join(SCRIPT_DIR, "results")
TEMPLATE_FOLDER = os.path.join(SCRIPT_DIR, "templates")
CSS_FILE = os.path.join(SCRIPT_DIR, "styles", "report_style.css")

# Configure Seaborn and Matplotlib for better visuals
sns.set_style("whitegrid")
plt.rcParams["font.family"] = "sans-serif"

# Custom color palette for consistent branding
COLORS = {
    'primary': '#3498db',    # Blue
    'secondary': '#2ecc71',  # Green
    'tertiary': '#e74c3c',   # Red
    'quaternary': '#f39c12', # Orange
    'text': '#2c3e50',       # Dark blue/gray
    'background': '#ecf0f1'  # Light gray
}

class ReportGenerationError(Exception):
    """Custom exception for report generation errors"""
    pass

class DataValidationError(Exception):
    """Custom exception for data validation errors"""
    pass

def ensure_directory_exists(directory):
    """Ensure the specified directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
            traceback.print_exc()

def fetch_user_profile_data(user_id):
    """Fetch user profile data from the database"""
    try:
        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()
        
        cursor.execute('''SELECT * FROM user_profiles WHERE id = ?''', (user_id,))
        
        columns = [desc[0] for desc in cursor.description]
        user_data = cursor.fetchone()
        
        if not user_data:
            print(f"Warning: No user profile found for user_id {user_id}")
            return {}
        
        # Convert to dictionary with column names as keys
        user_profile = dict(zip(columns, user_data))
        conn.close()
        return user_profile
        
    except Exception as e:
        print(f"Error fetching user profile data: {e}")
        traceback.print_exc()
        return {}

def fetch_initial_measurements(user_id):
    """Fetch initial measurements from the database"""
    try:
        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM initial_measurements 
            WHERE user_id = ? 
            ORDER BY date ASC LIMIT 1
        ''', (user_id,))
        
        columns = [desc[0] for desc in cursor.description]
        initial_data = cursor.fetchone()
        
        if not initial_data:
            print(f"Warning: No initial measurements found for user_id {user_id}")
            return {}
        
        # Convert to dictionary with column names as keys
        initial_measurements = dict(zip(columns, initial_data))
        conn.close()
        return initial_measurements
        
    except Exception as e:
        print(f"Error fetching initial measurements: {e}")
        traceback.print_exc()
        return {}

def fetch_weekly_updates(user_id):
    """Fetch weekly updates from the database"""
    try:
        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM weekly_updates 
            WHERE user_id = ? 
            ORDER BY date ASC
        ''', (user_id,))
        
        columns = [desc[0] for desc in cursor.description]
        weekly_data = cursor.fetchall()
        
        # Convert to list of dictionaries with column names as keys
        weekly_updates = [dict(zip(columns, row)) for row in weekly_data]
        conn.close()
        return weekly_updates
        
    except Exception as e:
        print(f"Error fetching weekly updates: {e}")
        traceback.print_exc()
        return []

def parse_date(date_str):
    """Parse a date string in various formats"""
    if not date_str:
        return None
        
    formats = ["%m%d%y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y"]
    
    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    print(f"Warning: Could not parse date '{date_str}'")
    return None

def format_date_for_display(date_obj_or_str):
    """Format a date for display in the report (MM/DD/YYYY)"""
    if isinstance(date_obj_or_str, datetime.datetime):
        return date_obj_or_str.strftime("%m/%d/%Y")
    elif isinstance(date_obj_or_str, str):
        date_obj = parse_date(date_obj_or_str)
        if date_obj:
            return date_obj.strftime("%m/%d/%Y")
    return date_obj_or_str

def generate_weight_progress_chart(weekly_data):
    """Generate a weight progress chart"""
    # Extract dates and weights, handling parsing errors
    dates = []
    weights = []
    for entry in weekly_data:
        date_str = entry.get('date')
        weight = entry.get('weight') or entry.get('body_weight')
        
        if not date_str or not weight:
            continue
            
        date_obj = parse_date(date_str)
        if date_obj and weight:
            dates.append(date_obj)
            weights.append(float(weight))
    
    if not dates or not weights:
        # Generate a placeholder chart if no valid data
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No weight data available", 
                ha='center', va='center', fontsize=14)
        ax.set_title("Weight Progress")
        ax.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100)
        plt.close(fig)
        img_buffer.seek(0)
        return base64.b64encode(img_buffer.getvalue()).decode()
    
    # Create figure with styling
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot data with styling
    ax.plot(dates, weights, marker='o', linestyle='-', color=COLORS['primary'])
    
    # Add trend line if we have enough data
    if len(dates) > 2:
        try:
            # Convert dates to ordinal for trend line calculation
            x = mdates.date2num(dates)
            z = np.polyfit(x, weights, 1)
            p = np.poly1d(z)
            ax.plot(dates, p(x), linestyle='--', color=COLORS['tertiary'], 
                    alpha=0.7, label=f'Trend: {z[0]:.2f} lbs/day')
            ax.legend(loc='upper right')
        except Exception as e:
            print(f"Error generating trend line: {e}")
    
    # Format the plot
    ax.set_title("Weight Progress Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Weight (lbs)")
    ax.grid(True, alpha=0.7)
    
    # Format date axis and adjust layout
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y'))
    fig.autofmt_xdate()
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100)
    plt.close(fig)
    img_buffer.seek(0)
    return base64.b64encode(img_buffer.getvalue()).decode()

def generate_body_composition_chart(weekly_data):
    """Generate a body composition chart"""
    # Extract dates and body fat percentages
    dates = []
    bf_percentages = []
    
    for entry in weekly_data:
        date_str = entry.get('date')
        bf = entry.get('body_fat') or entry.get('body_fat_percentage')
        
        if not date_str or not bf:
            continue
            
        date_obj = parse_date(date_str)
        if date_obj and bf:
            dates.append(date_obj)
            bf_percentages.append(float(bf))
    
    if not dates or not bf_percentages:
        # Generate a placeholder chart if no valid data
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No body composition data available", 
                ha='center', va='center', fontsize=14)
        ax.set_title("Body Composition")
        ax.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100)
        plt.close(fig)
        img_buffer.seek(0)
        return base64.b64encode(img_buffer.getvalue()).decode()
    
    # Create a simple BF% chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(dates, bf_percentages, marker='o', linestyle='-', color=COLORS['primary'])
    
    # Format the plot
    ax.set_title("Body Fat Percentage Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Body Fat %")
    ax.grid(True, alpha=0.7)
    
    # Format date axis and adjust layout
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%y'))
    fig.autofmt_xdate()
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100)
    plt.close(fig)
    img_buffer.seek(0)
    return base64.b64encode(img_buffer.getvalue()).decode()

def generate_ai_insights(report_data):
    """Generate AI-powered insights based on the report data"""
    insights = {
        'progress': [],
        'nutrition': [],
        'workout': [],
        'warnings': [],
        'recommendations': []
    }
    
    # Extract key metrics
    initial_weight = report_data.get('initial_weight')
    final_weight = report_data.get('final_weight') 
    
    # Basic validation
    if not all([initial_weight, final_weight]):
        insights['warnings'].append("Some key metrics are missing, which may affect analysis accuracy.")
    
    # Analyze overall progress
    if initial_weight and final_weight:
        weight_change = final_weight - initial_weight
        if weight_change < 0:
            insights['progress'].append(f"You've lost {abs(weight_change):.1f} lbs since starting your journey.")
        elif weight_change > 0:
            insights['progress'].append(f"You've gained {weight_change:.1f} lbs since starting your journey.")
        else:
            insights['progress'].append("Your weight has remained stable since starting.")
    
    # Simple recommendations
    insights['recommendations'].append("Focus on consistency with your nutrition and training for continued progress.")
    insights['recommendations'].append("Regular progress tracking helps identify effective strategies and areas for adjustment.")
    
    return insights

def prepare_report_data(user_profile, initial_measurements, weekly_updates):
    """Prepare report data from user profile and measurements"""
    # Basic validation
    if not user_profile:
        raise DataValidationError("No user profile data available")
    
    # Initialize report data
    report_data = {
        'name': user_profile.get('user_name', 'User'),
        'report_date': datetime.datetime.now().strftime("%m/%d/%Y"),
        'weekly_progress': []
    }
    
    # Extract and process profile data
    report_data['gender'] = 'Male' if user_profile.get('gender', 'm').lower() in ['m', 'male'] else 'Female'
    
    # Height formatting
    height_feet = user_profile.get('height_feet', 0)
    height_inches = user_profile.get('height_inches', 0)
    report_data['height'] = f"{height_feet}'{height_inches}\""
    
    # Initial measurements
    if initial_measurements:
        report_data['initial_weight'] = initial_measurements.get('weight', 0)
        report_data['initial_bf'] = initial_measurements.get('body_fat', 0)
    else:
        # Fallback to profile data if no initial measurements
        report_data['initial_weight'] = user_profile.get('initial_weight', 0)
        report_data['initial_bf'] = user_profile.get('initial_bf', 0)
    
    # Goal data
    report_data['goal_weight'] = user_profile.get('goal_weight', 0)
    report_data['goal_bf'] = user_profile.get('goal_bf', 0)
    
    # Current/final measurements (from weekly updates or profile)
    if weekly_updates:
        # Use the most recent weekly update
        latest_update = weekly_updates[-1]
        report_data['final_weight'] = latest_update.get('weight', report_data.get('initial_weight', 0))
        report_data['final_bf'] = latest_update.get('body_fat', report_data.get('initial_bf', 0))
        
        # Process all weekly updates for the progress table
        for update in weekly_updates:
            # Format date
            date = format_date_for_display(update.get('date', ''))
            
            # Extract measurements
            weight = update.get('weight', 0)
            body_fat = update.get('body_fat', 0)
            
            # Add to weekly progress list
            report_data['weekly_progress'].append({
                'date': date,
                'weight': weight,
                'body_fat': body_fat,
                'notes': update.get('notes', '')
            })
    else:
        # No weekly updates, use profile data as final values
        report_data['final_weight'] = user_profile.get('current_weight', report_data.get('initial_weight', 0))
        report_data['final_bf'] = user_profile.get('current_bf', report_data.get('initial_bf', 0))
    
    # Calculate summary metrics
    report_data['total_weeks'] = len(weekly_updates)
    report_data['total_weight_loss'] = report_data.get('initial_weight', 0) - report_data.get('final_weight', 0)
    report_data['total_bf_loss'] = report_data.get('initial_bf', 0) - report_data.get('final_bf', 0)
    
    # Current weight for display
    report_data['current_weight'] = report_data.get('final_weight', 0)
    
    return report_data

def generate_enhanced_report(user_id, options=None):
    """Generate an enhanced report for a user with charts and AI analysis"""
    try:
        # Set default options
        default_options = {
            'format': 'both',  # 'pdf', 'markdown', 'both', or 'all' (includes JSON)
            'include_ai_analysis': True,
            'include_charts': True,
        }
        
        # Use provided options or defaults
        if options is None:
            options = {}
        options = {**default_options, **options}
        
        # Fetch user data
        user_profile = fetch_user_profile_data(user_id)
        initial_measurements = fetch_initial_measurements(user_id)
        weekly_updates = fetch_weekly_updates(user_id)
        
        if not user_profile:
            raise DataValidationError(f"No user profile found for user ID {user_id}")
        
        # Extract user name for report
        user_name = user_profile.get('user_name', f"User_{user_id}")
        
        # Process data for the report
        report_data = prepare_report_data(user_profile, initial_measurements, weekly_updates)
        
        # Generate charts if enabled
        charts = {}
        if options['include_charts']:
            charts['weight_progress'] = generate_weight_progress_chart(weekly_updates)
            charts['body_composition'] = generate_body_composition_chart(weekly_updates)
        
        # Generate AI insights if enabled
        insights = {}
        if options['include_ai_analysis']:
            insights = generate_ai_insights(report_data)
        
        # Combine all data
        full_report_data = {
            **report_data,
            'charts': charts,
            'insights': insights
        }
        
        # Generate report content (placeholder for now)
        full_report_data['markdown_content'] = f"# Fitness Report for {report_data['name']}\n\nGenerated on {report_data['report_date']}"
        full_report_data['pdf_content'] = b'PDF content would be generated here'
        
        # Return the full report data
        return full_report_data
        
    except Exception as e:
        print(f"Error generating enhanced report: {e}")
        traceback.print_exc()
        return {'error': str(e)}

def save_report(report_data, username, save_format='both'):
    """Save the report in the specified format(s)"""
    saved_files = {}
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{username.replace(' ', '_')}_{timestamp}"
    
    # Ensure results folder exists
    ensure_directory_exists(RESULTS_FOLDER)
    
    if save_format in ['markdown', 'md', 'both']:
        markdown_filename = os.path.join(RESULTS_FOLDER, f"{base_filename}.md")
        markdown_content = report_data.get('markdown_content', '')
        with open(markdown_filename, 'w') as f:
            f.write(markdown_content)
        saved_files['markdown'] = os.path.abspath(markdown_filename)

    if save_format in ['pdf', 'both']:
        pdf_filename = os.path.join(RESULTS_FOLDER, f"{base_filename}.pdf")
        pdf_content = report_data.get('pdf_content', b'')
        with open(pdf_filename, 'wb') as f:
            f.write(pdf_content)
        saved_files['pdf'] = os.path.abspath(pdf_filename)

    if save_format in ['json', 'all']:
        json_filename = os.path.join(RESULTS_FOLDER, f"{base_filename}.json")
        # Encode 'pdf_content' using Base64 to make it JSON serializable
        json_data = report_data.copy()
        if 'pdf_content' in json_data:
            json_data['pdf_content'] = base64.b64encode(json_data['pdf_content']).decode('utf-8')
        with open(json_filename, 'w') as f:
            json.dump(json_data, f, default=str, indent=2)
        saved_files['json'] = os.path.abspath(json_filename)
    
    return saved_files

def generate_and_save_report(user_id, save_format='both'):
    """Generate and save a report for a user"""
    report_data = generate_enhanced_report(user_id)
    if 'error' in report_data:
        print(f"Error generating report: {report_data['error']}")
        return None
    
    username = report_data.get('name', f"User_{user_id}")
    saved_files = save_report(report_data, username, save_format)
    return saved_files

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        user_id = int(sys.argv[1])
        print(f"Generating report for user ID: {user_id}")
        saved_files = generate_and_save_report(user_id)
        if saved_files:
            print("Report saved to:")
            for format_type, filepath in saved_files.items():
                print(f"  {format_type}: {filepath}")
    else:
        print("Usage: python enhanced_report_generator.py <user_id>")

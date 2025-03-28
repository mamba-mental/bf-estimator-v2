#!/usr/bin/env python
# fixed_report_generation.py
# --- Beginning of File ---
# report_generation.py
# Author: Tiran Ronelle Winston
# Created: 09/09/24
# Last Modified: 03/27/25
# Description: A Python script to generate personalized weight loss journey reports in Markdown and PDF formats.
# Usage: The script can be used to generate reports from provided data and save them in the desired format.
# Dependencies: os, datetime, base64, io, matplotlib.pyplot, weasyprint.HTML, weasyprint.CSS, jinja2.Environment, jinja2.FileSystemLoader, json
# Version: 1.3.0 - FIXED
# License: Apache License 2.0
# --- End of Header ---

import os
import datetime
import json  # Ensure this is added
import base64  # Import base64 for encoding binary data
import io
import matplotlib.pyplot as plt
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FOLDER = os.path.join(SCRIPT_DIR, "results")
TEMPLATE_FOLDER = os.path.join(SCRIPT_DIR, "templates")
CSS_FILE = os.path.join(SCRIPT_DIR, "styles", "report_style.css")

def save_report(report_data, username, save_format):
    """
    Save the report in the specified format(s).

    Args:
        report_data (dict): The data to be included in the report.
        username (str): The name of the user for filename purposes.
        save_format (str): The format to save the report ('pdf', 'md', 'both', 'json').

    Returns:
        dict: A dictionary containing paths to the saved files.
    """
    saved_files = {}
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{username.replace(' ', '_')}_{timestamp}"
    results_folder = os.path.abspath('results')  # Absolute path for consistency

    # Ensure results folder exists
    os.makedirs(results_folder, exist_ok=True)

    if save_format in ['markdown', 'md', 'both']:
        markdown_filename = os.path.join(results_folder, f"{base_filename}.md")
        markdown_content = report_data.get('markdown_content', '')
        with open(markdown_filename, 'w') as f:
            f.write(markdown_content)
        saved_files['markdown'] = markdown_filename

    if save_format in ['pdf', 'both']:
        pdf_filename = os.path.join(results_folder, f"{base_filename}.pdf")
        pdf_content = report_data.get('pdf_content', b'')
        with open(pdf_filename, 'wb') as f:
            f.write(pdf_content)
        saved_files['pdf'] = pdf_filename

    if save_format in ['json', 'both']:
        json_filename = os.path.join(results_folder, f"{base_filename}.json")
        # Encode 'pdf_content' using Base64 to make it JSON serializable
        json_data = report_data.copy()
        if 'pdf_content' in json_data:
            json_data['pdf_content'] = base64.b64encode(json_data['pdf_content']).decode('utf-8')
        with open(json_filename, 'w') as f:
            json.dump(json_data, f, default=str)
        saved_files['json'] = json_filename

    return saved_files

def generate_markdown(report_data):
    # Generate a Markdown formatted report.
    # Parameters:
    # report_data (dict): The data to be included in the report.
    # Returns:
    # str: A string containing the Markdown formatted report.
    markdown = f"""# Your Personalized Weight Loss Journey Report

Generated on: {report_data['report_date']}

## 1. Personal Profile

- Start Date: {report_data['start_date']}
- End Date: {report_data['end_date']}
- Age: {report_data['age']} years
- Gender: {report_data['gender']}
- Height: {report_data['height']}
- Initial Weight: {report_data['initial_weight']} lbs
- Goal Weight: {report_data['goal_weight']} lbs
- Initial Body Fat: {report_data['initial_body_fat']}%
- Goal Body Fat: {report_data['goal_body_fat']}%
- Activity Level: {report_data['activity_level']}
- Experience Level: {report_data['experience_level']}

## 2. Metabolic Calculations

- Initial RMR: {report_data['initial_rmr']} cal/day
- Initial TDEE: {report_data['initial_tdee']} cal/day
- TEF: {report_data['tef']} cal/day
- NEAT: {report_data['neat']} cal/day
- Initial Daily Calorie Intake: {report_data['initial_daily_calorie_intake']} cal/day

## 3. Workout Analysis

- Type: {report_data['workout_type']}
- Frequency: {report_data['workout_frequency']}
- Volume Score: {report_data['volume_score']}
- Intensity Score: {report_data['intensity_score']}
- Frequency Score: {report_data['frequency_score']}
- Resistance Training: {report_data['resistance_training']}
- Athlete Status: {report_data['athlete_status']}

## 4. Body Composition Adjustments

- Initial Lean Mass: {report_data['initial_lean_mass']} lbs
- Initial Fat Mass: {report_data['initial_fat_mass']} lbs
- Est. Weekly Muscle Gain: {report_data['weekly_muscle_gain']} lbs

## 5. Weekly Progress Forecast

(Chart not available in Markdown format)

## 6. Body Composition Changes Over Time

(Chart not available in Markdown format)

## 7. Metabolic Adaptation

- Week 1 Metabolic Adaptation: {report_data['week_1_adaptation']}
- Final Week Metabolic Adaptation: {report_data['final_week_adaptation']}

## 8. Final Results

- Duration: {report_data['total_weeks']} weeks
- Total Weight Loss: {report_data['total_weight_loss']} lbs
- Total Body Fat Reduction: {report_data['total_bf_loss']}%
- Final Weight: {report_data['final_weight']} lbs
- Final Body Fat: {report_data['final_body_fat']}%
- Average Weekly Weight Loss: {report_data['avg_weekly_loss']} lbs
- Total Muscle Gain: {report_data['total_muscle_gain']} lbs
- Final Daily Calorie Intake: {report_data['final_daily_calorie_intake']} calories
- Final TDEE: {report_data['final_tdee']} calories
- Final Weekly Caloric Output: {report_data['final_weekly_caloric_output']} calories

## 9. Body Fat Category Progression

- Initial: {report_data['initial_body_fat_category']}
  - Description: {report_data['initial_body_fat_description']}
  - Est. Time to Six-Pack: {report_data['initial_time_to_six_pack']}
- Final: {report_data['final_body_fat_category']}
  - Description: {report_data['final_body_fat_description']}
  - Est. Time to Six-Pack: {report_data['final_time_to_six_pack']}

## 10. Insights and Recommendations

- Your metabolic rate adapted by {report_data['adaptation_percentage']}% over the course of your journey.
- You maintained {report_data['lean_mass_preserved']}% of your initial lean mass.
- Your muscle gain rate averaged {report_data['avg_muscle_gain']} lbs per week.
- Based on your final body fat percentage, you're now in the {report_data['final_body_fat_category']} category.
- To maintain your results, consider a daily calorie intake of {report_data['final_tdee']} calories.

## 11. Next Steps

- Continue with your current plan.
- Consider adjusting your protein intake to support lean mass.
- Your next ideal body composition goal could be a lower body fat percentage.
"""
    return markdown

def generate_html(report_data):
    # Generate an HTML formatted report for PDF conversion.
    # Parameters:
    # report_data (dict): The data to be included in the report.
    # Returns:
    # str: A string containing the HTML formatted report.
    env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))

    # Add the get_score_description function to the template environment
    env.globals['get_score_description'] = get_score_description

    template = env.get_template('report_template.html')

    # Generate charts
    report_data['weight_progress_chart'] = generate_weight_progress_chart(report_data['weekly_progress'])
    report_data['body_composition_chart'] = generate_body_composition_chart(report_data['body_composition_changes'])

    return template.render(report_data)

def get_score_description(score, score_type):
    """
    Get a description for a score (volume, intensity, frequency).

    Args:
        score (int): The numerical score value.
        score_type (str): The type of score ('volume', 'intensity', 'frequency').

    Returns:
        str: A descriptive text for the score.
    """
    descriptions = {
        'volume': {
            0: "No training",
            1: "Very low volume (1-3 sets per muscle group per week)",
            2: "Low volume (4-6 sets per muscle group per week)",
            3: "Moderate volume (7-10 sets per muscle group per week)",
            4: "High volume (11-15 sets per muscle group per week)",
            5: "Very high volume (16+ sets per muscle group per week)"
        },
        'intensity': {
            0: "No training",
            1: "Very light intensity (RPE 4-5 / 60% 1RM or less)",
            2: "Light intensity (RPE 6 / 60-70% 1RM)",
            3: "Moderate intensity (RPE 7-8 / 70-80% 1RM)",
            4: "High intensity (RPE 9 / 80-90% 1RM)",
            5: "Very high intensity (RPE 10 / 90%+ 1RM)"
        },
        'frequency': {
            0: "No training",
            1: "Very low frequency (training 1 day per week)",
            2: "Low frequency (training 2 days per week)",
            3: "Moderate frequency (training 3-4 days per week)",
            4: "High frequency (training 5-6 days per week)",
            5: "Very high frequency (training 7+ days per week)"
        }
    }

    if score_type in descriptions:
        # Try to find exact score match
        if score in descriptions[score_type]:
            return descriptions[score_type][score]

        # If exact score not found, find closest lower bound
        available_scores = sorted(descriptions[score_type].keys())
        for i in range(len(available_scores) - 1, -1, -1):
            if available_scores[i] <= score:
                return descriptions[score_type][available_scores[i]]

        # If all else fails, return lowest description
        if available_scores:
            return descriptions[score_type][available_scores[0]]

    return "No description available"

def generate_weight_progress_chart(weekly_progress):
    # Generate a chart showing the user's weight progress over time.
    # Parameters:
    # weekly_progress (list): A list of dictionaries containing weekly progress data.
    # Returns:
    # str: A base64 encoded string of the generated chart image.
    dates = []
    weights = []
    for week in weekly_progress:
        try:
            # Try parsing with '%m/%d/%Y' format first (most common)
            date = datetime.datetime.strptime(week['date'], '%m/%d/%Y')
        except ValueError:
            try:
                # If that fails, try '%m%d%y' format
                date = datetime.datetime.strptime(week['date'], '%m%d%y')
            except ValueError:
                # If both fail, log an error and skip this data point
                print(f"Error parsing date: {week['date']}. Skipping this data point.")
                continue
        dates.append(date)
        weights.append(week['weight'])

    plt.figure(figsize=(10, 6))
    plt.plot(dates, weights, marker='o')
    plt.title('Weight Progress')
    plt.xlabel('Date')
    plt.ylabel('Weight (lbs)')
    plt.grid(True)

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    return base64.b64encode(img_buffer.getvalue()).decode()

def generate_body_composition_chart(body_composition_changes):
    # Generate a chart showing changes in body composition over time.
    # Parameters:
    # body_composition_changes (list): A list of dictionaries containing body composition data.
    # Returns:
    # str: A base64 encoded string of the generated chart image.
    dates = []
    body_fat_percentages = []
    for change in body_composition_changes:
        try:
            # Try parsing with '%m/%d/%Y' format first
            date = datetime.datetime.strptime(change['date_reached'], '%m/%d/%Y')
        except ValueError:
            try:
                # If that fails, try '%m%d%y' format
                date = datetime.datetime.strptime(change['date_reached'], '%m%d%y')
            except ValueError:
                # If both fail, log an error and skip this data point
                print(f"Error parsing date: {change['date_reached']}. Skipping this data point.")
                continue
        dates.append(date)
        body_fat_percentages.append(change['body_fat_percentage'])

    plt.figure(figsize=(10, 6))
    plt.plot(dates, body_fat_percentages, marker='o')
    plt.title('Body Composition Changes')
    plt.xlabel('Date')
    plt.ylabel('Body Fat Percentage')
    plt.grid(True)

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    return base64.b64encode(img_buffer.getvalue()).decode()

def print_summary(progression, initial_data):
    # Print a summary of the weight loss journey and optionally save the detailed report.
    # Parameters:
    # progression (list): A list of dictionaries containing weekly progress data.
    # initial_data (dict): A dictionary containing the user's initial data and settings.
    report_data = generate_comprehensive_report(progression, initial_data)

    print("\nWeight Loss Journey Summary:")
    print(f"Initial Weight: {report_data['initial_weight']:.1f} lbs")
    print(f"Final Weight: {report_data['final_weight']:.1f} lbs")
    print(f"Total Weight Loss: {report_data['total_weight_loss']:.1f} lbs")
    print(f"Initial Body Fat: {report_data['initial_body_fat']:.1f}%")
    print(f"Final Body Fat: {report_data['final_body_fat']:.1f}%")
    print(f"Total Body Fat Reduction: {report_data['total_bf_loss']:.1f}%")
    print(f"Total Muscle Gain: {report_data['total_muscle_gain']:.1f} lbs")

    save_option = input("\nDo you want to save the detailed report? (y/n): ").lower()
    saved_files = {}
    if save_option == 'y':
        save_format = input("Choose the format to save (markdown/pdf/both): ").lower()
        if save_format in ['markdown', 'pdf', 'both']:
            saved_files = save_report(report_data, initial_data.get('name', 'User'), save_format)
        else:
            print("Invalid format choice. Report will not be saved.")
    else:
        print("Report will not be saved.")

    return saved_files

def generate_comprehensive_report(progression, initial_data):
    # Generate a comprehensive report with all relevant data.
    # Parameters:
    # progression (list): A list of dictionaries containing weekly progress data.
    # initial_data (dict): A dictionary containing the user's initial data and settings.
    # Returns:
    # dict: A dictionary containing the full report data.

    # --- Calculate Age Safely ---
    calculated_age = "N/A" # Default value
    start_date_str_converted = convert_date_string(progression[0]['date'])
    start_date_dt = None
    birth_date_dt = None

    # Try parsing start date
    try:
        start_date_dt = datetime.datetime.strptime(start_date_str_converted, "%m/%d/%Y")
    except (ValueError, TypeError) as e:
        print(f"Error: Could not parse start date '{start_date_str_converted}' for age calculation: {e}")

    # Try parsing birth date (dob)
    if 'dob' in initial_data and initial_data['dob']:
        dob_str = initial_data['dob']

        # Check if dob_str is already a datetime object
        if isinstance(dob_str, datetime.datetime):
            birth_date_dt = dob_str
        elif isinstance(dob_str, str): # Only parse if it's a string
            try:
                # Try parsing MMDDYY first
                birth_date_dt = datetime.datetime.strptime(dob_str, "%m%d%y")
            except ValueError:
                try:
                    # Try parsing MM/DD/YYYY
                    birth_date_dt = datetime.datetime.strptime(dob_str, "%m/%d/%Y")
                except ValueError:
                    try:
                        # Try parsing YYYY-MM-DD
                        birth_date_dt = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
                    except ValueError:
                        print(f"Warning: Could not parse birth date format for '{dob_str}'")
        else:
             print(f"Warning: Unexpected type for birth date: {type(dob_str)}")

    # Calculate age only if both dates are valid datetime objects
    if start_date_dt and birth_date_dt:
        # Ensure birth_date_dt is actually a datetime object before calculating
        if isinstance(birth_date_dt, datetime.datetime):
            age_result = calculate_age(birth_date_dt, start_date_dt) # Pass datetime objects
            if age_result is not None:
                calculated_age = age_result
        else:
            print(f"Warning: Could not calculate age because birth_date_dt is not a valid datetime object.")
    # --- End Age Calculation ---

    # Get height values with safe defaults
    height_feet = initial_data.get('height_feet', 5)
    height_inches = initial_data.get('height_inches', 0)

    # Format height string
    if initial_data.get('height_cm'):
        height_str = f"{height_feet}'{'0' if height_inches == 0 else height_inches}\" ({initial_data.get('height_cm', 0):.1f} cm)"
    else:
        height_str = f"{height_feet}'{'0' if height_inches == 0 else height_inches}\""

    report_data = {
        'name': initial_data.get('name', 'User'),
        'report_date': datetime.datetime.now().strftime("%m/%d/%Y"),
        'start_date': start_date_str_converted, # Use the converted string
        'end_date': convert_date_string(progression[-1]['date']),
        'age': calculated_age, # Use the safely calculated age
        'gender': 'Male' if initial_data.get('gender', 'm').lower() == 'm' else 'Female',
        'height': height_str,
        'initial_weight': progression[0]['weight'],
        'final_weight': progression[-1]['weight'],
        'goal_weight': initial_data.get('goal_weight', 0),
        'initial_body_fat': progression[0]['body_fat_percentage'],
        'final_body_fat': progression[-1]['body_fat_percentage'],
        'goal_body_fat': initial_data.get('goal_bf', 0),
        'activity_level': initial_data.get('activity_level_description', 'Unknown'),
        'experience_level': initial_data.get('experience_level', 'Beginner'),
        'initial_rmr': progression[0].get('rmr', 0),
        'initial_tdee': progression[0].get('tdee', 0),
        'tef': initial_data.get('tef', calculate_tef(initial_data.get('protein_intake', 0))),
        'neat': initial_data.get('neat', calculate_neat(initial_data.get('job_activity', 'sedentary'), initial_data.get('leisure_activity', 'sedentary'))),
        'initial_daily_calorie_intake': progression[0].get('daily_calorie_intake', 0),
        'workout_type': get_workout_type_description(initial_data.get('workout_type', 7)),
        'workout_frequency': initial_data.get('workout_days', 0),
        'volume_score': initial_data.get('volume_score', 0),
        'intensity_score': initial_data.get('intensity_score', 0),
        'frequency_score': initial_data.get('frequency_score', 0),
        'resistance_training': 'Yes' if initial_data.get('resistance_training', False) else 'No',
        'athlete_status': 'Yes' if initial_data.get('is_athlete', False) else 'No',
        'initial_lean_mass': progression[0].get('lean_mass', 0),
        'initial_fat_mass': progression[0].get('fat_mass', 0),
        'weekly_muscle_gain': sum(week.get('muscle_gain', 0) for week in progression) / len(progression),
    }

    # Weekly progress (with safe date conversion)
    weekly_progress = []
    for week in progression:
        try:
            date_converted = datetime.datetime.strptime(week['date'], "%m%d%y").strftime("%m/%d/%Y")
        except ValueError:
            try:
                date_converted = datetime.datetime.strptime(week['date'], "%m/%d/%Y").strftime("%m/%d/%Y")
            except ValueError:
                date_converted = week['date']  # Keep original if parsing fails

        weekly_progress.append({**week, 'date': date_converted})

    report_data['weekly_progress'] = weekly_progress

    # Add additional metrics with safe defaults
    report_data.update({
        'week_1_adaptation': 1.0,
        'final_week_adaptation': progression[-1].get('tdee', 0) / max(progression[0].get('tdee', 1), 1),  # Avoid division by zero
        'total_weeks': len(progression) - 1 if len(progression) > 1 else 0,
        'total_weight_loss': progression[0]['weight'] - progression[-1]['weight'],
        'total_bf_loss': progression[0]['body_fat_percentage'] - progression[-1]['body_fat_percentage'],
        'avg_weekly_loss': (progression[0]['weight'] - progression[-1]['weight']) / max(len(progression) - 1, 1),  # Avoid division by zero
        'total_muscle_gain': sum(week.get('muscle_gain', 0) for week in progression),
        'final_daily_calorie_intake': progression[-1].get('daily_calorie_intake', 0),
        'final_tdee': progression[-1].get('tdee', 0),
        'final_weekly_caloric_output': progression[-1].get('weekly_caloric_output', 0),
    })

    # Add body fat category information
    from complete_report_functions import get_body_fat_info
    initial_bf_info = get_body_fat_info(initial_data.get('gender', 'm'), progression[0]['body_fat_percentage'])
    final_bf_info = get_body_fat_info(initial_data.get('gender', 'm'), progression[-1]['body_fat_percentage'])

    report_data.update({
        'initial_body_fat_category': initial_bf_info[0],
        'initial_body_fat_description': initial_bf_info[2],
        'initial_time_to_six_pack': initial_bf_info[1],
        'final_body_fat_category': final_bf_info[0],
        'final_body_fat_description': final_bf_info[2],
        'final_time_to_six_pack': final_bf_info[1],
        'adaptation_percentage': (1 - (progression[-1].get('tdee', 0) / max(progression[0].get('tdee', 1), 1))) * 100,
        'lean_mass_preserved': (progression[-1].get('lean_mass', 0) / max(progression[0].get('lean_mass', 1), 1)) * 100,
        'avg_muscle_gain': sum(week.get('muscle_gain', 0) for week in progression) / max(len(progression) - 1, 1),
    })

    # Ensure body_composition_changes is populated
    report_data['body_composition_changes'] = []
    for week in progression:
        bf_info = get_body_fat_info(initial_data.get('gender', 'm'), week['body_fat_percentage'])

        try:
            date_converted = datetime.datetime.strptime(week['date'], "%m%d%y").strftime("%m/%d/%Y")
        except ValueError:
            try:
                date_converted = datetime.datetime.strptime(week['date'], "%m/%d/%Y").strftime("%m/%d/%Y")
            except ValueError:
                date_converted = week['date']  # Keep original if parsing fails

        report_data['body_composition_changes'].append({
            'category': bf_info[0],
            'body_fat_percentage': week['body_fat_percentage'],
            'date_reached': date_converted,
            'description': bf_info[2],
            'time_to_six_pack': bf_info[1]
        })

    # Generate charts
    report_data['weight_progress_chart'] = generate_weight_progress_chart(report_data['weekly_progress'])
    report_data['body_composition_chart'] = generate_body_composition_chart(report_data['body_composition_changes'])

    # Generate the markdown content
    report_data['markdown_content'] = generate_markdown(report_data)

    # Generate the HTML content
    html_content = generate_html(report_data)

    # Generate the PDF content using WeasyPrint
    pdf_content = HTML(string=html_content).write_pdf(stylesheets=[CSS(CSS_FILE)])

    # Store the pdf_content in report_data
    report_data['pdf_content'] = pdf_content

    # Round all float values to one decimal place
    for key, value in report_data.items():
        if isinstance(value, float):
            report_data[key] = round(value, 1)

    return report_data

def calculate_age(birth_date, start_date):
    """
    Calculate the age of the user based on birth date and start date.

    Args:
        birth_date (datetime): The user's birth date as a datetime object.
        start_date (datetime): The start date of the weight loss journey as a datetime object.

    Returns:
        int: The calculated age in years.
    """
    # Ensure both inputs are datetime objects before proceeding
    if not isinstance(birth_date, datetime.datetime) or not isinstance(start_date, datetime.datetime):
        print("Error: calculate_age received invalid date types.")
        return None

    try:
        age = start_date.year - birth_date.year - ((start_date.month, start_date.day) < (birth_date.month, birth_date.day))
        return age
    except AttributeError as e:
        # This catch is a safeguard, but the type check above should prevent it.
        print(f"Error calculating age (AttributeError): {e}. Check date objects.")
        return None

def calculate_tef(protein_intake):
    # Calculate the Thermic Effect of Food (TEF) based on protein intake.
    # This function assumes that 10% of the protein intake contributes to TEF.
    # Parameters:
    # protein_intake (int): The amount of protein intake in grams.
    # Returns:
    # int: The calculated TEF value.
    return protein_intake * 0.1

def calculate_neat(job_activity, leisure_activity):
    # Calculate Non-Exercise Activity Thermogenesis (NEAT) based on activity levels.
    # The function assigns a numerical value to activity levels and combines job and leisure activities to estimate NEAT.
    # Parameters:
    # job_activity (str): The user's job activity level.
    # leisure_activity (str): The user's leisure activity level.
    # Returns:
    # int: The calculated NEAT value.
    activity_levels = {'sedentary': 1, 'light': 2, 'moderate': 3, 'active': 4}
    # Use get with default 1 (sedentary) to handle missing or invalid activity levels
    job_level = activity_levels.get(job_activity.lower(), 1) if isinstance(job_activity, str) else 1
    leisure_level = activity_levels.get(leisure_activity.lower(), 1) if isinstance(leisure_activity, str) else 1
    return (job_level + leisure_level) * 50

def convert_date_string(date_str):
    """
    Convert a date string to a consistent format (MM/DD/YYYY).

    Args:
        date_str (str): The date string to convert.

    Returns:
        str: The converted date string in MM/DD/YYYY format.
    """
    if not date_str:
        return datetime.datetime.now().strftime("%m/%d/%Y")

    try:
        # Try parsing with MMDDYY format
        date_obj = datetime.datetime.strptime(date_str, "%m%d%y")
        return date_obj.strftime("%m/%d/%Y")
    except ValueError:
        try:
            # Try parsing with MM/DD/YYYY format
            date_obj = datetime.datetime.strptime(date_str, "%m/%d/%Y")
            return date_obj.strftime("%m/%d/%Y")
        except ValueError:
            # Return the original string if parsing fails
            return date_str

def get_workout_type_description(workout_type):
    """
    Get a description of the workout type based on its code.

    Args:
        workout_type (int): The code representing the workout type.

    Returns:
        str: The description of the workout type.
    """
    descriptions = {
        1: "Bodybuilding (focus on muscle hypertrophy)",
        2: "Strength Training (focus on increasing maximal strength)",
        3: "Powerlifting (focus on squat, bench press, and deadlift)",
        4: "Olympic Weightlifting (focus on snatch and clean & jerk)",
        5: "Crossfit (high-intensity functional training)",
        6: "Calisthenics (bodyweight exercises)",
        7: "General Fitness (balanced approach to overall health and fitness)"
    }

    # If workout_type is a string (like "3"), convert to int
    if isinstance(workout_type, str) and workout_type.isdigit():
        workout_type = int(workout_type)

    # If workout_type is an int and in the descriptions dictionary, return the description
    if isinstance(workout_type, int) and workout_type in descriptions:
        return descriptions[workout_type]

    # Default to General Fitness if not found
    return descriptions[7]

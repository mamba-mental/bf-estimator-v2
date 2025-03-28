# fixed_report_generation_enhanced.py
# Author: Tiran Ronelle Winston
# Created: 03/27/25
# Last Modified: 03/27/25
# Description: Enhanced report generation with support for the updated user profile fields
# Dependencies: os, datetime, base64, io, matplotlib.pyplot, weasyprint.HTML, weasyprint.CSS, jinja2.Environment, jinja2.FileSystemLoader, json
# Version: 1.3.0

import os
import datetime
import json
import base64
import io
import matplotlib.pyplot as plt
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
import sqlite3
import diet_calculations

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FOLDER = os.path.join(SCRIPT_DIR, "results")
TEMPLATE_FOLDER = os.path.join(SCRIPT_DIR, "templates")
CSS_FILE = os.path.join(SCRIPT_DIR, "styles", "report_style.css")
DB_FILE = 'history.db'

def save_report(report_data, username, save_format):
    """Save the report in the specified format(s)."""
    saved_files = {}
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{username.replace(' ', '_')}_{timestamp}"
    results_folder = os.path.abspath('results')  # Absolute path for consistency

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

    # Save a copy of the report data (without PDF) for reference
    with open("last_report_data.json", 'w') as f:
        json_data = report_data.copy()
        if 'pdf_content' in json_data:
            del json_data['pdf_content']
        json.dump(json_data, f, indent=4, default=str)

    return saved_files

def generate_markdown(report_data):
    """Generate a Markdown formatted report."""
    markdown = f"""# Your Personalized Fitness Journey Report

Generated on: {report_data['report_date']}

## 1. Personal Profile

- Start Date: {report_data['start_date']}
- End Date: {report_data['end_date']}
- Age: {report_data['age']} years
- Gender: {report_data['gender']}
- Height: {report_data['height']}
- Email: {report_data.get('email', 'Not provided')}
- Phone: {report_data.get('phone', 'Not provided')}

## 2. Initial Measurements (Baseline)

- Initial Weight: {report_data['initial_weight']} lbs
- Initial Body Fat: {report_data['initial_body_fat']}%
- Goal Weight: {report_data['goal_weight']} lbs
- Goal Body Fat: {report_data['goal_body_fat']}%

## 3. Current Measurements

- Current Weight: {report_data.get('current_weight', 'Not available')} lbs
- Current Body Fat: {report_data.get('current_bf', 'Not available')}%

## 4. Metabolic Calculations

- RMR (Resting Metabolic Rate): {report_data['initial_rmr']} cal/day
- TDEE (Total Daily Energy Expenditure): {report_data['initial_tdee']} cal/day
- TEF (Thermic Effect of Food): {report_data['tef']} cal/day
- NEAT (Non-Exercise Activity Thermogenesis): {report_data['neat']} cal/day
- Daily Calorie Intake: {report_data['initial_daily_calorie_intake']} cal/day

## 5. Workout Information

- Type: {report_data['workout_type']}
- Frequency: {report_data['workout_frequency']} days/week
- Resistance Training: {report_data['resistance_training']}
- Experience Level: {report_data['experience_level']}
- Athlete Status: {report_data['athlete_status']}

## 6. Nutrition Profile

- Protein Intake: {report_data.get('protein_intake', 'Not available')} g/day ({report_data.get('protein_ratio', 0):.1f}% of calories)
- Carbohydrate Intake: {report_data.get('carb_intake', 'Not available')} g/day ({report_data.get('carbs_ratio', 0):.1f}% of calories)
- Fat Intake: {report_data.get('fat_intake', 'Not available')} g/day ({report_data.get('fat_ratio', 0):.1f}% of calories)
- Diet Type: {report_data.get('diet_type', 'Not available')}
- Total Daily Calories: {report_data.get('total_daily_calories', 'Not available')} calories
- Diet Quality Assessment: {report_data.get('diet_quality', 'Not available')}

## 7. Diet-Based Projections

- Expected Weekly Fat Loss: {report_data.get('weekly_fat_loss', 'Not available')} lbs/week
- Expected Weekly Muscle Gain: {report_data.get('weekly_muscle_gain', 'Not available')} lbs/week
- Estimated Weeks to Goal: {report_data.get('weeks_to_goal', 'Not available')}
- Diet Effect on Fat Loss: {report_data.get('diet_fat_loss_effect', 'Not available')}
- Diet Effect on Muscle Gain: {report_data.get('diet_muscle_gain_effect', 'Not available')}

## 8. Body Composition Analysis

- Initial Lean Mass: {report_data['initial_lean_mass']} lbs
- Initial Fat Mass: {report_data['initial_fat_mass']} lbs
- Est. Weekly Muscle Gain: {report_data['weekly_muscle_gain']} lbs

## 9. Weekly Progress Forecast

(Chart not available in Markdown format)

## 10. Body Composition Changes Over Time

(Chart not available in Markdown format)

## 11. Metabolic Adaptation

- Week 1 Metabolic Adaptation: {report_data['week_1_adaptation']}
- Final Week Metabolic Adaptation: {report_data['final_week_adaptation']}

## 12. Final Results

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

## 13. Body Fat Category Progression

- Initial: {report_data['initial_body_fat_category']}
  - Description: {report_data['initial_body_fat_description']}
  - Est. Time to Six-Pack: {report_data['initial_time_to_six_pack']}
- Final: {report_data['final_body_fat_category']}
  - Description: {report_data['final_body_fat_description']}
  - Est. Time to Six-Pack: {report_data['final_time_to_six_pack']}

## 14. Nutrition Recommendations
"""
    
    # Add any diet warnings to the report
    if 'diet_warnings' in report_data and report_data['diet_warnings']:
        markdown += "\n### Diet Adjustments Recommended:\n\n"
        for warning in report_data['diet_warnings']:
            markdown += f"- {warning}\n"
    
    markdown += f"""
## 15. Insights and Recommendations

- Your metabolic rate adapted by {report_data['adaptation_percentage']}% over the course of your journey.
- You maintained {report_data['lean_mass_preserved']}% of your initial lean mass.
- Your muscle gain rate averaged {report_data['avg_muscle_gain']} lbs per week.
- Based on your final body fat percentage, you're now in the {report_data['final_body_fat_category']} category.
- To maintain your results, consider a daily calorie intake of {report_data['final_tdee']} calories.

## 16. Next Steps

- Continue with your current plan.
- Consider adjusting your protein intake to support lean mass.
- Your next ideal body composition goal could be a lower body fat percentage.
"""
    return markdown

def generate_html(report_data):
    """Generate an HTML formatted report for PDF conversion."""
    env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))
    
    # Add the get_score_description function to the template environment
    env.globals['get_score_description'] = get_score_description
    
    template = env.get_template('report_template.html')
    
    # Generate charts
    report_data['weight_progress_chart'] = generate_weight_progress_chart(report_data['weekly_progress'])
    report_data['body_composition_chart'] = generate_body_composition_chart(report_data['body_composition_changes'])
    
    return template.render(report_data)

def generate_weight_progress_chart(weekly_progress):
    """Generate a chart showing the user's weight progress over time."""
    dates = []
    weights = []
    for week in weekly_progress:
        try:
            # Try parsing with '%m%d%y' format first
            date = datetime.datetime.strptime(week['date'], '%m%d%y')
        except ValueError:
            try:
                # If that fails, try '%m/%d/%Y' format
                date = datetime.datetime.strptime(week['date'], '%m/%d/%Y')
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
    """Generate a chart showing changes in body composition over time."""
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
    """Print a summary of the fitness journey and optionally save the detailed report."""
    report_data = generate_comprehensive_report(progression, initial_data)
    
    print("\nFitness Journey Summary:")
    print(f"Initial Weight: {report_data['initial_weight']:.1f} lbs")
    print(f"Current Weight: {report_data['final_weight']:.1f} lbs")
    print(f"Total Weight Loss: {report_data['total_weight_loss']:.1f} lbs")
    print(f"Initial Body Fat: {report_data['initial_body_fat']:.1f}%")
    print(f"Current Body Fat: {report_data['final_body_fat']:.1f}%")
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

def calculate_rmr(gender, weight_kg, height_cm, age):
    """
    Calculate RMR using the Mifflin-St Jeor equation.
    
    Parameters:
    gender (str): 'male' or 'female'
    weight_kg (float): Weight in kilograms
    height_cm (float): Height in centimeters
    age (int): Age in years
    
    Returns:
    float: Calculated RMR in calories per day
    """
    try:
        # Validate inputs
        if not all([gender, weight_kg, height_cm, age]):
            print("Warning: Missing required fields for RMR calculation")
            return None
            
        if gender.lower() == 'male':
            return 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
        else:  # female
            return 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
    except Exception as e:
        print(f"Error calculating RMR: {str(e)}")
        return None
        
def get_initial_measurements(user_id):
    """Get initial measurements from the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT weight, body_fat_percentage, waist, hips, chest, 
                   left_arm, right_arm, left_thigh, right_thigh, neck
            FROM initial_measurements
            WHERE user_id = ?
            ORDER BY date ASC
            LIMIT 1
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'weight': result[0],
                'body_fat_percentage': result[1],
                'waist': result[2],
                'hips': result[3],
                'chest': result[4],
                'left_arm': result[5],
                'right_arm': result[6],
                'left_thigh': result[7],
                'right_thigh': result[8],
                'neck': result[9]
            }
        return None
    except Exception as e:
        print(f"Error getting initial measurements: {str(e)}")
        return None

def generate_comprehensive_report(progression, initial_data):
    """Generate a comprehensive report with all relevant data."""
    # --- Calculate Age Safely ---
    calculated_age = 30  # Default value if calculation fails
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

    # Calculate age only if both dates are valid datetime objects
    if start_date_dt and birth_date_dt:
        age_result = calculate_age(birth_date_dt, start_date_dt) # Pass datetime objects
        if age_result is not None:
            calculated_age = age_result
    # --- End Age Calculation ---
    
    # Get initial measurements if available
    initial_measurements = get_initial_measurements(initial_data.get('user_id', 1))
    
    # Get gender from initial_data, ensuring it's properly formatted
    gender = initial_data.get('gender', 'male')
    if isinstance(gender, str) and gender.lower() in ['m', 'male']:
        gender_display = 'Male'
        gender_code = 'male'
    else:
        gender_display = 'Female'
        gender_code = 'female'
    
    # Calculate height in cm for RMR formula
    height_feet = float(initial_data.get('height_feet', 0))
    height_inches = float(initial_data.get('height_inches', 0))
    height_cm = (height_feet * 30.48) + (height_inches * 2.54)
    
    # Calculate RMR using proper formula
    weight_kg = progression[0]['weight'] * 0.453592  # Convert lbs to kg
    rmr = calculate_rmr(gender_code, weight_kg, height_cm, calculated_age)
    
    # Use the calculated RMR or fallback to existing value
    if rmr is None:
        rmr = progression[0].get('rmr', 1800)  # Fallback value
        print("Warning: Using fallback RMR value.")
    
    # Calculate TDEE based on activity level
    activity_multipliers = {
        '1': 1.2,  # Sedentary
        '2': 1.375,  # Lightly Active
        '3': 1.55,  # Moderately Active
        '4': 1.725,  # Very Active
        '5': 1.9  # Extra Active
    }
    activity_level = initial_data.get('activity_level', '3')
    tdee = rmr * activity_multipliers.get(activity_level, 1.55)
    
    # Use calculated TDEE or fallback
    if 'tdee' not in progression[0]:
        progression[0]['tdee'] = tdee
    
    # Set initial body composition values from initial measurements if available
    initial_weight = initial_measurements['weight'] if initial_measurements else progression[0]['weight']
    initial_body_fat = initial_measurements['body_fat_percentage'] if initial_measurements else progression[0]['body_fat_percentage']
    
    # Calculate lean mass and fat mass
    lean_mass = initial_weight * (1 - initial_body_fat / 100)
    fat_mass = initial_weight * (initial_body_fat / 100)
    
    # Update progression[0] with the derived values if not present
    if 'lean_mass' not in progression[0]:
        progression[0]['lean_mass'] = lean_mass
    if 'fat_mass' not in progression[0]:
        progression[0]['fat_mass'] = fat_mass
    if 'rmr' not in progression[0]:
        progression[0]['rmr'] = rmr
    if 'daily_calorie_intake' not in progression[0]:
        progression[0]['daily_calorie_intake'] = tdee - 500  # Default 500 calorie deficit
    
    # Calculate nutrition information
    protein_g = float(initial_data.get('protein_intake', 150))
    carbs_g = float(initial_data.get('carb_intake', 200))
    fat_g = float(initial_data.get('fat_intake', 60))
    diet_type = initial_data.get('diet_type', 'standard')
    
    # Calculate total calories and nutrition ratios
    nutrition_info = diet_calculations.calculate_nutrition_info(protein_g, carbs_g, fat_g, diet_type)
    
    # Calculate expected weekly fat loss and muscle gain
    weekly_fat_loss = diet_calculations.calculate_weekly_rate_of_fat_loss(
        initial_weight, initial_body_fat, tdee, 
        nutrition_info['total_calories'], diet_type, activity_level
    )
    
    weekly_muscle_gain = diet_calculations.calculate_weekly_muscle_gain(
        initial_weight, initial_body_fat, protein_g, 
        diet_type, initial_data.get('resistance_training', False), 
        str(initial_data.get('experience_level', '3'))[0]
    )
    
    # Calculate expected body composition progression
    projected_progression = diet_calculations.project_body_composition_changes(
        initial_weight, initial_body_fat, 
        initial_data['goal_weight'], initial_data['goal_bf'], 
        protein_g, carbs_g, fat_g, diet_type, tdee, activity_level,
        initial_data.get('resistance_training', False),
        str(initial_data.get('experience_level', '3'))[0]
    )
    
    # Get diet-specific effects
    fat_loss_multiplier, muscle_gain_multiplier = diet_calculations.get_diet_multipliers(diet_type)
    diet_fat_loss_effect = "Enhanced" if fat_loss_multiplier > 1.0 else ("Reduced" if fat_loss_multiplier < 1.0 else "Neutral")
    diet_muscle_gain_effect = "Enhanced" if muscle_gain_multiplier > 1.0 else ("Reduced" if muscle_gain_multiplier < 1.0 else "Neutral")
    
    # Prepare report data
    report_data = {
        'name': initial_data['name'],
        'report_date': datetime.datetime.now().strftime("%m/%d/%Y"),
        'start_date': start_date_str_converted,
        'end_date': convert_date_string(progression[-1]['date']),
        'age': calculated_age,
        'gender': gender_display,
        'height': f"{height_feet}'{'0' if height_inches == 0 else height_inches}\" ({height_cm:.1f} cm)",
        'email': initial_data.get('email', 'Not provided'),
        'phone': initial_data.get('phone', 'Not provided'),
        'initial_weight': initial_weight,
        'final_weight': progression[-1]['weight'],
        'current_weight': progression[-1]['weight'],
        'current_bf': progression[-1]['body_fat_percentage'],
        'goal_weight': initial_data['goal_weight'],
        'initial_body_fat': initial_body_fat,
        'final_body_fat': progression[-1]['body_fat_percentage'],
        'goal_body_fat': initial_data['goal_bf'],
        'activity_level': get_activity_level_description(activity_level),
        'experience_level': initial_data['experience_level'],
        'initial_rmr': rmr,
        'initial_tdee': tdee,
        'tef': initial_data.get('tef', calculate_tef(initial_data.get('protein_intake', 150))),
        'neat': initial_data.get('neat', calculate_neat(initial_data.get('job_activity', 'light'), initial_data.get('leisure_activity', 'moderate'))),
        'initial_daily_calorie_intake': progression[0]['daily_calorie_intake'],
        'workout_type': initial_data.get('workout_type', 'Not specified'),
        'workout_frequency': initial_data.get('workout_days', 0),
        'resistance_training': 'Yes' if initial_data.get('resistance_training', False) else 'No',
        'athlete_status': 'Yes' if initial_data.get('is_athlete', False) else 'No',
        'initial_lean_mass': progression[0]['lean_mass'],
        'initial_fat_mass': progression[0]['fat_mass'],
        'weekly_muscle_gain': weekly_muscle_gain,
        'protein_intake': protein_g,
        'carb_intake': carbs_g,
        'fat_intake': fat_g,
        'diet_type': diet_type,
        # Nutrition analysis
        'total_daily_calories': nutrition_info['total_calories'],
        'protein_ratio': nutrition_info['protein_ratio'],
        'carbs_ratio': nutrition_info['carbs_ratio'],
        'fat_ratio': nutrition_info['fat_ratio'],
        'diet_quality': nutrition_info['diet_quality'],
        'diet_warnings': nutrition_info['warnings'],
        # Diet-based projections
        'weekly_fat_loss': weekly_fat_loss,
        'diet_fat_loss_effect': diet_fat_loss_effect, 
        'diet_muscle_gain_effect': diet_muscle_gain_effect,
        'weeks_to_goal': len(projected_progression) if projected_progression else "Unknown"
    }
    
    # Add weekly progress data
    report_data['weekly_progress'] = [
        {**week, 'date': convert_date_string(week['date'])}
        for week in progression
    ]
    
    # Add metabolic adaptation data
    report_data.update({
        'week_1_adaptation': 1.0,
        'final_week_adaptation': progression[-1].get('tdee', tdee) / rmr,
        'total_weeks': len(progression) - 1,
        'total_weight_loss': initial_weight - progression[-1]['weight'],
        'total_bf_loss': initial_body_fat - progression[-1]['body_fat_percentage'],
        'avg_weekly_loss': (initial_weight - progression[-1]['weight']) / (len(progression) - 1) if len(progression) > 1 else 0,
        'total_muscle_gain': sum(week.get('muscle_gain', 0) for week in progression),
        'final_daily_calorie_intake': progression[-1].get('daily_calorie_intake', tdee - 500),
        'final_tdee': progression[-1].get('tdee', tdee),
        'final_weekly_caloric_output': progression[-1].get('weekly_caloric_output', tdee * 7),
    })
    
    # Add body fat category information
    initial_bf_info = get_body_fat_info(gender_code, initial_body_fat)
    final_bf_info = get_body_fat_info(gender_code, progression[-1]['body_fat_percentage'])
    
    report_data.update({
        'initial_body_fat_category': initial_bf_info[0],
        'initial_body_fat_description': initial_bf_info[2],
        'initial_time_to_six_pack': initial_bf_info[1],
        'final_body_fat_category': final_bf_info[0],
        'final_body_fat_description': final_bf_info[2],
        'final_time_to_six_pack': final_bf_info[1],
        'adaptation_percentage': (1 - (progression[-1].get('tdee', tdee) / rmr)) * 100,
        'lean_mass_preserved': (progression[-1].get('lean_mass', lean_mass) / lean_mass) * 100,
        'avg_muscle_gain': sum(week.get('muscle_gain', 0) for week in progression) / (len(progression) - 1) if len(progression) > 1 else 0,
    })

    # Ensure body_composition_changes is populated
    report_data['body_composition_changes'] = []
    for week in progression:
        bf_info = get_body_fat_info(gender_code, week['body_fat_percentage'])
        report_data['body_composition_changes'].append({
            'category': bf_info[0],
            'body_fat_percentage': week['body_fat_percentage'],
            'date_reached': convert_date_string(week['date']),
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
    """Calculate the age of the user based on birth date and start date."""
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
    """Calculate the Thermic Effect of Food (TEF) based on protein intake."""
    try:
        return float(protein_intake) * 0.1
    except (ValueError, TypeError):
        return 15  # Default value if protein_intake is not valid

def calculate_neat(job_activity, leisure_activity):
    """Calculate Non-Exercise Activity Thermogenesis (NEAT) based on activity levels."""
    activity_levels = {'sedentary': 1, 'light': 2, 'moderate': 3, 'active': 4}
    
    job_level = activity_levels.get(str(job_activity).lower(), 2)
    leisure_level = activity_levels.get(str(leisure_activity).lower(), 2)
    
    return (job_level + leisure_level) * 50

def get_activity_level_description(activity_level):
    """Get a description of the activity level."""
    descriptions = {
        '1': 'Sedentary (little or no exercise)',
        '2': 'Lightly Active (light exercise/sports 1-3 days/week)',
        '3': 'Moderately Active (moderate exercise/sports 3-5 days/week)',
        '4': 'Very Active (hard exercise/sports 6-7 days/week)',
        '5': 'Extra Active (very hard exercise/physical job/training twice a day)'
    }
    return descriptions.get(str(activity_level), 'Unknown activity level')

def get_score_description(score):
    """Get a description for a score based on its value."""
    try:
        score_float = float(score)
        if score_float < 0.2:
            return "Very Low"
        elif score_float < 0.4:
            return "Low"
        elif score_float < 0.6:
            return "Moderate"
        elif score_float < 0.8:
            return "High"
        else:
            return "Very High"
    except (ValueError, TypeError):
        return "Unknown"

def convert_date_string(date_str):
    """Convert date string from various formats to MM/DD/YYYY format"""
    try:
        # Try MM/DD/YYYY format first (most common user input format)
        return datetime.datetime.strptime(date_str, "%m/%d/%Y").strftime("%m/%d/%Y")
    except ValueError:
        try:
            # Try MMDDYY format next (legacy format)
            return datetime.datetime.strptime(date_str, "%m%d%y").strftime("%m/%d/%Y")
        except ValueError:
            try:
                # Try YYMMDD format 
                return datetime.datetime.strptime(date_str, "%y%m%d").strftime("%m/%d/%Y")
            except ValueError:
                try:
                    # Try DD/MM/YYYY format
                    return datetime.datetime.strptime(date_str, "%d/%m/%Y").strftime("%m/%d/%Y")
                except ValueError:
                    try:
                        # Try YYYY-MM-DD format
                        return datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%m/%d/%Y")
                    except ValueError:
                        # If all formats fail, return the original string
                        print(f"Warning: Could not parse date format for '{date_str}', using as-is")
                        return date_str

def get_body_fat_info(gender, body_fat_percentage):
    """Get information about body fat percentage, including category, time to six-pack, and description."""
    categories = [
        {"name": "Very Lean", "men": 10, "women": 18, "time": "3-4 weeks", "description": "Visible abs, vascularity, striations"},
        {"name": "Lean", "men": 14, "women": 22, "time": "2-3 months", "description": "Some muscle definition, less visible abs"},
        {"name": "Average", "men": 19, "women": 27, "time": "3-4 months", "description": "Little muscle definition, soft look"},
        {"name": "Above Average", "men": 24, "women": 32, "time": "4-6 months", "description": "No visible abs, excess fat"},
        {"name": "High Body Fat", "men": 29, "women": 37, "time": "6-12 months", "description": "Excess fat all around, round physique"},
        {"name": "Obese", "men": float('inf'), "women": float('inf'), "time": "12+ months", "description": "Significant excess fat all around"}
    ]

    threshold_key = "men" if gender.lower() == 'male' else "women"

    for category in categories:
        if body_fat_percentage < category[threshold_key]:
            return category["name"], category["time"], category["description"]

    return categories[-1]["name"], categories[-1]["time"], categories[-1]["description"]

if __name__ == "__main__":
    # This block is for testing purposes only
    print("Enhanced report generation module loaded.")

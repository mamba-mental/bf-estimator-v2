import os
import datetime
import base64
import io
import matplotlib.pyplot as plt
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FOLDER = os.path.join(SCRIPT_DIR, "results")
TEMPLATE_FOLDER = os.path.join(SCRIPT_DIR, "templates")
CSS_FILE = os.path.join(SCRIPT_DIR, "styles", "report_style.css")

def save_report(report_data, username, save_format):
    if not os.path.exists(RESULTS_FOLDER):
        os.makedirs(RESULTS_FOLDER)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{username}_{timestamp}"
    
    if save_format in ['markdown', 'both']:
        markdown_filename = os.path.join(RESULTS_FOLDER, f"{base_filename}.md")
        with open(markdown_filename, 'w') as f:
            f.write(generate_markdown(report_data))
        print(f"Markdown report saved as {markdown_filename}")

    if save_format in ['pdf', 'both']:
        pdf_filename = os.path.join(RESULTS_FOLDER, f"{base_filename}.pdf")
        try:
            html_content = generate_html(report_data)
            HTML(string=html_content).write_pdf(pdf_filename, stylesheets=[CSS(filename=CSS_FILE)])
            print(f"PDF report saved as {pdf_filename}")
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")

def generate_markdown(report_data):
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
    env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))
    
    # Add the get_score_description function to the template environment
    env.globals['get_score_description'] = get_score_description
    
    template = env.get_template('report_template.html')
    
    # Generate charts
    report_data['weight_progress_chart'] = generate_weight_progress_chart(report_data['weekly_progress'])
    report_data['body_composition_chart'] = generate_body_composition_chart(report_data['body_composition_changes'])
    
    return template.render(report_data)


def generate_weight_progress_chart(weekly_progress):
    dates = [datetime.datetime.strptime(week['date'], '%m%d%y') for week in weekly_progress]
    weights = [week['weight'] for week in weekly_progress]
    
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
    dates = [datetime.datetime.strptime(change['date_reached'], '%m/%d/%Y') for change in body_composition_changes]
    body_fat_percentages = [change['body_fat_percentage'] for change in body_composition_changes]
    
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
    if save_option == 'y':
        save_format = input("Choose the format to save (markdown/pdf/both): ").lower()
        if save_format in ['markdown', 'pdf', 'both']:
            save_report(report_data, initial_data.get('name', 'User'), save_format)
        else:
            print("Invalid format choice. Report will not be saved.")
    else:
        print("Report will not be saved.")

def generate_comprehensive_report(progression, initial_data):
    report_data = {
        'name': initial_data['name'],
        'report_date': datetime.datetime.now().strftime("%m/%d/%Y"),
        'start_date': datetime.datetime.strptime(progression[0]['date'], "%m%d%y").strftime("%m/%d/%Y"),
        'end_date': datetime.datetime.strptime(progression[-1]['date'], "%m%d%y").strftime("%m/%d/%Y"),
        'age': calculate_age(initial_data['dob'], datetime.datetime.strptime(progression[0]['date'], "%m%d%y")),
        'gender': 'Male' if initial_data['gender'].lower() == 'm' else 'Female',
        'height': f"{initial_data['height_feet']}'{'0' if initial_data['height_inches'] == 0 else initial_data['height_inches']}\" ({initial_data['height_cm']:.1f} cm)",
        'initial_weight': progression[0]['weight'],
        'final_weight': progression[-1]['weight'],
        'goal_weight': initial_data['goal_weight'],
        'initial_body_fat': progression[0]['body_fat_percentage'],
        'final_body_fat': progression[-1]['body_fat_percentage'],
        'goal_body_fat': initial_data['goal_bf'],
        'activity_level': initial_data['activity_level_description'],
        'experience_level': initial_data['experience_level'],
        'initial_rmr': progression[0]['rmr'],
        'initial_tdee': progression[0]['tdee'],
        'tef': initial_data.get('tef', calculate_tef(initial_data['protein_intake'])),
        'neat': initial_data.get('neat', calculate_neat(initial_data['job_activity'], initial_data['leisure_activity'])),
        'initial_daily_calorie_intake': progression[0]['daily_calorie_intake'],
        'workout_type': get_workout_type_description(initial_data['workout_type']),
        'workout_frequency': initial_data['workout_days'],
        'volume_score': initial_data['volume_score'],
        'intensity_score': initial_data['intensity_score'],
        'frequency_score': initial_data['frequency_score'],
        'resistance_training': 'Yes' if initial_data['resistance_training'] else 'No',
        'athlete_status': 'Yes' if initial_data['is_athlete'] else 'No',
        'initial_lean_mass': progression[0]['lean_mass'],
        'initial_fat_mass': progression[0]['fat_mass'],
        'weekly_muscle_gain': sum(week['muscle_gain'] for week in progression) / len(progression),
        'weekly_progress': [
            {**week, 'date': datetime.datetime.strptime(week['date'], "%m%d%y").strftime("%m/%d/%Y")}
            for week in progression
        ],
        'body_composition_changes': [
            {**change, 'date_reached': datetime.datetime.strptime(change['date_reached'], "%m/%d/%Y").strftime("%m/%d/%Y")}
            for change in initial_data.get('body_composition_changes', [])
        ],
        'week_1_adaptation': 1.0,
        'final_week_adaptation': progression[-1]['tdee'] / progression[0]['tdee'],
        'total_weeks': len(progression) - 1,
        'total_weight_loss': progression[0]['weight'] - progression[-1]['weight'],
        'total_bf_loss': progression[0]['body_fat_percentage'] - progression[-1]['body_fat_percentage'],
        'avg_weekly_loss': (progression[0]['weight'] - progression[-1]['weight']) / (len(progression) - 1),
        'total_muscle_gain': sum(week['muscle_gain'] for week in progression),
        'final_daily_calorie_intake': progression[-1]['daily_calorie_intake'],
        'final_tdee': progression[-1]['tdee'],
        'final_weekly_caloric_output': progression[-1]['weekly_caloric_output'],
    }
    
    # Add body fat category information
    initial_bf_info = get_body_fat_info(initial_data['gender'], progression[0]['body_fat_percentage'])
    final_bf_info = get_body_fat_info(initial_data['gender'], progression[-1]['body_fat_percentage'])
    
    report_data.update({
        'initial_body_fat_category': initial_bf_info[0],
        'initial_body_fat_description': initial_bf_info[2],
        'initial_time_to_six_pack': initial_bf_info[1],
        'final_body_fat_category': final_bf_info[0],
        'final_body_fat_description': final_bf_info[2],
        'final_time_to_six_pack': final_bf_info[1],
        'adaptation_percentage': (1 - (progression[-1]['tdee'] / progression[0]['tdee'])) * 100,
        'lean_mass_preserved': (progression[-1]['lean_mass'] / progression[0]['lean_mass']) * 100,
        'avg_muscle_gain': sum(week['muscle_gain'] for week in progression) / (len(progression) - 1),
    })

    # Ensure body_composition_changes is populated
    report_data['body_composition_changes'] = []
    for week in progression:
        bf_info = get_body_fat_info(initial_data['gender'], week['body_fat_percentage'])
        report_data['body_composition_changes'].append({
            'category': bf_info[0],
            'body_fat_percentage': week['body_fat_percentage'],
            'date_reached': datetime.datetime.strptime(week['date'], "%m%d%y").strftime("%m/%d/%Y"),
            'description': bf_info[2],
            'time_to_six_pack': bf_info[1]
        })

    # Generate charts
    report_data['weight_progress_chart'] = generate_weight_progress_chart(report_data['weekly_progress'])
    report_data['body_composition_chart'] = generate_body_composition_chart(report_data['body_composition_changes'])

    # Round all float values to one decimal place
    for key, value in report_data.items():
        if isinstance(value, float):
            report_data[key] = round(value, 1)

    return report_data

def calculate_age(birth_date, start_date):
    return start_date.year - birth_date.year - ((start_date.month, start_date.day) < (birth_date.month, birth_date.day))

def calculate_tef(protein_intake):
    # Placeholder function, replace with actual calculation
    return protein_intake * 0.1

def calculate_neat(job_activity, leisure_activity):
    # Placeholder function, replace with actual calculation
    activity_levels = {'sedentary': 1, 'light': 2, 'moderate': 3, 'active': 4}
    return (activity_levels[job_activity] + activity_levels[leisure_activity]) * 50

def get_workout_type_description(workout_type):
    descriptions = {
        1: "Bodybuilding (focus on muscle hypertrophy)",
        2: "Strength Training (focus on increasing maximal strength)",
        3: "Powerlifting (focus on squat, bench press, and deadlift)",
        4: "Olympic Weightlifting (focus on snatch and clean & jerk)",
        5: "Crossfit (high-intensity functional training)",
        6: "Calisthenics (bodyweight exercises)",
        7: "General Fitness (balanced approach to overall health and fitness)"
    }
    return descriptions.get(workout_type, "Custom workout plan")

def get_score_description(score):
    if score < 0.2:
        return "Very Low"
    elif score < 0.4:
        return "Low"
    elif score < 0.6:
        return "Moderate"
    elif score < 0.8:
        return "High"
    else:
        return "Very High"

def get_body_fat_info(gender, body_fat_percentage):
    categories = [
        {"name": "Very Lean", "men": 10, "women": 18, "time": "3-4 weeks", "description": "Visible abs, vascularity, striations"},
        {"name": "Lean", "men": 14, "women": 22, "time": "2-3 months", "description": "Some muscle definition, less visible abs"},
        {"name": "Average", "men": 19, "women": 27, "time": "3-4 months", "description": "Little muscle definition, soft look"},
        {"name": "Above Average", "men": 24, "women": 32, "time": "4-6 months", "description": "No visible abs, excess fat"},
        {"name": "High Body Fat", "men": 29, "women": 37, "time": "6-12 months", "description": "Excess fat all around, round physique"},
        {"name": "Obese", "men": float('inf'), "women": float('inf'), "time": "12+ months", "description": "Significant excess fat all around"}
    ]

    threshold_key = "men" if gender.lower() == 'm' else "women"

    for category in categories:
        if body_fat_percentage < category[threshold_key]:
            return category["name"], category["time"], category["description"]

    return categories[-1]["name"], categories[-1]["time"], categories[-1]["description"]

def generate_weight_progress_chart(weekly_progress):
    dates = [datetime.datetime.strptime(week['date'], "%m/%d/%Y") for week in weekly_progress]
    weights = [week['weight'] for week in weekly_progress]
    
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
    dates = [datetime.datetime.strptime(change['date_reached'], "%m/%d/%Y") for change in body_composition_changes]
    body_fat_percentages = [change['body_fat_percentage'] for change in body_composition_changes]
    
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


if __name__ == "__main__":
    # This block is for testing purposes only
    test_progression = [
        {"date": "010123", "weight": 200, "body_fat_percentage": 25, "lean_mass": 150, "fat_mass": 50, "rmr": 1800, "tdee": 2500, "daily_calorie_intake": 2000, "weekly_caloric_output": 17500, "muscle_gain": 0.1},
        {"date": "010823", "weight": 198, "body_fat_percentage": 24, "lean_mass": 150.5, "fat_mass": 47.5, "rmr": 1790, "tdee": 2480, "daily_calorie_intake": 1980, "weekly_caloric_output": 17360, "muscle_gain": 0.1}
    ]
    test_initial_data = {
        "name": "John Doe",
        "dob": "010190",
        "gender": "m",
        "height_feet": 5,
        "height_inches": 10,
        "height_cm": 177.8,
        "goal_weight": 180,
        "goal_bf": 15,
        "activity_level_description": "Moderate exercise/sports 3-5 days/week",
        "experience_level": "Intermediate (2-4 years)",
        "protein_intake": 150,
        "workout_type": "Bodybuilding",
        "workout_days": 4,
        "volume_score": 0.7,
        "intensity_score": 0.8,
        "frequency_score": 0.9,
        "resistance_training": True,
        "is_athlete": False,
        "job_activity": "light",
        "leisure_activity": "moderate",
        "is_bodybuilder": True
    }
    print_summary(test_progression, test_initial_data)

# --- Footer ---
# Status: Development
# Contact: mambamental3mil@gmail.com
# © 2024 Mamba Matrix Solutions LLC. All rights reserved.
# --- End of File ---
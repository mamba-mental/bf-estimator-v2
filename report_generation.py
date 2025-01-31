# report_generation.py
import os
import datetime
import json
import base64
import io
import ctypes
import matplotlib

matplotlib.use('Agg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
plt.style.use('seaborn-v0_8-whitegrid')  # Use a clean, modern style with white background
matplotlib.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial'],
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'axes.unicode_minus': False,
    'date.autoformatter.year': '%Y',
    'date.autoformatter.month': '%m/%d/%Y',
    'date.autoformatter.day': '%m/%d/%Y',
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'savefig.facecolor': 'white',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.figsize': [12, 7],
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.3,
    'savefig.dpi': 300,
    'savefig.format': 'png',
    'savefig.transparent': False,
    'figure.max_open_warning': 0,
    'agg.path.chunksize': 10000
})

from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from utils import estimate_tef, estimate_neat


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FOLDER = os.path.join(SCRIPT_DIR, "results")
TEMPLATE_FOLDER = os.path.join(SCRIPT_DIR, "templates")
CSS_FILE = os.path.join(SCRIPT_DIR, "styles", "report_style.css")


def get_body_fat_info(gender, body_fat_percentage):
    """
    Get body fat category information.
    """
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
    """
    Generate a weight progress chart.
    """
    dates = [datetime.datetime.strptime(week['date'], "%m/%d/%y") for week in weekly_progress]
    weights = [week['weight'] for week in weekly_progress]

    fig, ax = plt.subplots()
    ax.plot(dates, weights, marker='o', linestyle='-', color='b')
    ax.set_title('Weight Progress Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Weight (lbs)')
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return image_base64


def generate_body_composition_chart(body_composition_changes):
    """
    Generate a body composition changes chart.
    """
    dates = [datetime.datetime.strptime(change['date_reached'], "%m/%d/%y") for change in body_composition_changes]
    body_fat = [change['body_fat_percentage'] for change in body_composition_changes]

    fig, ax = plt.subplots()
    ax.plot(dates, body_fat, marker='s', linestyle='--', color='r')
    ax.set_title('Body Fat Percentage Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Body Fat %')
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return image_base64


def generate_comprehensive_report(progression, initial_data):
    """
    Generate a comprehensive report from progression and initial data.
    """
    report_data = {
        'name': initial_data['name'],
        'report_date': datetime.datetime.now().strftime("%m/%d/%Y"),
        'start_date': datetime.datetime.strptime(progression[0]['date'], "%m%d%y").strftime("%m/%d/%y"),
        'end_date': datetime.datetime.strptime(progression[-1]['date'], "%m%d%y").strftime("%m/%d/%y"),
        'age': initial_data['age'],
        'gender': 'Male' if initial_data['gender'].lower() == 'm' else 'Female',
        'height': f"{initial_data['height_feet']}'{'0' if initial_data['height_inches'] == 0 else initial_data['height_inches']}\" ({initial_data['height_cm']:.2f} cm)",
        'initial_weight': progression[0]['weight'],
        'final_weight': progression[-1]['weight'],
        'goal_weight': initial_data['goal_weight'],
        'initial_body_fat': progression[0]['body_fat_percentage'],
        'final_body_fat': progression[-1]['body_fat_percentage'],
        'goal_body_fat': initial_data['goal_bf'],
        'activity_level': initial_data.get('activity_level_description', 'Unknown'),
        'experience_level': initial_data['experience_level'],
        'initial_rmr': progression[0]['rmr'],
        'initial_tdee': progression[0]['tdee'],
        'tef': estimate_tef(initial_data.get('protein_intake', initial_data.get('daily_protein_intake', 0))),
        'neat': estimate_neat(initial_data['job_activity'], initial_data['leisure_activity']),
        'initial_daily_calorie_intake': progression[0]['daily_calorie_intake'],
        'workout_type': initial_data['workout_type'],
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
            {**week, 'date': datetime.datetime.strptime(week['date'], "%m%d%y").strftime("%m/%d/%y")}
            for week in progression
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

    report_data['body_composition_changes'] = []
    for week in progression:
        bf_info = get_body_fat_info(initial_data['gender'], week['body_fat_percentage'])
        report_data['body_composition_changes'].append({
            'category': bf_info[0],
            'body_fat_percentage': week['body_fat_percentage'],
            'date_reached': datetime.datetime.strptime(week['date'], "%m%d%y").strftime("%m/%d/%y"),
            'description': bf_info[2],
            'time_to_six_pack': bf_info[1]
        })

    report_data['weight_progress_chart'] = generate_weight_progress_chart(report_data['weekly_progress'])
    report_data['body_composition_chart'] = generate_body_composition_chart(report_data['body_composition_changes'])

    html_content = generate_html(report_data)
    base_url = os.path.dirname(os.path.abspath(__file__))

    # Convert HTML to PDF using WeasyPrint with CSS
    try:
        html = HTML(string=html_content, base_url=base_url)
        css = [CSS(filename=CSS_FILE)]
        pdf_content = html.write_pdf(stylesheets=css)
        print("PDF generation successful")
    except Exception as e:
        print(f"Error generating PDF: {e}")
        pdf_content = b''
    report_data['pdf_content'] = pdf_content

    return report_data


def save_report(report_data, username, save_format):
    """
    Save the report in the specified format(s).
    """
    saved_files = {}
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{username.replace(' ', '_')}_{timestamp}"
    results_folder = RESULTS_FOLDER  # Use the constant defined at module level

    # Ensure results directory exists
    os.makedirs(results_folder, exist_ok=True)

    # Save weight progress chart
    weight_chart_filename = os.path.join(results_folder, f"weight_progress_chart_{timestamp}.png")
    with open(weight_chart_filename, 'wb') as f:
        f.write(base64.b64decode(report_data['weight_progress_chart']))

    # Save body composition chart
    body_comp_chart_filename = os.path.join(results_folder, f"body_composition_chart_{timestamp}.png")
    with open(body_comp_chart_filename, 'wb') as f:
        f.write(base64.b64decode(report_data['body_composition_chart']))

    if save_format in ['markdown', 'md', 'both']:
        markdown_filename = os.path.join(results_folder, f"{base_filename}.md")
        markdown_content = generate_markdown(report_data, weight_chart_filename, body_comp_chart_filename)
        with open(markdown_filename, 'w') as f:
            f.write(markdown_content)
        saved_files['markdown'] = markdown_filename

    if save_format in ['pdf', 'both']:
        try:
            pdf_filename = os.path.join(results_folder, f"{base_filename}.pdf")
            pdf_content = report_data.get('pdf_content', b'')
            if pdf_content:
                with open(pdf_filename, 'wb') as f:
                    f.write(pdf_content)
                saved_files['pdf'] = pdf_filename
            else:
                print("PDF generation was not successful, skipping PDF save")
        except Exception as e:
            print(f"Error saving PDF: {e}")

    if save_format in ['json', 'both']:
        json_filename = os.path.join(results_folder, f"{base_filename}.json")
        json_data = report_data.copy()
        if 'pdf_content' in json_data:
            json_data['pdf_content'] = base64.b64encode(json_data['pdf_content']).decode('utf-8')
        with open(json_filename, 'w') as f:
            json.dump(json_data, f, default=str)
        saved_files['json'] = json_filename

    return saved_files


def generate_html(report_data):
    """
    Generate HTML content for the report using Jinja2 templates.
    """
    env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))
    template = env.get_template('report_template.html')
    html_content = template.render({**report_data, 'get_score_description': get_score_description})
    return html_content


def get_score_description(score):
    """
    Provide a description based on the score.
    """
    if score < 1:
        return "Low"
    elif 1 <= score < 3:
        return "Moderate"
    else:
        return "High"


def generate_markdown(report_data, weight_chart_path=None, body_comp_chart_path=None):
    """
    Generate markdown content for the report.
    """
    markdown = f"""# Body Fat and Weight Loss Calculator Report - {report_data['name']}

Report Date: {report_data['report_date']}

## 1. Current Profile

- Height: {report_data['height']}
- Current Weight: {report_data['initial_weight']:.2f} lbs
- Current Body Fat: {report_data['initial_body_fat']:.2f}%
- Current Lean Mass: {report_data['initial_lean_mass']:.2f} lbs
- Current Fat Mass: {report_data['initial_fat_mass']:.2f} lbs
- Age: {report_data['age']} years
- Gender: {report_data['gender']}

## 2. Target Goals

- Goal Weight: {report_data['goal_weight']:.2f} lbs
- Goal Body Fat: {report_data['goal_body_fat']:.2f}%
- Timeline: {report_data['start_date']} to {report_data['end_date']}
- Total Duration: {report_data['total_weeks']} weeks

## 3. Current Activity Profile

- Activity Level: {report_data['activity_level']}
- Training Experience: {report_data['experience_level']}
- Workout Type: {report_data['workout_type']}
- Weekly Workout Frequency: {report_data['workout_frequency']} days
- Currently Using Resistance Training: {report_data['resistance_training']}
- Athlete Status: {report_data['athlete_status']}

## 4. Current Metabolic Profile

These calculations provide insight into your body's energy requirements and how they will change over time:

- Base Metabolic Rate (RMR): {report_data['initial_rmr']:.2f} cal/day
- Total Daily Energy Expenditure (TDEE): {report_data['initial_tdee']:.2f} cal/day
- Thermic Effect of Food (TEF): {report_data['tef']:.2f} cal/day
- Non-Exercise Activity Thermogenesis (NEAT): {report_data['neat']:.2f} cal/day
- Recommended Daily Calorie Intake: {report_data['initial_daily_calorie_intake']:.2f} cal/day

### Understanding Your Metabolic Profile:
- RMR: Your body burns {report_data['initial_rmr']:.2f} calories daily at rest. This is calculated using the Mifflin-St Jeor equation, adjusted for your body composition.
- TDEE: Based on your activity level, you burn approximately {report_data['initial_tdee']:.2f} calories per day.
- TEF: You burn about {report_data['tef']:.2f} calories digesting food, particularly protein.
- NEAT: Your daily activities burn approximately {report_data['neat']:.2f} additional calories.

## 5. Workout Analysis

This analysis provides insight into your workout routine and its effectiveness:

- Type: {report_data['workout_type']}
- Frequency: {report_data['workout_frequency']} days/week
- Volume Score: {report_data['volume_score']:.2f} - {get_score_description(report_data['volume_score'])}
- Intensity Score: {report_data['intensity_score']:.2f} - {get_score_description(report_data['intensity_score'])}
- Frequency Score: {report_data['frequency_score']:.2f} - {get_score_description(report_data['frequency_score'])}

### Impact on Your Caloric Needs:
- Volume Score {report_data['volume_score']:.2f}: Your training volume contributes approximately {report_data['volume_score'] * 500:.2f} additional calories to your daily expenditure.
- Intensity Score {report_data['intensity_score']:.2f}: Your training intensity increases your metabolic rate by about {report_data['intensity_score'] * 15:.2f}% for up to 48 hours post-workout.
- Frequency Score {report_data['frequency_score']:.2f}: Training {report_data['workout_frequency']} days per week optimizes your caloric burn and recovery periods.

## 6. Predicted Progress Charts

### Weight Progress Chart
![Weight Progress Chart]({os.path.basename(weight_chart_path)})

### Body Fat Changes Chart
![Body Composition Chart]({os.path.basename(body_comp_chart_path)})

## 7. Weekly Progress Forecast

| Date | Weight (lbs) | Body Fat % | Daily Cal Intake | TDEE | Weekly Cal Output | Total Weight Lost (lbs) | Lean Mass (lbs) | Fat Mass (lbs) | Muscle Gain (lbs) | RMR |
|------|-------------|------------|------------------|------|-------------------|------------------------|-----------------|---------------|-------------------|-----|
"""
    for week in report_data['weekly_progress']:
        markdown += f"| {week['date']} | {week['weight']:.2f} | {week['body_fat_percentage']:.2f} | {week['daily_calorie_intake']:.2f} | {week['tdee']:.2f} | {week['weekly_caloric_output']:.2f} | {week.get('total_weight_lost', 0):.2f} | {week['lean_mass']:.2f} | {week['fat_mass']:.2f} | {week['muscle_gain']:.2f} | {week['rmr']:.2f} |\n"

    markdown += f"""
## 8. Body Composition Changes

| Body Fat Category | Body Fat % | Date Reached | Description | Est. Time to Six-Pack |
|------------------|------------|--------------|-------------|-----------------------|
"""
    for change in report_data['body_composition_changes']:
        markdown += f"| {change['category']} | {change['body_fat_percentage']:.2f}% | {change['date_reached']} | {change['description']} | {change['time_to_six_pack']} |\n"

    markdown += f"""
## 9. Expected Results

You can expect to achieve:
- Total Weight Loss: {report_data['total_weight_loss']:.2f} lbs
- Fat Loss: {report_data['total_bf_loss']:.2f}%
- Muscle Gain: {report_data['total_muscle_gain']:.2f} lbs

Average Weekly Changes:
- Weight Loss: {report_data['avg_weekly_loss']:.2f} lbs
- Muscle Gain: {report_data['avg_muscle_gain']:.2f} lbs

## 10. Metabolic Adaptation Forecast

Your metabolism will adapt throughout this journey:
- Initial Week: {report_data['week_1_adaptation']:.2f} multiplier
- Final Week: {report_data['final_week_adaptation']:.2f} multiplier
- Expected Adaptation: {report_data['adaptation_percentage']:.2f}% change
- Lean Mass Preservation: {report_data['lean_mass_preserved']:.2f}%

## 11. Final Phase Targets

To maintain your results at the end of your journey:
- Maintenance Calories: {report_data['final_tdee']:.2f} calories/day
- Weekly Energy Output: {report_data['final_weekly_caloric_output']:.2f} calories

## 12. Terms and Definitions Reference

### Activity Levels and Their Impact:
- **Sedentary:** Little to no exercise, desk job (multiplier: 1.2, +20% above RMR)
- **Lightly Active:** Light exercise 1-3 days/week (multiplier: 1.375, +37.5% above RMR)
- **Moderately Active:** Moderate exercise 3-5 days/week (multiplier: 1.55, +55% above RMR)
- **Very Active:** Heavy exercise 6-7 days/week (multiplier: 1.725, +72.5% above RMR)
- **Extremely Active:** Very heavy exercise, physical job (multiplier: 1.9, +90% above RMR)

### Training Experience and Muscle Gain Potential:
- **Beginner (0-2 years):** Higher potential for muscle gain (0.5-1% body weight/month), requires +500 cal/day surplus
- **Intermediate (2-4 years):** Moderate gains (0.25-0.5% body weight/month), requires +300-400 cal/day surplus
- **Advanced (4+ years):** Slower gains (0.125-0.25% body weight/month), requires +200-300 cal/day surplus

### Workout Types and Their Effects:
- **Bodybuilding:** 600-800 cal/session, 24-36 hour EPOC effect, high protein needs (1g/lb)
- **Strength Training:** 400-600 cal/session, 24-48 hour EPOC effect, high CNS recovery needs
- **Powerlifting:** 500-700 cal/session, 36-48 hour EPOC effect, very high CNS demands
- **Olympic Weightlifting:** 600-800 cal/session, 24-36 hour EPOC effect, technical recovery focus
- **CrossFit:** 800-1000 cal/session, 36-48 hour EPOC effect, high systemic demands
- **Calisthenics:** 400-600 cal/session, 24-36 hour EPOC effect, joint/tendon focus

### Resistance Training Impact:
- **With RT:** 90-100% muscle preservation, +100-300 cal/day through increased muscle mass and EPOC
- **Without RT:** 60-80% muscle preservation, no additional metabolic benefit

### Athlete Status Effects:
- **Athlete:** +10-15% higher metabolic rate, enhanced nutrient partitioning efficiency
- **Non-Athlete:** Standard metabolic rate and normal nutrient partitioning

### Workout Analysis Metrics:
- **Volume Score:** Total work done (sets × reps × weight), contributes 100-500 additional daily calories
- **Intensity Score:** Average weight relative to 1RM, increases metabolic rate 5-15% for 24-48 hours
- **Frequency Score:** Training frequency per muscle group, optimizes recovery and adaptation

### Caloric Components:
- **RMR:** Base calories burned at rest (Mifflin-St Jeor equation with body composition adjustments)
- **TDEE:** Total daily calories (RMR × Activity Multiplier + Exercise Calories)
- **TEF:** 10-15% of total caloric intake, higher with protein-rich meals
- **NEAT:** Daily activity calories, varies by lifestyle and job type

### Calculation Formulas:
- **RMR (Male):** (10 × weight kg) + (6.25 × height cm) - (5 × age) + 5
- **RMR (Female):** (10 × weight kg) + (6.25 × height cm) - (5 × age) - 161
- **TDEE:** RMR × Activity Multiplier + Exercise Calories
- **Caloric Deficit:** TDEE - Daily Intake
- **Weekly Fat Loss:** (Weekly Deficit) ÷ 3,500 calories
- **Muscle Gain:** Based on training experience (0.125-1% body weight per month)
- **Metabolic Adaptation:** Progressive reduction in TDEE based on deficit duration
"""
    return markdown


def print_summary(progression, initial_data):
    """
    Print and save the summary report of weight loss progression.
    """
    report_data = generate_comprehensive_report(progression, initial_data)
    saved_files = save_report(report_data, initial_data['name'], 'both')

    if 'markdown' in saved_files:
        print(f"Markdown report available at: {saved_files['markdown']}")
    if 'pdf' in saved_files:
        print(f"PDF report available at: {saved_files['pdf']}")
    if 'pdf_error' in saved_files:
        print(f"Failed to generate PDF report: {saved_files['pdf_error']}")

    return saved_files

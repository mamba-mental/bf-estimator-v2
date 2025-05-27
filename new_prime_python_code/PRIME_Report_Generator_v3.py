import os
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from .PRIME_Utils import calculate_age, DIET_MULTIPLIERS, EXERCISE_ADJUSTMENTS
from .PRIME_Calculations import calculate_lean_mass_preservation_scores
import numpy as np
import base64
from io import BytesIO
from jinja2 import Template

# Set matplotlib backend for headless environments
import matplotlib
matplotlib.use('Agg')

def create_professional_charts(progression_data, output_dir):
    """
    Create professional charts for the report with proper styling.
    
    Args:
        progression_data (list): Weekly progression data
        output_dir (str): Directory to save charts
        
    Returns:
        dict: Base64 encoded chart data for embedding in HTML
    """
    os.makedirs(output_dir, exist_ok=True)
    chart_data = {}
    
    # Set professional style
    plt.style.use('default')
    sns.set_palette("Set2")
    
    # Extract data for plotting
    dates = [datetime.datetime.strptime(d['date'], "%m%d%y") for d in progression_data]
    weights = [d['weight'] for d in progression_data]
    body_fat_pcts = [d['body_fat_percentage'] for d in progression_data]
    lean_mass = [d['lean_mass'] for d in progression_data]
    fat_mass = [d['fat_mass'] for d in progression_data]
    
    # 1. Weight Progress Chart
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(dates, weights, linewidth=3, marker='o', markersize=8, color='#2E86AB', label='Weight')
    ax.set_title('Predicted Weight Changes', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Weight (lbs)', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.tick_params(axis='x', rotation=45)
    
    # Format dates on x-axis
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    
    plt.tight_layout()
    
    # Save to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    chart_data['weight_progress_chart'] = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    # 2. Body Composition Chart (Combined)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(dates, body_fat_pcts, linewidth=3, marker='s', markersize=8, color='#A23B72', label='Body Fat %')
    ax2 = ax.twinx()
    ax2.plot(dates, lean_mass, linewidth=3, marker='o', markersize=8, color='#F18F01', label='Lean Mass')
    ax2.plot(dates, fat_mass, linewidth=3, marker='^', markersize=8, color='#C73E1D', label='Fat Mass')
    
    ax.set_title('Predicted Body Fat and Composition Changes', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Body Fat %', fontsize=12, color='#A23B72')
    ax2.set_ylabel('Mass (lbs)', fontsize=12, color='#F18F01')
    
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.tick_params(axis='x', rotation=45)
    ax.tick_params(axis='y', labelcolor='#A23B72')
    ax2.tick_params(axis='y', labelcolor='#F18F01')
    
    # Format dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    
    # Combine legends
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.tight_layout()
    
    # Save to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    chart_data['body_composition_chart'] = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return chart_data

def get_body_fat_category(bf_percentage):
    """Get body fat category and description."""
    if bf_percentage >= 30:
        return "Obese", "Significant excess fat all around", "12+ months"
    elif bf_percentage >= 25:
        return "High Body Fat", "Excess fat all around, round physique", "6-12 months"
    elif bf_percentage >= 20:
        return "Above Average", "No visible abs, excess fat", "4-6 months"
    elif bf_percentage >= 15:
        return "Average", "Little muscle definition, soft look", "3-4 months"
    elif bf_percentage >= 12:
        return "Fit", "Some muscle definition, minimal fat", "2-3 months"
    elif bf_percentage >= 10:
        return "Athletic", "Good muscle definition, low fat", "1-2 months"
    else:
        return "Very Lean", "Excellent definition, very low fat", "Already there"

def get_score_description(score):
    """Get description for workout scores."""
    if score < 0.4:
        return "Low"
    elif score < 0.7:
        return "Moderate"
    else:
        return "High"

def calculate_workout_scores(workout_days, workout_type, experience_level):
    """Calculate detailed workout analysis scores."""
    volume_score, intensity_score, frequency_score = calculate_lean_mass_preservation_scores(workout_days, workout_type)
    
    # Enhanced scoring based on experience
    experience_multipliers = {
        'Beginner': 0.8,
        'Novice': 0.9,
        'Intermediate': 1.0,
        'Advanced': 1.1,
        'Elite': 1.2
    }
    
    multiplier = experience_multipliers.get(experience_level.split()[0], 1.0)
    volume_score *= multiplier
    intensity_score *= multiplier
    
    return volume_score, intensity_score, frequency_score

def generate_prime_report_terminal(user_data, progression_data, output_dir="results"):
    """
    Generate a comprehensive PRIME report using the professional HTML template.
    
    Args:
        user_data (dict): User profile data
        progression_data (list): Weekly progression predictions
        output_dir (str): Output directory for files
        
    Returns:
        tuple: (markdown_path, pdf_path) if successful, (markdown_path, None) if PDF fails
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate professional charts
    chart_data = create_professional_charts(progression_data, output_dir)
    
    # Calculate comprehensive metrics
    initial_data = progression_data[0]
    final_data = progression_data[-1]
    
    # Extract user data with defaults
    name = user_data.get('name', 'User')
    height_ft = user_data.get('height_feet', 5)
    height_in = user_data.get('height_inches', 9)
    height_cm = user_data.get('height_cm', 175.26)
    current_weight = initial_data['weight']
    current_bf = initial_data['body_fat_percentage']
    goal_weight = user_data.get('goal_weight', final_data['weight'])
    goal_bf = user_data.get('goal_bf', final_data['body_fat_percentage'])
    age = user_data.get('age', 30)
    gender = user_data.get('gender', 'Male')
    activity_level = user_data.get('activity_level_description', 'Light exercise/sports 1-3 days/week')
    experience_level = user_data.get('experience_level', 'Intermediate')
    workout_type = user_data.get('workout_type', 'Bodybuilding')
    workout_days = user_data.get('workout_days', 4)
    is_athlete = user_data.get('is_athlete', True)
    resistance_training = user_data.get('resistance_training', True)
    
    # Calculate timeline
    start_date = datetime.datetime.now().strftime("%m/%d/%y")
    end_date = (datetime.datetime.now() + datetime.timedelta(weeks=len(progression_data)-1)).strftime("%m/%d/%y")
    total_weeks = len(progression_data) - 1
    
    # Calculate workout scores
    volume_score, intensity_score, frequency_score = calculate_workout_scores(workout_days, workout_type, experience_level)
    
    # Calculate metabolic adaptation
    initial_rmr = initial_data['rmr']
    final_rmr = final_data['rmr']
    metabolic_adaptation = (final_rmr / initial_rmr) if initial_rmr > 0 else 1.0
    
    # Calculate results summary
    total_weight_loss = current_weight - final_data['weight']
    fat_loss_percentage = current_bf - final_data['body_fat_percentage']
    muscle_gain = final_data['lean_mass'] - initial_data['lean_mass']
    avg_weekly_weight_loss = total_weight_loss / total_weeks if total_weeks > 0 else 0
    avg_weekly_muscle_gain = muscle_gain / total_weeks if total_weeks > 0 else 0
    
    # Prepare weekly progress data
    weekly_progress = []
    for data in progression_data:
        weekly_progress.append({
            'date': datetime.datetime.strptime(data['date'], "%m%d%y").strftime("%m/%d/%y"),
            'weight': data['weight'],
            'body_fat_percentage': data['body_fat_percentage'],
            'daily_calorie_intake': data['daily_calorie_intake'],
            'tdee': data['tdee'],
            'weekly_caloric_output': data['weekly_caloric_output'],
            'total_weight_lost': data['total_weight_lost'],
            'lean_mass': data['lean_mass'],
            'fat_mass': data['fat_mass'],
            'muscle_gain': data['muscle_gain'],
            'rmr': data['rmr']
        })
    
    # Prepare body composition changes
    body_composition_changes = []
    for data in progression_data:
        category, description, six_pack_time = get_body_fat_category(data['body_fat_percentage'])
        body_composition_changes.append({
            'category': category,
            'body_fat_percentage': data['body_fat_percentage'],
            'date_reached': datetime.datetime.strptime(data['date'], "%m%d%y").strftime("%m/%d/%y"),
            'description': description,
            'time_to_six_pack': six_pack_time
        })
    
    # Read the HTML template
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'report_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Create Jinja2 template
    template = Template(template_content)
    
    # Prepare template variables
    template_vars = {
        'name': name,
        'report_date': datetime.datetime.now().strftime("%m/%d/%Y"),
        'height': f"{height_ft}'{height_in}\" ({height_cm:.2f} cm)",
        'initial_weight': current_weight,
        'initial_body_fat': current_bf,
        'initial_lean_mass': initial_data['lean_mass'],
        'initial_fat_mass': initial_data['fat_mass'],
        'age': age,
        'gender': gender,
        'goal_weight': goal_weight,
        'goal_body_fat': goal_bf,
        'start_date': start_date,
        'end_date': end_date,
        'total_weeks': total_weeks,
        'activity_level': activity_level,
        'experience_level': experience_level,
        'workout_type': workout_type,
        'workout_frequency': workout_days,
        'resistance_training': 'Yes' if resistance_training else 'No',
        'athlete_status': 'Yes' if is_athlete else 'No',
        'initial_rmr': initial_data['rmr'],
        'initial_tdee': initial_data['tdee'],
        'tef': initial_data.get('tef', 330),
        'neat': initial_data.get('neat', 150),
        'initial_daily_calorie_intake': initial_data['daily_calorie_intake'],
        'volume_score': volume_score,
        'intensity_score': intensity_score,
        'frequency_score': frequency_score,
        'weight_progress_chart': chart_data['weight_progress_chart'],
        'body_composition_chart': chart_data['body_composition_chart'],
        'weekly_progress': weekly_progress,
        'body_composition_changes': body_composition_changes,
        'total_weight_loss': total_weight_loss,
        'total_bf_loss': fat_loss_percentage,
        'total_muscle_gain': muscle_gain,
        'avg_weekly_loss': avg_weekly_weight_loss,
        'avg_muscle_gain': avg_weekly_muscle_gain,
        'week_1_adaptation': 1.0,
        'final_week_adaptation': metabolic_adaptation,
        'adaptation_percentage': (1 - metabolic_adaptation) * 100,
        'lean_mass_preserved': (final_data['lean_mass'] / initial_data['lean_mass'] * 100),
        'final_tdee': final_data['tdee'],
        'final_weekly_caloric_output': final_data['weekly_caloric_output'],
        'get_score_description': get_score_description
    }
    
    # Render HTML
    html_content = template.render(**template_vars)
    
    # Read CSS file
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles', 'report_style.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # Embed CSS in HTML
    html_content = html_content.replace('<link rel="stylesheet" href="styles/report_style.css">', 
                                       f'<style>{css_content}</style>')
    
    # Generate file names
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    html_filename = f"{name.replace(' ', '_')}_Prime_{timestamp}.html"
    pdf_filename = f"{name.replace(' ', '_')}_Prime_{timestamp}.pdf"
    markdown_filename = f"{name.replace(' ', '_')}_Prime_{timestamp}.md"
    
    html_path = os.path.join(output_dir, html_filename)
    pdf_path = os.path.join(output_dir, pdf_filename)
    markdown_path = os.path.join(output_dir, markdown_filename)
    
    # Save HTML file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Generate PDF from HTML
    pdf_generated = False
    try:
        from weasyprint import HTML, CSS
        
        # Create WeasyPrint HTML object
        html_doc = HTML(string=html_content, base_url=os.path.dirname(html_path))
        
        # Generate PDF
        html_doc.write_pdf(pdf_path)
        pdf_generated = True
        print(f"✅ Professional PDF report generated: {pdf_path}")
        
    except ImportError:
        print("⚠️  WeasyPrint not available, PDF generation skipped")
    except Exception as e:
        print(f"⚠️  PDF generation failed: {e}")
    
    # Also generate a markdown version for compatibility
    markdown_content = f"""# Body Fat and Weight Loss Calculator Report - {name} Prime

**Report Date:** {datetime.datetime.now().strftime("%m/%d/%Y")}

## Summary
- **Total Weight Loss:** {total_weight_loss:.2f} lbs
- **Body Fat Reduction:** {fat_loss_percentage:.2f}%
- **Muscle Gain:** {muscle_gain:.2f} lbs
- **Timeline:** {total_weeks} weeks

## Files Generated
- **HTML Report:** {html_filename}
- **PDF Report:** {pdf_filename if pdf_generated else 'Failed to generate'}

*This is a summary. Please view the HTML or PDF report for complete details.*
"""
    
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"📄 Professional HTML Report: {html_path}")
    print(f"📋 Summary Markdown: {markdown_path}")
    
    return markdown_path, pdf_path if pdf_generated else None
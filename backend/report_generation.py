# report_generation.py
import os
import datetime
import json
import logging
import glob
import matplotlib
from pathlib import Path
matplotlib.use('Agg')  # Set the backend to Agg before importing pyplot
import matplotlib.pyplot as plt
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from docx import Document
from docx.shared import Inches, Pt

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
MAX_FILES_PER_TYPE = 50  # Maximum number of files to keep per file type
FILE_RETENTION_DAYS = 7  # Number of days to keep files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FOLDER = os.path.join(SCRIPT_DIR, "results")
TEMPLATE_FOLDER = os.path.join(SCRIPT_DIR, "templates")
CSS_FILE = os.path.join(SCRIPT_DIR, "styles", "report_style.css")

# Ensure required directories exist
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def sanitize_text(text):
    """Sanitize text for PDF output by replacing problematic characters."""
    replacements = {
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '•': '-',
        '–': '-',
        '—': '-',
        '…': '...',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def generate_comprehensive_report(progression_data, initial_data):
    """Generate a comprehensive report from progression and initial data."""
    try:
        # Calculate initial and final stats
        initial_weight = initial_data['current_weight']
        final_weight = progression_data[-1]['weight']
        initial_bf = initial_data['current_bf']
        final_bf = progression_data[-1]['body_fat_percentage']
        initial_lbm = initial_weight * (1 - initial_bf/100)
        final_lbm = final_weight * (1 - final_bf/100)

        # Generate charts and convert paths to file:// URIs
        weight_progress_chart_path = generate_weight_progress_chart(progression_data)
        body_composition_chart_path = generate_body_composition_chart(progression_data)
        
        # Convert paths to file:// URIs
        weight_progress_chart_uri = f"file:///{os.path.abspath(weight_progress_chart_path).replace(os.sep, '/')}"
        body_composition_chart_uri = f"file:///{os.path.abspath(body_composition_chart_path).replace(os.sep, '/')}"
        
        body_composition_changes = []

        # Calculate total weight loss
        total_weight_loss = initial_weight - final_weight
        report_data = {
            'initial_weight': initial_weight,
            'final_weight': final_weight,
            'total_weight_loss': total_weight_loss,
            'initial_body_fat': initial_bf,
            'final_body_fat': final_bf,
            'total_bf_loss': initial_bf - final_bf,
            'total_muscle_gain': final_lbm - initial_lbm,
            'initial_body_fat_category': get_body_fat_category(initial_bf),
            'initial_body_fat_description': get_body_fat_description(initial_bf),
            'initial_time_to_six_pack': calculate_time_to_six_pack(initial_bf),
            'final_body_fat_category': get_body_fat_category(final_bf),
            'final_body_fat_description': get_body_fat_description(final_bf),
            'final_time_to_six_pack': calculate_time_to_six_pack(final_bf),
            'adaptation_percentage': calculate_adaptation_percentage(progression_data),
            'lean_mass_preserved': calculate_lean_mass_preserved(progression_data),
            'avg_muscle_gain': calculate_avg_muscle_gain(progression_data),
            'final_tdee': calculate_final_tdee(progression_data[-1]),
            'next_steps': generate_next_steps(progression_data[-1]),
            'volume_score': initial_data.get('volume_score', 0),
            'intensity_score': initial_data.get('intensity_score', 0),
            'frequency_score': initial_data.get('frequency_score', 0),
            'week_1_adaptation': round(progression_data[0]['tdee'] / progression_data[0]['rmr'], 2) if progression_data else 1.0,
            'final_week_adaptation': round(progression_data[-1]['tdee'] / progression_data[-1]['rmr'], 2) if progression_data else 1.0,
            'initial_rmr': round(progression_data[0]['rmr'], 2) if progression_data else 0.0,
            'initial_tdee': round(progression_data[0]['tdee'], 2) if progression_data else 0.0,
            'tef': round(progression_data[0]['tdee'] * 0.1, 2) if progression_data else 0.0,
            'neat': round(progression_data[0]['tdee'] * 0.15, 2) if progression_data else 0.0,
            'initial_daily_calorie_intake': progression_data[0]['daily_calorie_intake'] if progression_data else 0.0,
            'workout_frequency': initial_data['workout_days'],
            'workout_type': initial_data['workout_type'],
            'resistance_training': 'Yes' if initial_data['resistance_training'] else 'No',
            'athlete_status': 'Yes' if initial_data['is_athlete'] else 'No',
            'initial_lean_mass': progression_data[0]['lean_mass'] if progression_data else 0.0,
            'initial_fat_mass': progression_data[0]['weight'] * (progression_data[0]['body_fat_percentage'] / 100) if progression_data else 0.0,
            'weekly_muscle_gain': calculate_avg_muscle_gain(progression_data),
            'total_weeks': len(progression_data),
            'avg_weekly_loss': (initial_weight - final_weight) / len(progression_data) if progression_data else 0.0,
            'final_daily_calorie_intake': progression_data[-1]['daily_calorie_intake'] if progression_data else 0.0,
            'final_weekly_caloric_output': progression_data[-1]['weekly_caloric_output'] if progression_data else 0.0,
            'weekly_progress': progression_data,
            'report_date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'name': initial_data['name'],
            'start_date': initial_data['start_date'].strftime('%Y-%m-%d'),
            'end_date': initial_data['end_date'].strftime('%Y-%m-%d'),
            'age': int((datetime.datetime.now() - initial_data['dob']).days / 365.25),
            'gender': 'Male' if initial_data['gender'].lower() == 'm' else 'Female',
            'height': f"{initial_data['height_feet']}'{initial_data['height_inches']}\"",
            'activity_level': initial_data['activity_level_description'],
            'experience_level': initial_data['experience_level'],
            'weight_progress_chart_path': weight_progress_chart_uri,
            'body_composition_chart_path': body_composition_chart_uri,
            'body_composition_changes': body_composition_changes,
            'goal_weight': initial_data['goal_weight'],
            'goal_body_fat': initial_data['goal_bf'],
            'height_feet': initial_data['height_feet'],
            'height_inches': initial_data['height_inches']
        }

        # Skip generating different format contents for initial response
        report_data['markdown_content'] = ""
        report_data['pdf_content'] = b''

        return report_data
    except Exception as e:
        logger.error(f"Error generating comprehensive report: {e}")
        raise

def cleanup_old_files():
    """Clean up old files from the results directory."""
    try:
        current_time = datetime.datetime.now()
        cutoff_time = current_time - datetime.timedelta(days=FILE_RETENTION_DAYS)
        
        # Get all files in results directory
        for file_path in Path(RESULTS_FOLDER).glob('*'):
            # Skip if directory
            if file_path.is_dir():
                continue
                
            # Get file modification time
            mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
            
            # Remove if older than retention period
            if mtime < cutoff_time:
                try:
                    file_path.unlink()
                    logger.info(f"Removed old file: {file_path}")
                except Exception as e:
                    logger.error(f"Error removing file {file_path}: {e}")
                    
        # Enforce max files per type limit
        for extension in ['.png', '.json', '.md', '.pdf', '.docx']:
            files = sorted(
                Path(RESULTS_FOLDER).glob(f'*{extension}'),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Remove excess files
            for file_path in files[MAX_FILES_PER_TYPE:]:
                try:
                    file_path.unlink()
                    logger.info(f"Removed excess file: {file_path}")
                except Exception as e:
                    logger.error(f"Error removing excess file {file_path}: {e}")
                    
    except Exception as e:
        logger.error(f"Error during file cleanup: {e}")

def generate_weight_progress_chart(progression_data):
    """Generate a weight progress chart and save it as an image file."""
    fig = None
    try:
        fig = plt.figure(figsize=(10, 6))
        weeks = list(range(len(progression_data)))
        weights = [week['weight'] for week in progression_data]
        plt.plot(weeks, weights, marker='o')
        plt.title('Weight Progress Over Time')
        plt.xlabel('Week')
        plt.ylabel('Weight (lbs)')
        plt.grid(True)

        # Save to file
        chart_filename = f"weight_progress_chart_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        chart_path = os.path.join(RESULTS_FOLDER, chart_filename)
        plt.savefig(chart_path, format='png', dpi=300, bbox_inches='tight')
        return chart_path
    except Exception as e:
        logger.error(f"Error generating weight progress chart: {e}")
        return ""
    finally:
        if fig is not None:
            plt.close(fig)

def generate_body_composition_chart(progression_data):
    """Generate a body composition chart and save it as an image file."""
    fig = None
    try:
        fig = plt.figure(figsize=(10, 6))
        weeks = list(range(len(progression_data)))
        bf_percentages = [week['body_fat_percentage'] for week in progression_data]
        plt.plot(weeks, bf_percentages, marker='o', color='red')
        plt.title('Body Fat Percentage Over Time')
        plt.xlabel('Week')
        plt.ylabel('Body Fat %')
        plt.grid(True)

        # Save to file
        chart_filename = f"body_composition_chart_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        chart_path = os.path.join(RESULTS_FOLDER, chart_filename)
        plt.savefig(chart_path, format='png', dpi=300, bbox_inches='tight')
        return chart_path
    except Exception as e:
        logger.error(f"Error generating body composition chart: {e}")
        return ""
    finally:
        if fig is not None:
            plt.close(fig)

def get_body_fat_category(bf_percentage):
    """Get the category for a given body fat percentage."""
    if bf_percentage < 6:
        return "Essential Fat"
    elif bf_percentage < 13:
        return "Athletic"
    elif bf_percentage < 17:
        return "Fitness"
    elif bf_percentage < 25:
        return "Average"
    else:
        return "Above Average"

def get_body_fat_description(bf_percentage):
    """Get the description for a given body fat percentage."""
    descriptions = {
        "Essential Fat": "Minimal essential fat necessary for basic bodily functions.",
        "Athletic": "Visible muscle definition and vascularity.",
        "Fitness": "Good muscle definition with some vascularity.",
        "Average": "Some muscle definition with higher fat storage.",
        "Above Average": "Limited muscle definition with significant fat storage."
    }
    return descriptions[get_body_fat_category(bf_percentage)]

def get_score_description(score):
    """Get description for a given score."""
    if score >= 0.8:
        return "Excellent"
    elif score >= 0.6:
        return "Good"
    elif score >= 0.4:
        return "Average"
    else:
        return "Needs Improvement"

def calculate_time_to_six_pack(bf_percentage):
    """Calculate estimated time to reach six-pack abs (around 10% body fat)."""
    if bf_percentage <= 10:
        return "Already achieved"

    # Assume safe fat loss of 1% body fat per month
    months_needed = (bf_percentage - 10)
    if months_needed <= 1:
        return "About 1 month"
    else:
        return f"Approximately {round(months_needed)} months"

def calculate_adaptation_percentage(progression_data):
    """Calculate metabolic adaptation percentage."""
    if len(progression_data) < 2:
        return 0
    initial_tdee = progression_data[0]['tdee']
    final_tdee = progression_data[-1]['tdee']
    return round(((final_tdee - initial_tdee) / initial_tdee) * 100, 1)

def calculate_lean_mass_preserved(progression_data):
    """Calculate percentage of lean mass preserved."""
    if len(progression_data) < 2:
        return 100
    initial_lbm = progression_data[0]['lean_mass']
    final_lbm = progression_data[-1]['lean_mass']
    return round((final_lbm / initial_lbm) * 100, 1)

def calculate_avg_muscle_gain(progression_data):
    """Calculate average muscle gain per week."""
    if len(progression_data) < 2:
        return 0
    total_weeks = len(progression_data)
    total_gain = progression_data[-1]['lean_mass'] - progression_data[0]['lean_mass']
    return round(total_gain / total_weeks, 2)

def calculate_final_tdee(final_data):
    """Calculate final TDEE."""
    return round(final_data['tdee'])

def generate_next_steps(final_data):
    """Generate next steps based on final data."""
    bf_category = get_body_fat_category(final_data['body_fat_percentage'])
    if bf_category in ["Essential Fat", "Athletic"]:
        return ["Focus on maintaining current body composition", "Consider a lean bulk phase"]
    elif bf_category == "Fitness":
        return ["Continue with current plan", "Consider slight caloric deficit for further definition"]
    else:
        return ["Continue with caloric deficit", "Increase protein intake", "Add resistance training"]

def generate_pdf_report(report_data):
    """Generate a PDF report using WeasyPrint."""
    try:
        env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))
        template = env.get_template('report_template.html')

        # Create a copy of report_data to avoid modifying the original
        template_data = report_data.copy()

        # Add score descriptions
        template_data['volume_score_description'] = get_score_description(template_data.get('volume_score', 0))
        template_data['intensity_score_description'] = get_score_description(template_data.get('intensity_score', 0))
        template_data['frequency_score_description'] = get_score_description(template_data.get('frequency_score', 0))

        # Add default values for numeric fields
        numeric_fields = [
            'week_1_adaptation', 'final_week_adaptation', 'initial_weight', 'final_weight',
            'total_weight_loss', 'initial_body_fat', 'final_body_fat', 'total_bf_loss',
            'total_muscle_gain', 'adaptation_percentage', 'lean_mass_preserved',
            'avg_muscle_gain', 'avg_weekly_loss', 'final_tdee', 'final_daily_calorie_intake',
            'final_weekly_caloric_output', 'initial_rmr', 'initial_tdee', 'tef', 'neat',
            'initial_daily_calorie_intake', 'initial_lean_mass', 'initial_fat_mass',
            'weekly_muscle_gain'
        ]
        for field in numeric_fields:
            template_data[field] = template_data.get(field, 0.0)

        # Generate HTML content
        html_content = template.render(report=template_data)

        # Fix chart paths for PDF generation
        for chart in ['weight_progress_chart_path', 'body_composition_chart_path']:
            if chart in template_data:
                path = template_data[chart].replace('file:///', '')
                abs_path = os.path.abspath(path)
                if os.path.exists(abs_path):
                    template_data[chart] = abs_path
                else:
                    logger.error(f"Chart file not found: {abs_path}")

        # Generate PDF with WeasyPrint
        logger.info("Generating PDF...")
        try:
            # Create HTML document with base URL for resolving relative paths
            html = HTML(string=html_content)
            # Write PDF directly to bytes
            pdf_bytes = html.write_pdf()
            logger.info(f"PDF generated successfully, size: {len(pdf_bytes)} bytes")
            return pdf_bytes
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return b''

    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        return b''

def generate_markdown_report(report_data):
    """Generate a markdown format report."""
    try:
        md_content = f"""# Your Personalized Weight Loss Journey Report

Generated on: {report_data['report_date']}

## 1. Personal Profile

- Start Date: {report_data['start_date']}
- End Date: {report_data['end_date']}
- Age: {report_data['age']} years
- Gender: {report_data['gender']}
- Height: {report_data['height']}
- Initial Weight: {report_data['initial_weight']:.1f} lbs
- Goal Weight: {report_data['goal_weight']:.1f} lbs
- Initial Body Fat: {report_data['initial_body_fat']:.1f}%
- Goal Body Fat: {report_data['goal_body_fat']:.1f}%
- Activity Level: {report_data['activity_level']}
- Experience Level: {report_data['experience_level']}

## 2. Metabolic Calculations

- Initial RMR: {report_data['initial_rmr']:.2f} cal/day
- Initial TDEE: {report_data['initial_tdee']:.2f} cal/day
- TEF: {report_data['tef']:.1f} cal/day
- NEAT: {report_data['neat']:.1f} cal/day
- Initial Daily Calorie Intake: {report_data['initial_daily_calorie_intake']:.2f} cal/day

## 3. Workout Analysis

- Type: {report_data['workout_type']}
- Frequency: {report_data['workout_frequency']}
- Volume Score: {report_data['volume_score']}
- Intensity Score: {report_data['intensity_score']}
- Frequency Score: {report_data['frequency_score']}
- Resistance Training: {report_data['resistance_training']}
- Athlete Status: {report_data['athlete_status']}

## 4. Body Composition Adjustments

- Initial Lean Mass: {report_data['initial_lean_mass']:.2f} lbs
- Initial Fat Mass: {report_data['initial_fat_mass']:.2f} lbs
- Est. Weekly Muscle Gain: {report_data['weekly_muscle_gain']:.2f} lbs

## 5. Weekly Progress Forecast

(Chart not available in Markdown format)

## 6. Body Composition Changes Over Time

(Chart not available in Markdown format)

## 7. Metabolic Adaptation

- Week 1 Metabolic Adaptation: {report_data['week_1_adaptation']:.2f}
- Final Week Metabolic Adaptation: {report_data['final_week_adaptation']:.2f}

## 8. Final Results

- Duration: {report_data['total_weeks']} weeks
- Total Weight Loss: {report_data['total_weight_loss']:.2f} lbs
- Total Body Fat Reduction: {report_data['total_bf_loss']:.2f}%
- Final Weight: {report_data['final_weight']:.2f} lbs
- Final Body Fat: {report_data['final_body_fat']:.2f}%
- Average Weekly Weight Loss: {report_data['avg_weekly_loss']:.2f} lbs
- Total Muscle Gain: {report_data['total_muscle_gain']:.2f} lbs
- Final Daily Calorie Intake: {report_data['final_daily_calorie_intake']:.2f} calories
- Final TDEE: {report_data['final_tdee']:.2f} calories
- Final Weekly Caloric Output: {report_data['final_weekly_caloric_output']:.2f} calories

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
- Your muscle gain rate averaged {report_data['avg_muscle_gain']:.2f} lbs per week.
- Based on your final body fat percentage, you're now in the {report_data['final_body_fat_category']} category.
- To maintain your results, consider a daily calorie intake of {report_data['final_tdee']:.2f} calories.

## 11. Next Steps

"""
        # Add next steps as bullet points
        for step in report_data['next_steps']:
            md_content += f"- {step}\n"

        return md_content
    except Exception as e:
        logger.error(f"Error generating markdown report: {e}")
        return ""

def save_report(report_data, username, save_format):
    """Save the report in the specified format(s)."""
    try:
        # Clean up old files before saving new ones
        cleanup_old_files()
        saved_files = {}
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{username.replace(' ', '_')}_{timestamp}"

        # Save JSON
        json_filename = os.path.join(RESULTS_FOLDER, f"{base_filename}.json")
        json_data = {
            'initial_weight': report_data['initial_weight'],
            'final_weight': report_data['final_weight'],
            'total_weight_loss': report_data['total_weight_loss'],
            'initial_body_fat': report_data['initial_body_fat'],
            'final_body_fat': report_data['final_body_fat'],
            'total_bf_loss': report_data['total_bf_loss'],
            'total_muscle_gain': report_data['total_muscle_gain'],
            'weekly_progress': report_data['weekly_progress']
        }
        with open(json_filename, 'w') as f:
            json.dump(json_data, f, indent=4)
        saved_files['json'] = json_filename

        # Save Markdown
        if save_format == 'md':
            md_content = generate_markdown_report(report_data)
            md_filename = os.path.join(RESULTS_FOLDER, f"{base_filename}.md")
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(md_content)
            saved_files['md'] = md_filename

        # Save PDF
        elif save_format == 'pdf':
            pdf_content = generate_pdf_report(report_data)
            if pdf_content:
                pdf_filename = os.path.join(RESULTS_FOLDER, f"{base_filename}.pdf")
                with open(pdf_filename, 'wb') as f:
                    f.write(pdf_content)
                saved_files['pdf'] = pdf_filename

        # Save DOCX
        elif save_format == 'docx':
            docx_content = generate_docx_report(report_data)
            if docx_content:
                docx_filename = os.path.join(RESULTS_FOLDER, f"{base_filename}.docx")
                with open(docx_filename, 'wb') as f:
                    f.write(docx_content)
                saved_files['docx'] = docx_filename

        return saved_files
    except Exception as e:
        logger.error(f"Error saving report: {e}")
        return None

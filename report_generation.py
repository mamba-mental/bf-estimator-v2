# report_generation.py
from tabulate import tabulate
from calculations import calculate_metabolic_adaptation
from utils import calculate_age, estimate_tef, estimate_neat
import datetime
import os
import markdown
import pdfkit

# Define the correct path for the results folder
RESULTS_FOLDER = r"C:\Code_Projects\bf-estimator-v2\results"

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

def generate_comprehensive_report(progression, initial_data):
    initial_entry = progression[0]
    final_entry = progression[-1]
    total_weeks = len(progression) - 1

    total_weight_loss = initial_entry['weight'] - final_entry['weight']
    total_bf_loss = initial_entry['body_fat_percentage'] - final_entry['body_fat_percentage']
    avg_weekly_loss = total_weight_loss / total_weeks
    total_muscle_gain = sum(entry['muscle_gain'] for entry in progression)
    adaptation_percentage = (1 - final_entry['tdee'] / initial_entry['tdee']) * 100
    lean_mass_preserved = (final_entry['lean_mass'] / initial_entry['lean_mass']) * 100
    avg_muscle_gain = total_muscle_gain / total_weeks

    body_composition_changes = ""
    for entry in progression:
        category, time_to_six_pack, description = get_body_fat_info(initial_data['gender'], entry['body_fat_percentage'])
        entry_date = datetime.datetime.strptime(entry['date'], "%m%d%y").strftime("%m/%d/%Y")
        body_composition_changes += f"| {category:<18} | {entry['body_fat_percentage']:.1f}% | {entry_date} | {description:<40} | {time_to_six_pack:<12} |\n"

    start_date = datetime.datetime.strptime(initial_entry['date'], "%m%d%y").strftime("%m/%d/%Y")
    end_date = datetime.datetime.strptime(final_entry['date'], "%m%d%y").strftime("%m/%d/%Y")

    # Use a default name if 'name' is not provided in initial_data
    user_name = initial_data.get('name', 'User')

    report = f"""
# Your Personalized Weight Loss Journey Report

Dear {user_name},

We've analyzed your data using our advanced weight loss prediction model. Here's a comprehensive breakdown of your journey:

## 1. Personal Profile

- Start Date: {start_date}  
- End Date: {end_date}
- Age: {calculate_age(initial_data['dob'], datetime.datetime.strptime(initial_entry['date'], "%m%d%y"))} years
- Gender: {'Male' if initial_data['gender'].lower() == 'm' else 'Female'}
- Height: {initial_data['height_feet']}'{"" if initial_data['height_inches'] == 0 else initial_data['height_inches']}" ({initial_data['height_cm']:.1f} cm)
- Initial Weight: {initial_entry['weight']:.1f} lbs 
- Goal Weight: {initial_data['goal_weight']:.1f} lbs
- Initial Body Fat: {initial_entry['body_fat_percentage']:.1f}%
- Goal Body Fat: {initial_data['goal_bf']:.1f}%  
- Activity Level: {initial_data['activity_level_description']}
- Experience Level: {initial_data['experience_level']} 

## 2. Metabolic Calculations

- Initial Resting Metabolic Rate (RMR): {initial_entry['rmr']:.0f} calories/day
- Initial Total Daily Energy Expenditure (TDEE): {initial_entry['tdee']:.0f} calories/day
- Thermic Effect of Food (TEF): {estimate_tef(initial_data['protein_intake']):.0f} calories/day
- Non-Exercise Activity Thermogenesis (NEAT): {estimate_neat(initial_data['job_activity'], initial_data['leisure_activity']):.0f} calories/day
- Initial Daily Calorie Intake: {initial_entry['daily_calorie_intake']:.0f} calories/day

## 3. Workout Analysis

- Workout Type: {initial_data['workout_type']}
- Workout Frequency: {initial_data['workout_days']} days/week
- Volume Score: {initial_data['volume_score']:.2f}
  - 0.57 - Moderate volume, in the 40-60th percentile
  - 0.00 to 0.20 - Very low
  - 0.21 to 0.40 - Low  
  - 0.41 to 0.60 - Moderate
  - 0.61 to 0.80 - High
  - 0.81 to 1.00 - Very high
- Intensity Score: {initial_data['intensity_score']:.2f}
  - 0.80 - High intensity, working close to failure
  - 0.00 to 0.20 - Very low 
  - 0.21 to 0.40 - Low
  - 0.41 to 0.60 - Moderate
  - 0.61 to 0.80 - High
  - 0.81 to 1.00 - Very high  
- Frequency Score: {initial_data['frequency_score']:.2f}
  - 1.00 - Optimal frequency, training each muscle 2-3x per week
  - 0.00 to 0.20 - Very low
  - 0.21 to 0.40 - Low
  - 0.41 to 0.60 - Moderate
  - 0.61 to 0.80 - High 
  - 0.81 to 1.00 - Optimal
- Resistance Training: {'Yes' if initial_data['resistance_training'] else 'No'}
- Athlete Status: {'Yes' if initial_data['is_athlete'] else 'No'}

## 4. Body Composition Adjustments

- Initial Lean Mass: {initial_entry['lean_mass']:.1f} lbs
- Initial Fat Mass: {initial_entry['fat_mass']:.1f} lbs  
- Estimated Weekly Muscle Gain: {avg_muscle_gain:.3f} lbs

## 5. Weekly Progress Forecast

{tabulate(progression, headers="keys", tablefmt="pipe")}

## 6. Body Composition Changes Over Time

| Body Fat Category | Body Fat % | Date Reached | Description | Est. Time to Six-Pack |
|-------------------|------------|--------------|-------------|----------------------|
{body_composition_changes}

## 7. Metabolic Adaptation

- Week 1 Metabolic Adaptation: {calculate_metabolic_adaptation(1, initial_entry['body_fat_percentage'], initial_data['is_bodybuilder']):.2f}
- Final Week Metabolic Adaptation: {calculate_metabolic_adaptation(total_weeks, final_entry['body_fat_percentage'], initial_data['is_bodybuilder']):.2f}

## 8. Final Results

- Duration: {total_weeks} weeks
- Total Weight Loss: {total_weight_loss:.1f} lbs
- Total Body Fat Reduction: {total_bf_loss:.1f}%
- Final Weight: {final_entry['weight']:.1f} lbs 
- Final Body Fat: {final_entry['body_fat_percentage']:.1f}%
- Average Weekly Weight Loss: {avg_weekly_loss:.2f} lbs
- Total Muscle Gain: {total_muscle_gain:.1f} lbs 
- Final Daily Calorie Intake: {final_entry['daily_calorie_intake']:.0f} calories
- Final TDEE: {final_entry['tdee']:.0f} calories
- Final Weekly Caloric Output: {final_entry['weekly_caloric_output']:.1f} calories

## 9. Body Fat Category Progression

- Initial Category: {get_body_fat_info(initial_data['gender'], initial_entry['body_fat_percentage'])[0]}
   - Description: {get_body_fat_info(initial_data['gender'], initial_entry['body_fat_percentage'])[2]} 
   - Estimated Time to Six-Pack: {get_body_fat_info(initial_data['gender'], initial_entry['body_fat_percentage'])[1]}

- Final Category: {get_body_fat_info(initial_data['gender'], final_entry['body_fat_percentage'])[0]} 
   - Description: {get_body_fat_info(initial_data['gender'], final_entry['body_fat_percentage'])[2]}
   - Estimated Time to Six-Pack: {get_body_fat_info(initial_data['gender'], final_entry['body_fat_percentage'])[1]}

## 10. Insights and Recommendations

- Your metabolic rate adapted by {adaptation_percentage:.1f}% over the course of your journey.
- You maintained an impressive {lean_mass_preserved:.1f}% of your initial lean mass.  
- Your muscle gain rate averaged {avg_muscle_gain:.3f} lbs per week, which is {'excellent' if avg_muscle_gain > 0.5 else 'good' if avg_muscle_gain > 0.25 else 'moderate'}.
- Based on your final body fat percentage, you're now in the {get_body_fat_info(initial_data['gender'], final_entry['body_fat_percentage'])[0]} category.
- To maintain your results, consider a daily calorie intake of {final_entry['tdee']:.0f} calories.

## 11. Next Steps

- {'Continue with your current plan.' if final_entry['body_fat_percentage'] > initial_data['goal_bf'] else 'Consider a muscle building phase to further improve body composition.'}
- Consider adjusting your protein intake to {final_entry['weight'] * 0.8:.0f} g/day to support lean mass.
- Your next ideal body composition goal could be {max(final_entry['body_fat_percentage'] - 2, 5):.1f}% body fat.  

Remember, this journey is a marathon, not a sprint. Celebrate your progress and stay committed to your health and fitness goals!

*Powered by Advanced AI Analytics*
"""
    return report

def save_report(report, username, save_format):
    # Create the 'results' directory if it doesn't exist
    if not os.path.exists(RESULTS_FOLDER):
        os.makedirs(RESULTS_FOLDER)

    # Generate the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{username}_{timestamp}"

    if save_format in ['markdown', 'both']:
        markdown_filename = os.path.join(RESULTS_FOLDER, f"{base_filename}.md")
        with open(markdown_filename, 'w') as f:
            f.write(report)
        print(f"Markdown report saved as {markdown_filename}")

    if save_format in ['pdf', 'both']:
        pdf_filename = os.path.join(RESULTS_FOLDER, f"{base_filename}.pdf")
        html = markdown.markdown(report)
        try:
            pdfkit.from_string(html, pdf_filename)
            print(f"PDF report saved as {pdf_filename}")
        except OSError as e:
            print(f"Error generating PDF: {str(e)}")
            print("\nTo generate PDF reports, please install wkhtmltopdf:")
            print("1. Download from: https://wkhtmltopdf.org/downloads.html")
            print("2. Install and add the installation directory to your system PATH")
            print("3. Restart your application and try again")
            print("\nAlternatively, you can use only the markdown option for now.")

def print_summary(progression, initial_data):
    report = generate_comprehensive_report(progression, initial_data)
    print(report)

    # Ask user for save preferences
    save_option = input("Do you want to save the report? (y/n): ").lower()
    if save_option == 'y':
        while True:
            save_format = input("Choose the format to save (markdown/pdf/both): ").lower()
            if save_format in ['markdown', 'pdf', 'both']:
                save_report(report, initial_data.get('name', 'User'), save_format)
                break
            else:
                print("Invalid format choice. Please enter 'markdown', 'pdf', or 'both'.")
    else:
        print("Report will not be saved.")

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
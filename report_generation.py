# report_generation.py
# --- Beginning of File ---
# report_generation.py
# Author: Tiran Ronelle Winston
# Created: 09/09/24
# Last Modified: 09/11/24
# Description: A Python script to generate personalized weight loss journey reports in Markdown and PDF formats.
# Usage: The script can be used to generate reports from provided data and save them in the desired format.
# Dependencies: os, datetime, base64, io, matplotlib.pyplot, weasyprint.HTML, weasyprint.CSS, jinja2.Environment, jinja2.FileSystemLoader, json
# Version: 1.2.7
# License: Apache License 2.0
# --- End of Header ---

[Previous content remains the same until the generate_markdown function]

def generate_markdown(report_data, weight_chart_path=None, body_comp_chart_path=None):
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

## 5. Workout Analysis

This analysis provides insight into your workout routine and its effectiveness:

- Type: {report_data['workout_type']}
- Frequency: {report_data['workout_frequency']} days/week
- Volume Score: {report_data['volume_score']:.2f} - {get_score_description(report_data['volume_score'])}
- Intensity Score: {report_data['intensity_score']:.2f} - {get_score_description(report_data['intensity_score'])}
- Frequency Score: {report_data['frequency_score']:.2f} - {get_score_description(report_data['frequency_score'])}

## 6. Predicted Progress Charts

### Weight Progress Chart
![Weight Progress Chart]({os.path.basename(weight_chart_path)})

### Body Fat Changes Chart
![Body Composition Chart]({os.path.basename(body_comp_chart_path)})

## 7. Weekly Progress Forecast

| Date | Weight (lbs) | Body Fat % | Daily Cal Intake | TDEE | Weekly Cal Output | Total Weight Lost (lbs) | Lean Mass (lbs) | Fat Mass (lbs) | Muscle Gain (lbs) | RMR |
|------|-------------|------------|------------------|------|-------------------|----------------------|----------------|---------------|-----------------|-----|
"""
    for week in report_data['weekly_progress']:
        markdown += f"| {week['date']} | {week['weight']:.2f} | {week['body_fat_percentage']:.2f} | {week['daily_calorie_intake']:.2f} | {week['tdee']:.2f} | {week['weekly_caloric_output']:.2f} | {week.get('total_weight_lost', 0):.2f} | {week['lean_mass']:.2f} | {week['fat_mass']:.2f} | {week['muscle_gain']:.2f} | {week['rmr']:.2f} |\n"

    markdown += f"""
## 8. Body Composition Changes

| Body Fat Category | Body Fat % | Date Reached | Description | Est. Time to Six-Pack |
|------------------|------------|--------------|-------------|---------------------|
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
- **Sedentary:** Little to no exercise, desk job (multiplier: 1.2)
- **Lightly Active:** Light exercise 1-3 days/week (multiplier: 1.375)
- **Moderately Active:** Moderate exercise 3-5 days/week (multiplier: 1.55)
- **Very Active:** Heavy exercise 6-7 days/week (multiplier: 1.725)
- **Extremely Active:** Very heavy exercise, physical job (multiplier: 1.9)

### Training Experience Levels:
- **Beginner (0-2 years):** Higher potential for muscle gain (0.5-1% body weight/month)
- **Intermediate (2-4 years):** Moderate gains (0.25-0.5% body weight/month)
- **Advanced (4+ years):** Slower gains (0.125-0.25% body weight/month)

### Workout Types and Their Effects:
- **Bodybuilding:** Optimized for muscle growth and aesthetics
- **Strength Training:** Focus on increasing maximal strength
- **Powerlifting:** Specialized in squat, bench press, and deadlift
- **Olympic Weightlifting:** Technical lifts for power development
- **CrossFit:** High-intensity functional movements
- **Calisthenics:** Bodyweight exercises for strength and control

### Resistance Training Impact:
- **With Resistance Training:** Higher muscle preservation (90-100%)
- **Without Resistance Training:** Lower muscle preservation (60-80%)

### Athlete Status Effects:
- **Athlete:** Higher metabolic rate, better nutrient partitioning
- **Non-Athlete:** Standard metabolic calculations apply

### Workout Analysis Metrics:
- **Volume Score:** Total work done (sets × reps × weight)
- **Intensity Score:** Average weight relative to 1RM
- **Frequency Score:** Training frequency per muscle group

### Caloric Components:
- **RMR (Resting Metabolic Rate):** Calories burned at complete rest
- **TDEE (Total Daily Energy Expenditure):** Total calories burned per day
- **TEF (Thermic Effect of Food):** Calories burned digesting food (10-15% of total intake)
- **NEAT (Non-Exercise Activity Thermogenesis):** Calories burned through daily activities

### Score Interpretations:
- **Very Low (0.0-0.2):** Significant room for improvement
- **Low (0.2-0.4):** Below optimal range
- **Moderate (0.4-0.6):** Average effectiveness
- **High (0.6-0.8):** Optimal range
- **Very High (0.8-1.0):** Maximum effectiveness

### Calculation Formulas:
- **RMR:** Based on Mifflin-St Jeor equation with adjustments for body composition
- **TDEE:** RMR × Activity Multiplier + Exercise Calories
- **Caloric Deficit:** TDEE - Daily Calorie Intake
- **Weekly Deficit:** Daily Deficit × 7
- **Fat Loss Rate:** Weekly Deficit ÷ 3500 (calories per pound of fat)
- **Muscle Gain Rate:** Based on training experience and current lean mass
- **Metabolic Adaptation:** Progressive reduction in TDEE based on deficit duration
"""
    return markdown

[Rest of the file remains the same]

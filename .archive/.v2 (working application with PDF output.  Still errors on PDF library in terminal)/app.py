from flask import Flask, render_template, request, send_file
from main import run_user_interaction, generate_comprehensive_report
from report_generation import save_report
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Process form data
        user_data = {
            'name': request.form['name'],
            'current_weight': float(request.form['current_weight']),
            'current_bf': float(request.form['current_bf']),
            'goal_weight': float(request.form['goal_weight']),
            'goal_bf': float(request.form['goal_bf']),
            'start_date': request.form['start_date'],
            'end_date': request.form['end_date'],
            'dob': request.form['dob'],
            'gender': request.form['gender'],
            'height_feet': int(request.form['height_feet']),
            'height_inches': int(request.form['height_inches']),
            'protein_intake': float(request.form['protein_intake']),
            'activity_level': int(request.form['activity_level']),
            'resistance_training': request.form['resistance_training'] == 'y',
            'is_athlete': request.form['is_athlete'] == 'y',
            'workout_type': request.form['workout_type'],
            'workout_days': int(request.form['workout_days']),
            'job_activity': request.form['job_activity'],
            'leisure_activity': request.form['leisure_activity'],
            'experience_level': request.form['experience_level'],
        }
        
        # Run the prediction
        progression, initial_data = run_user_interaction(use_test_data=False, user_data=user_data)
        
        # Generate the report
        report_data = generate_comprehensive_report(progression, initial_data)
        
        # Save the report
        report_filename = save_report(report_data, user_data['name'], 'pdf')
        
        return send_file(report_filename, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
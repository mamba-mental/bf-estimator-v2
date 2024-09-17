# app.py

# --- Beginning of File ---

# Author: Tiran Ronelle Winston
# Created: 09/08/24
# Last Modified: 09/12/24
# Description: Flask application for the Weight Loss Predictor web interface.
# Version: 1.3.1
# License: Apache License 2.0

import os
import datetime
import logging
import json
import traceback
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify, abort, send_file, redirect, url_for, session, flash, send_from_directory
from flask_wtf import FlaskForm
from forms import ReportForm
from werkzeug.exceptions import HTTPException
from main import run_user_interaction, generate_comprehensive_report
from report_generation import save_report
from test_data import TEST_DATA
from apscheduler.schedulers.background import BackgroundScheduler
import time
import glob

# Disable interactive mode in Matplotlib
plt.ioff()

# Flask application initialization
app = Flask(__name__,
            template_folder='templates',
            static_folder='styles',
            static_url_path='/styles')

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Set a secret key for session management
app.secret_key = 'mambamental3mil'  # It's better to use a more secure, randomly generated key in production

# Constants
LAST_REPORT_FILE = 'last_report_data.json'
RESULTS_FOLDER = 'results'

# Ensure results directory exists
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP errors
    if isinstance(e, HTTPException):
        return render_template('500.html', error=str(e)), e.code
    # Handle non-HTTP exceptions
    app.logger.error(f"An error occurred: {str(e)}")
    app.logger.error(traceback.format_exc())
    return render_template('500.html', error="An unexpected error occurred. Please try again."), 500

# Utility functions
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

def get_activity_level_description(activity_level):
    activity_levels = {
        1: "Little to no exercise",
        2: "Light exercise/sports 1-3 days/week",
        3: "Moderate exercise/sports 3-5 days/week",
        4: "Hard exercise/sports 6-7 days a week",
        5: "Very hard exercise/sports & a physical job"
    }
    return activity_levels.get(int(activity_level), "Unknown")

# Routes
@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('styles/js', filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('styles', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    form = ReportForm()
    if form.validate_on_submit():
        try:
            app.logger.info("POST request received for report generation")
            
            user_data = {
                'name': form.name.data,
                'current_weight': form.current_weight.data,
                'current_bf': form.current_bf.data,
                'goal_weight': form.goal_weight.data,
                'goal_bf': form.goal_bf.data,
                'height_feet': form.height_feet.data,
                'height_inches': form.height_inches.data,
                'protein_intake': form.protein_intake.data,
                'activity_level': int(form.activity_level.data),
                'workout_days': form.workout_days.data,
                'resistance_training': form.resistance_training.data,
                'is_athlete': form.is_athlete.data,
                'workout_type': form.workout_type.data,
                'job_activity': form.job_activity.data,
                'leisure_activity': form.leisure_activity.data,
                'experience_level': form.experience_level.data
            }
            
            app.logger.debug(f"User data before processing: {user_data}")
            
            progression, initial_data = run_user_interaction(use_test_data=False, user_data=user_data)
            
            app.logger.info("Starting generate_comprehensive_report")
            report_data = generate_comprehensive_report(progression, initial_data)
            
            app.logger.debug(f"Report data generated: {report_data}")
            
            # Save reports in all desired formats and store paths
            saved_files = save_report(report_data, initial_data.get('name', 'User'), 'both')  # Save both markdown and pdf
            
            app.logger.debug(f"Saved files: {saved_files}")
            
            # Store the saved file paths in the session
            session['saved_files'] = saved_files
            session['report_filename'] = os.path.basename(saved_files.get('json', ''))
            
            # **Update last_report_data.json with user_data**
            with open(LAST_REPORT_FILE, 'w') as f:
                json.dump(user_data, f, default=str)
            app.logger.debug(f"Updated {LAST_REPORT_FILE} with latest user data.")
            
            app.logger.info("Report generation completed successfully")
            return redirect(url_for('show_results'))
        except Exception as e:
            app.logger.error(f"Error processing request: {str(e)}")
            app.logger.error(traceback.format_exc())
            flash("An error occurred while generating the report. Please try again.", "error")
            return render_template('index.html', form=form)

    return render_template('index.html', form=form)

@app.route('/results')
def show_results():
    report_filename = session.get('report_filename')
    app.logger.debug(f"Report filename in session: {report_filename}")
    if not report_filename:
        app.logger.warning("No report filename found in session, redirecting to index")
        flash("No report found. Please generate a report first.", "warning")
        return redirect(url_for('index'))
    
    filepath = os.path.join(RESULTS_FOLDER, report_filename)
    if not os.path.exists(filepath):
        app.logger.warning(f"Report file not found: {filepath}")
        flash("Report file not found. Please generate a new report.", "warning")
        return redirect(url_for('index'))
    
    with open(filepath, 'r') as f:
        report_data = json.load(f)
    
    app.logger.info("Rendering results page")
    return render_template('results.html', report=report_data, get_score_description=get_score_description)

@app.route('/download/<format>')
def download_report(format):
    saved_files = session.get('saved_files')
    app.logger.debug(f"Saved files in session: {saved_files}")
    
    if not saved_files:
        flash("No report found. Please generate a report first.", "warning")
        return redirect(url_for('index'))
    
    # Determine the correct file path based on the format
    if format == 'pdf':
        file_path = saved_files.get('pdf')
    elif format in ['md', 'markdown']:
        file_path = saved_files.get('markdown')
    elif format == 'json':
        file_path = saved_files.get('json')
    else:
        flash("Invalid format requested.", "error")
        return redirect(url_for('index'))
    
    if not file_path or not os.path.exists(file_path):
        flash("Requested report format not found.", "error")
        return redirect(url_for('index'))
    
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error sending file: {str(e)}")
        flash("An error occurred while downloading the report. Please try again.", "error")
        return redirect(url_for('index'))



@app.route('/get_test_data', methods=['GET'])
def get_test_data():
    test_data = TEST_DATA.copy()
    test_data['activity_level_description'] = get_activity_level_description(int(test_data['activity_level']))
    app.logger.info(f"Serving test data: {test_data}")
    return jsonify(test_data)

@app.route('/get_last_report_data', methods=['GET'])
def get_last_report_data():
    if os.path.exists(LAST_REPORT_FILE):
        try:
            with open(LAST_REPORT_FILE, 'r') as f:
                last_data = json.load(f)
            
            # Optionally, update dates or other fields as needed
            today = datetime.date.today()
            last_data['start_date'] = today.strftime('%m%d%y')
            last_data['end_date'] = (today + datetime.timedelta(weeks=12)).strftime('%m%d%y')
            
            app.logger.debug(f"Last report data: {last_data}")
            return jsonify(last_data)
        except json.JSONDecodeError:
            app.logger.error("JSON decoding failed for last_report_data.json.")
            return jsonify({"error": "Corrupted last report data. Please generate a new report."}), 500
        except Exception as e:
            app.logger.error(f"Error reading last report data: {str(e)}")
            return jsonify({"error": "An error occurred while fetching last report data."}), 500
    else:
        app.logger.warning("last_report_data.json not found.")
        return jsonify({"error": "No previous report data found."}), 404




@app.route('/test', methods=['GET'])
def test():
    try:
        test_data = TEST_DATA.copy()
        test_data['activity_level_description'] = get_activity_level_description(int(test_data['activity_level']))
        app.logger.debug(f"Test data for report generation: {test_data}")
        
        progression, initial_data = run_user_interaction(use_test_data=True, user_data=test_data)
        report_data = generate_comprehensive_report(progression, initial_data)
        
        app.logger.debug(f"Test report data generated: {report_data}")
        
        # Generate a unique filename for the test report
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{timestamp}.json"
        filepath = os.path.join(RESULTS_FOLDER, filename)
        
        # Write the report data to a file
        with open(filepath, 'w') as f:
            json.dump(report_data, f, default=str)
        
        app.logger.info(f"Test report saved to file: {filepath}")
        
        # Store the filename in the session
        session['report_filename'] = filename
        
        return redirect(url_for('show_results'))
    except Exception as e:
        app.logger.error(f"Error in test route: {str(e)}")
        flash("An error occurred while generating the test report. Please try again.", "error")
        return redirect(url_for('index'))

@app.route('/update_weekly', methods=['POST'])
def update_weekly():
    if not os.path.exists(LAST_REPORT_FILE):
        flash("No previous data found. Please submit a full form first.", "warning")
        return redirect(url_for('index'))
    
    try:
        with open(LAST_REPORT_FILE, 'r') as f:
            last_data = json.load(f)
        
        last_data['current_weight'] = float(request.form['weekly_weight'])
        last_data['current_bf'] = float(request.form['weekly_bf'])
        
        today = datetime.date.today()
        last_data['start_date'] = today.strftime('%m%d%y')
        last_data['end_date'] = (today + datetime.timedelta(weeks=12)).strftime('%m%d%y')
        
        app.logger.debug(f"Updated data for weekly report: {last_data}")
        
        progression, initial_data = run_user_interaction(use_test_data=False, user_data=last_data)
        report_data = generate_comprehensive_report(progression, initial_data)
        
        app.logger.debug(f"Weekly report data generated: {report_data}")
        
        # Generate a unique filename for the weekly report
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"weekly_report_{timestamp}.json"
        filepath = os.path.join(RESULTS_FOLDER, filename)
        
        # Write the report data to a file
        with open(filepath, 'w') as f:
            json.dump(report_data, f, default=str)
        
        app.logger.info(f"Weekly report saved to file: {filepath}")
        
        # Store the filename in the session
        session['report_filename'] = filename
        
        return redirect(url_for('show_results'))
    except Exception as e:
        app.logger.error(f"Error in update_weekly: {str(e)}")
        flash("An error occurred while updating the weekly report. Please try again.", "error")
        return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning("404 error encountered")
    return render_template('400.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error("500 error encountered")
    return render_template('500.html', error="Internal server error"), 500

def cleanup_old_reports(retention_days=30):
    now = time.time()
    cutoff = now - (retention_days * 86400)  # 86400 seconds in a day
    for filename in glob.glob(os.path.join(RESULTS_FOLDER, '*')):
        if os.path.isfile(filename):
            if os.path.getmtime(filename) < cutoff:
                os.remove(filename)
                app.logger.info(f"Deleted old report file: {filename}")

# Initialize Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=cleanup_old_reports, trigger="interval", days=1)
scheduler.start()

# Shut down the scheduler when exiting the app
import atexit
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

# --- Footer ---
# Status: Development
# Contact: mambamental3mil@gmail.com
# © 2024 Mamba Matrix Solutions LLC. All rights reserved.
# --- End of File ---
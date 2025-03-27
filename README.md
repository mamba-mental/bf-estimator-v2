# Body Fat Estimator

A comprehensive tool to estimate and track body fat percentage, generate reports, and provide analysis for fitness goals.

## Overview

The Body Fat Estimator is a multi-purpose application that allows users to:
- Calculate and estimate body fat percentages
- Track weight and body fat progress over time
- Generate comprehensive PDF and Markdown reports
- Visualize progress with charts and graphs
- Set and monitor fitness goals

This application is available in two modes:
1. **Web Application** - A Flask-based web interface
2. **Desktop Application** - A CustomTkinter-based GUI application

## Getting Started

### Prerequisites

- Python 3.8 or newer
- Required packages (installed automatically by the launcher):
  - For web mode: `flask`, `pillow`, `matplotlib`
  - For desktop mode: `customtkinter`, `pillow`, `matplotlib`

### Installation

1. Clone or download this repository
2. Navigate to the repository directory
3. Run the launcher:
   - **Windows**: Double-click `run_bf_estimator.bat`
   - **Mac/Linux**: Run `python app_launcher.py` in your terminal

### Using the Application

#### Running the Application

When you run the application launcher, you'll be prompted to choose between web mode and desktop mode:

```
Body Fat Estimator Launcher
===========================
1: Desktop Application (CustomTkinter GUI)
2: Web Application (Flask web server)

Enter your choice (1-2):
```

#### Web Mode

The web mode provides a browser-based interface that's easy to use and navigate:

1. After selecting web mode (option 2), the Flask server will start
2. Open your web browser and navigate to http://127.0.0.1:5000
3. Use the web interface to enter your data and generate reports

#### Desktop Mode

The desktop mode provides a standalone application with full functionality:

1. After selecting desktop mode (option 1), the GUI application will launch
2. Use the tabbed interface to navigate between different sections:
   - **Input Data**: Enter personal information and measurements
   - **Weekly Progress**: Track and visualize changes over time
   - **Reports History**: View and manage previously generated reports
   - **Results**: See the latest report results
   - **About**: Application information

### Quick Start Guide

#### Generating a Test Report

To quickly test the functionality of the application:

1. Launch the application in either web or desktop mode
2. Click the "Generate Test Report" button
3. View the generated report in the Results tab

#### Tracking Progress

To track your progress over time:

1. Navigate to the "Weekly Progress" tab
2. Enter your current weight, body fat percentage, and any notes
3. Click "Add Entry"
4. View your progress in the charts and history table

## Features

### Body Fat Estimation

The application uses proven methods to estimate body fat percentage based on:
- Personal metrics (age, gender, height, weight)
- Activity level and exercise habits
- Fitness goals and timeframes

### Report Generation

Generate comprehensive reports that include:
- Current body composition analysis
- Progress tracking over time
- Lean mass preservation scores
- Weight loss predictions
- Customized recommendations

### Data Visualization

View your progress with interactive charts:
- Weight progress over time
- Body fat percentage changes
- Goal tracking

### File Export

Export your data in multiple formats:
- PDF reports for printing and sharing
- Markdown files for easy viewing
- JSON data for backup and portability

## Technical Information

### Project Structure

- `app_launcher.py` - Main entry point for the application
- `run_bf_estimator.bat` - Windows batch file for easy launching
- `run.py` - Web application launcher
- `main.py` - Core calculation and processing logic
- `calculations.py` - Algorithms for body fat estimations
- `report_generation.py` - Report creation functionality
- `desktop_app.py` - Desktop GUI application

### Dependencies

- **Flask**: Web framework for the browser interface
- **CustomTkinter**: Modern UI library for desktop application
- **Matplotlib**: Data visualization for charts and graphs
- **Pillow**: Image processing for charts and reports

## Troubleshooting

### Common Issues

**Missing Dependencies**
If you see errors about missing packages, you can install them manually:
```
# For web mode
pip install flask pillow matplotlib

# For desktop mode
pip install customtkinter pillow matplotlib
```

**Web Application Not Starting**
- Make sure no other application is using port 5000
- Check if Flask is properly installed
- Try running `python run.py` directly and enter "web"

**Desktop Application Not Launching**
- Ensure CustomTkinter is installed
- Check for any error messages in the console
- Try using the fallback basic GUI

## License

This project is licensed under the MIT License - see the LICENSE file for details.

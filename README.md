# BF Estimator - Terminal Version

A terminal-based body fat estimation and weight loss prediction tool that calculates personalized weight loss projections, caloric requirements, and generates comprehensive reports based on user metrics and fitness parameters.

## Description

BF Estimator helps users predict their weight loss journey by analyzing personal data including current weight, body fat percentage, activity levels, and workout routines. The application uses scientifically-backed formulas to calculate caloric requirements and projects weekly changes in weight and body composition. Results are presented through comprehensive reports available in both PDF and Markdown formats.

## Prerequisites & Installation

### System Requirements
- **Python 3.x** (REQUIRED - the application will not run without Python installed)
- Windows (for running the batch file, though the Python code is cross-platform)
- Approximately 50MB of free disk space

### Installation

1. **Install Python** if not already installed:
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH" to ensure Python is accessible from the command line
   
2. Clone or download this repository to your local machine

3. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
   
4. For backend functionality (if needed):
   ```
   pip install -r backend/requirements.txt
   ```

### Special Requirements

The application uses two different methods for PDF generation:

- **WeasyPrint**: Requires Cairo graphics library. On Windows, the GTK3 setup is included (`gtk3-setup.exe`)
- **wkhtmltopdf**: Binary executable included (`wkhtmltopdf.exe`)

## Usage

### Running the Application

To run the BF Estimator terminal app, follow these simple steps:

**Step 1:** Open a terminal/command prompt in the project directory
(Navigate to `z:/2024.0917 - Bf-estimator-v2/122924_bf-estimator-terminal` or wherever you've installed the app)

**Step 2:** Choose one of these methods to launch the app:

**Option 1: Using the batch file (Windows) - RECOMMENDED FOR WINDOWS USERS**
```
run_terminal.bat
```
This is the easiest method for Windows users as it automatically checks for Python installation and dependencies.

**Option 2: Running the Python script directly**
```
python main.py
```
This works on any operating system with Python installed.

**Option 3: Using run.py**
```
python run.py
```
Alternative entry point with the same functionality as main.py.

**Step 3:** Follow the interactive prompts to enter your personal information and fitness parameters.

**Step 4:** After entering all required information, the app will:
- Calculate your personalized weight loss projection
- Generate caloric requirements for your goals
- Create detailed reports in both PDF and Markdown formats in the current directory
- Display a summary of the results in the terminal

The generated reports (PDF and MD files) will be saved in the same directory with your name and the current date.

### Test Mode

To run the application with predefined test data instead of interactive input:
```
python main.py --test
```

### Input Parameters

When running in interactive mode, the application will prompt for the following information:

1. **Personal Information**
   - Name
   - Current weight (lbs)
   - Current body fat percentage
   - Goal weight (lbs)
   - Goal body fat percentage
   - Start date (MMDDYY format)
   - End date (MMDDYY format)
   - Date of birth (MMDDYY format)
   - Gender (m/f)
   - Height (feet and inches)
   - Daily protein intake (grams)

2. **Activity & Fitness Information**
   - Activity level (1-5 scale)
   - Resistance training status (Y/N)
   - Athlete status (Y/N)
   - Workout type (Bodybuilding, Cardio, General Fitness)
   - Workout frequency (days per week)
   - Job activity level (1-4 scale)
   - Leisure activity level (1-4 scale)
   - Experience level (1-5 scale)

### Example Session

```
Welcome to the Weight Loss Predictor!
=====================================
Please enter your information below:

Enter your name: John Smith
Enter your current weight in lbs: 200
Enter your current body fat percentage: 25
Enter your goal weight in lbs: 180
Enter your goal body fat percentage: 15
Enter your start date (MMDDYY): 052125
Enter your end date (MMDDYY): 083125
Enter your date of birth (MMDDYY): 011090
Enter your gender (m/f): m
Enter your height (feet): 5
Enter your height (inches): 10
Enter your daily protein intake in grams: 180
Enter your activity level (1-5):
1. Little to no exercise
2. Light exercise/sports 1-3 days/week
3. Moderate exercise/sports 3-5 days/week
4. Hard exercise/sports 6-7 days a week
5. Very hard exercise/sports & a physical job
Choose an option: 3
Are you doing resistance training? (Y/N): y
Are you an athlete? (Y/N): n
What type of workouts do you primarily do?
1. Bodybuilding (Strength training and muscle building)
2. Cardio (Cardiovascular exercises like running or cycling)
3. General Fitness (A mix of different exercises for overall health)
Choose an option: 1
How many days per week do you work out? 4
Select your job activity level:
1. Mostly sitting (e.g., desk job)
2. Light activity (e.g., teacher, salesperson)
3. Moderate activity (e.g., construction worker)
4. Very active (e.g., courier, agriculture)
Choose an option: 1
Select your leisure activity level:
1. Little to no physical activity
2. Light physical activity (e.g., walking, gardening)
3. Moderate physical activity (e.g., hiking, dancing)
4. High physical activity (e.g., sports, intense exercise)
Choose an option: 2
Enter your experience level (1-5):
1. Beginner (0-1 year)
2. Novice (1-2 years)
3. Intermediate (2-4 years)
4. Advanced (4-10 years)
5. Elite (10+ years)
Choose an option: 3
```

After providing the inputs, the application will generate predictions and create reports.

## Project Structure & Module Overview

```
├── app.py                    # Flask web application entry point (if using web interface)
├── calculations.py           # Core calculation algorithms for weight loss prediction
├── forms.py                  # Form definitions
├── main.py                   # Main entry point for terminal application
├── report_generation.py      # Functions for generating PDF and Markdown reports
├── requirements.txt          # Project dependencies
├── run.py                    # Alternative entry point
├── run_terminal.bat          # Windows batch file to run the application
├── test_data.py              # Contains sample data for testing
├── user_interaction.py       # Functions for handling user input in the terminal
├── utils.py                  # Helper functions for various calculations
├── wkhtmltopdf.exe           # PDF generation tool
├── backend/                  # Backend components for web application (optional use)
│   ├── main.py               # Backend entry point
│   ├── report_generation.py  # Backend report generation
│   ├── requirements.txt      # Backend-specific dependencies
│   ├── styles/               # CSS styles for reports
│   └── templates/            # HTML templates
├── styles/                   # CSS styles for the main application
└── templates/                # HTML templates for the main application
└── tests/                    # Automated tests
    ├── __init__.py
    ├── test_calculations.py  # Tests for calculation functions
    ├── test_report_generation.py # Tests for report generation
    └── test_user_interaction.py  # Tests for user interaction
```

### Key Module Descriptions

- **main.py**: Entry point for the terminal application that handles user interaction, data processing, and report generation. It provides options for both interactive input and testing with predefined data.

- **calculations.py**: Contains algorithms for calculating weight loss projections, metabolic adaptation, lean mass preservation, muscle gain, TDEE (Total Daily Energy Expenditure), and distributing weight loss between fat and lean mass.

- **report_generation.py**: Handles the creation of visual reports including charts, tables, and comprehensive PDF and Markdown documents summarizing the weight loss predictions.

- **user_interaction.py**: Provides utilities for gathering and validating user input, including functions for float, integer, date inputs, and selection from predefined choices.

- **utils.py**: Contains helper functions for calculating age, estimating thermic effect of food (TEF), non-exercise activity thermogenesis (NEAT), and resting metabolic rate (RMR).

- **forms.py**: Defines form structures for collecting user data.

- **run_terminal.bat**: Windows batch script that checks for Python installation, installs dependencies, and launches the application.

## Testing

The application includes automated tests using pytest. Tests are located in the `tests/` directory.

### Running Tests

To run all tests:
```
pytest
```

To run specific test modules:
```
pytest tests/test_calculations.py
pytest tests/test_report_generation.py
pytest tests/test_user_interaction.py
```

To run tests with verbose output:
```
pytest -v
```

### Test Files

- **tests/test_calculations.py**: Tests for the calculation algorithms
- **tests/test_report_generation.py**: Tests for report generation functions
- **tests/test_user_interaction.py**: Tests for user input functions

## Report Generation

The application generates comprehensive reports in both PDF and Markdown formats. These reports include:

1. User profile information (name, age, gender, height, etc.)
2. Current and goal metrics (weight, body fat percentage)
3. Visual charts showing projected weight and body fat changes
4. Weekly progression details
5. Metabolic calculations and projections
6. Body composition changes
7. Workout analysis

### Report Templates and Styling

- HTML templates for reports are stored in the `templates/` directory
- CSS styling for reports is in the `styles/` directory
- The main report template is `templates/report_template.html`

### PDF Generation Dependencies

The application uses two methods for PDF generation:

1. **WeasyPrint**: A Python library that converts HTML/CSS to PDF
   - Requires Cairo graphics library
   - On Windows, this is provided by the included GTK3 setup

2. **wkhtmltopdf**: An external tool that converts HTML to PDF
   - The executable is included in the repository

## Troubleshooting

### "Python is not installed!" or "Python was not found"
If you see this error when running the batch file or Python commands:

1. **Check if Python is installed**:
   - Open a command prompt and type `python --version` or `py --version`
   - If neither command works, Python is not installed or not in your PATH

2. **Install Python**:
   - Download and install Python from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation
   
3. **Verify installation**:
   - Open a new command prompt and type `python --version`
   - You should see the Python version number if installation was successful

4. **Try running the app again**:
   - After installing Python, try running the application again using one of the methods described in the Usage section

### PDF Generation Issues
If the application runs but fails to generate PDF reports:

1. **Try installing GTK3**:
   - Run the included `gtk3-setup.exe` to install the GTK3 library needed by WeasyPrint

2. **Check error.log**:
   - Look for an `error.log` file in the application directory for specific error details

## License & Author

© 2025 Mamba Matrix Solutions LLC. All rights reserved.

**Author**: Tiran Ronelle Winston
**Contact**: mambamental3mil@gmail.com
**License**: Apache License 2.0
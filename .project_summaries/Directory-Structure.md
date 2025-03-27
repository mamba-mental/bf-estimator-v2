# Project Directory Structure

## Directory Tree

.
├── app.py
├── calculations.py
├── main.py
├── report_generation.py
├── run.py
├── test_data.py
├── user_interaction.py
├── utils.py
├── requirements.txt
├── templates
│   ├── 400.html
│   ├── 500.html
│   ├── index.html
│   └── results.html
├── styles
│   ├── favicon.ico
│   ├── main.css
│   ├── report_style.css
│   ├── web_style.css
│   └── js
│       └── main.js
├── results
└── tests
    ├── test_calculations.py
    ├── test_report_generation.py
    └── test_user_interaction.py
```

## Root Directory
- **requirements.txt**: Lists all the dependencies needed for the project.
- **app.py**: The main Flask application script that handles web requests, processes user data, and generates reports.
- **calculations.py**: Contains functions for calculating various fitness and nutritional metrics.
- **main.py**: The entry point script for running the Weight Loss Predictor program either in terminal mode or web mode.
- **report_generation.py**: Handles the generation of detailed reports in markdown and PDF formats.
- **run.py**: Manages the execution of the program in different modes (terminal or web) and handles environment configurations.
- **test_data.py**: Contains test data used for testing purposes.
- **user_interaction.py**: Contains utility functions to interact with users, obtaining and validating various types of inputs.
- **utils.py**: Provides utility functions for calculating age, thermic effect of food (TEF), non-exercise activity thermogenesis (NEAT), and resting metabolic rate (RMR).

## Templates Directory
- **templates**
  - **400.html**: Custom 404 error page template.
  - **500.html**: Custom 500 error page template.
  - **index.html**: Main page template for the weight loss predictor application.
  - **results.html**: Template for displaying the weight loss journey report.

## Styles Directory
- **styles**
  - **favicon.ico**: The favicon used for the website.
  - **main.css**: Primary CSS file for general styling across the website.
  - **report_style.css**: CSS file specifically for styling the generated reports.
  - **web_style.css**: CSS file used for styling the web pages.
  - **js**
    - **main.js**: JavaScript file for handling form submissions and other dynamic interactions on the website.

## Results Directory
- **results**: Directory for saving generated reports.

## Tests Directory
- **tests**
  - **test_calculations.py**: Unit tests for the functions in `calculations.py`.
  - **test_report_generation.py**: Unit tests for the functions in `report_generation.py`.
  - **test_user_interaction.py**: Unit tests for the functions handling user interaction.

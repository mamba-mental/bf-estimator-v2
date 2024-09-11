# Weight Loss Predictor Application

Welcome to the **Weight Loss Predictor** application, a sophisticated and comprehensive tool designed to provide users with accurate predictions of their weight loss journey. This application integrates advanced metabolic science, precise body composition analysis, and extensive user interaction to deliver personalized insights into weight loss progress over time.

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Directory Structure](#directory-structure)
- [File Descriptions](#file-descriptions)
  - [`.gitignore`](#gitignore)
  - [`bf-estimator-v2.code-workspace`](#bf-estimator-v2code-workspace)
  - [`main.py`](#mainpy)
  - [`calculations.py`](#calculationspy)
  - [`report_generation.py`](#report_generationpy)
  - [`test_weight_loss_predictor.py`](#test_weight_loss_predictorpy)
  - [`user_interaction.py`](#user_interactionpy)
  - [`utils.py`](#utilspy)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [Input Details](#input-details)
  - [Output and Reports](#output-and-reports)
- [Detailed Functionality](#detailed-functionality)
  - [Metabolic Calculations](#metabolic-calculations)
  - [Predictive Modeling](#predictive-modeling)
  - [User Interaction](#user-interaction)
  - [Report Generation](#report-generation)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The **Weight Loss Predictor** is a Python-based application that leverages scientifically-backed algorithms and user-specific data to predict weight loss progress. It is designed for individuals who are serious about tracking and optimizing their fitness goals. The application guides users through a series of inputs, calculates key metabolic metrics, and forecasts body composition changes over a defined period.

## Key Features

- **Personalized Predictions**: Tailored predictions based on user-specific data including weight, body fat percentage, activity level, and more.
- **Comprehensive Reporting**: Generates detailed reports that include weekly progress, metabolic adaptation, and body composition changes.
- **Advanced Algorithms**: Utilizes complex formulas to simulate metabolic adaptations and predict muscle gain/loss.
- **User-Friendly Interaction**: Designed with an intuitive user interface that guides users step-by-step through the process.
- **Cross-Platform**: Compatible with multiple operating systems, provided Python is installed.

## Directory Structure

The project directory is structured to separate core functionalities, user interactions, and testing:

```plaintext
.
├── .gitignore
├── bf-estimator-v2.code-workspace
├── main.py
├── calculations.py
├── report_generation.py
├── test_weight_loss_predictor.py
├── user_interaction.py
└── utils.py
```

## File Descriptions

### `.gitignore`

The `.gitignore` file is essential for keeping your working directory clean. It specifies which files and directories Git should ignore, preventing them from being accidentally tracked or committed to the repository.

**Ignored Files:**
- `.env`: Typically used to store environment variables, which might contain sensitive data.
- `config.ini`: Configuration files that may contain environment-specific settings.
- `secrets.json`: Often contains API keys, passwords, or other sensitive information that should not be exposed.

### `bf-estimator-v2.code-workspace`

This file is a Visual Studio Code workspace configuration file. It stores settings, the workspace structure, and extensions used by the project, ensuring consistency across different development environments.

**Purpose:**
- Facilitates collaborative development by maintaining a consistent environment configuration.
- Ensures that the same set of tools and settings are applied when the project is opened in VS Code.

### `main.py`

The `main.py` file is the entry point of the application, orchestrating the flow of user interaction, data input, and the subsequent calculations that drive the prediction model.

**Core Functions:**
- `run_user_interaction()`: This function manages the entire user interaction sequence. It collects inputs from the user, including current and goal body metrics, activity levels, dietary habits, and more. After gathering all necessary data, it invokes the predictive model and generates a summary report.
  - **Input Handling**: Utilizes functions from `user_interaction.py` to ensure robust data validation and collection.
  - **Data Processing**: Integrates with `calculations.py` to perform complex metabolic calculations and predict weight loss.
  - **Report Generation**: Calls `print_summary()` from `report_generation.py` to create and display a detailed report.

### `calculations.py`

This file houses the core computational logic of the application. It includes functions that perform various metabolic and body composition calculations essential to the weight loss prediction model.

**Key Functions and Their Roles:**
- `estimate_muscle_gain()`: Estimates potential muscle gain based on factors such as training frequency, volume, intensity, protein intake, and user experience level.
- `calculate_lean_mass_preservation_scores()`: Calculates scores related to the preservation of lean mass during weight loss, considering the type, volume, and intensity of workouts.
- `calculate_tdee()`: Computes the Total Daily Energy Expenditure by considering the user’s Resting Metabolic Rate (RMR), activity level, and additional factors such as the Thermic Effect of Food (TEF) and Non-Exercise Activity Thermogenesis (NEAT).
- `calculate_metabolic_adaptation()`: Models how the user’s metabolism might adapt over time as they lose weight, which is crucial for predicting changes in energy expenditure.
- `predict_weight_loss()`: The central function that predicts weight loss over the specified period. It simulates weekly weight changes, fat loss, and lean mass alterations, taking into account the user's dietary intake, exercise habits, and metabolic adaptations.

### `report_generation.py`

The `report_generation.py` file focuses on formatting and saving the output generated by the application. It creates detailed reports summarizing the user's predicted weight loss journey.

**Core Components:**
- `generate_comprehensive_report()`: Constructs a detailed report in markdown format that includes all relevant data points, such as weight, body fat percentage, muscle gain, and metabolic rates, over the entire prediction period.
  - **Report Sections**: The report is divided into sections, each focusing on a specific aspect of the user's journey, including personal profile, metabolic calculations, workout analysis, and final results.
- `save_report()`: Saves the generated report to a specified location in either markdown or PDF format.
  - **Error Handling**: Includes mechanisms to handle errors during PDF generation, providing alternative instructions if the necessary tools (like `wkhtmltopdf`) are not installed.
- `print_summary()`: Outputs the report directly to the console, offering a quick summary for the user.

### `test_weight_loss_predictor.py`

This file is dedicated to testing the application's functionality, ensuring that all components work as expected. It uses the `unittest` framework to validate the accuracy of the calculations and predictions.

**Key Tests:**
- `test_calculate_rmr()`: Verifies that the Resting Metabolic Rate (RMR) is calculated within a reasonable range based on user inputs.
- `test_calculate_tdee()`: Ensures that the Total Daily Energy Expenditure (TDEE) is accurately computed, reflecting the user's metabolic needs.
- `test_predict_weight_loss()`: Tests the entire weight loss prediction process, checking for consistency in weekly weight loss, body fat percentage reduction, and adherence to the timeline.
- `test_verified_minimum_calories()`: Ensures that the predicted daily calorie intake does not fall below a safe threshold, protecting against unrealistic or dangerous predictions.

### `user_interaction.py`

The `user_interaction.py` file is responsible for managing all user inputs. It includes functions designed to handle different types of input, ensuring that the data is valid and correctly formatted before being processed.

**Important Functions:**
- `get_float_input()`, `get_int_input()`: Handle numerical inputs, ensuring that the user enters valid floats or integers, respectively.
- `get_experience_level_input()`: Guides the user through selecting their experience level in physical training, ensuring that the choice corresponds to a valid option.
- `get_date_input()`: Ensures the user provides a correctly formatted date, converting it into a usable datetime object.
- `get_yes_no_input()`: Collects and validates binary (yes/no) inputs, ensuring clarity in the user’s responses.
- `get_choice_input()`: Presents the user with a list of options and validates the selection, ensuring the input aligns with the provided choices.

### `utils.py`

The `utils.py` file contains auxiliary functions that support the main computational tasks. These functions provide essential calculations that are used across the application.

**Utility Functions:**
- `calculate_age()`: Computes the user’s age from their date of birth and the current date, a critical factor in many of the metabolic calculations.
- `estimate_tef()`: Estimates the Thermic Effect of Food, which is the number of calories burned during digestion, based on the user’s protein intake.
- `estimate_neat()`: Estimates Non-Exercise Activity Thermogenesis, which accounts for the calories burned during non-exercise activities, like daily chores or fidgeting.
- `calculate_rmr()`: Calculates the Resting Metabolic Rate (RMR), a baseline measure of how many calories the user burns at rest, based on their weight, age, gender, and height.

## Installation

### Prerequisites

Before you

 begin, ensure you have the following installed on your system:

- **Python 3.7+**: The application is written in Python, so you'll need Python installed. You can download it from [python.org](https://www.python.org/downloads/).
- **pip**: Python’s package installer, used to install the required dependencies.
- **wkhtmltopdf** (optional): Required if you want to generate PDF reports. It can be downloaded from [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html).

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/weight-loss-predictor.git
   cd weight-loss-predictor
   ```

2. **Set up a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Install wkhtmltopdf** for PDF report generation:
   - Download from: [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html)
   - Follow the installation instructions and ensure the binary is added to your system PATH.

5. **Run the application**:
   ```bash
   python main.py
   ```

## Usage

### Running the Application

To start using the Weight Loss Predictor, simply run the `main.py` script. The application will guide you through a series of prompts to collect the necessary data.

### Input Details

The application will ask for the following details:
- **Current Weight**: Your current weight in pounds.
- **Current Body Fat Percentage**: Your current body fat percentage.
- **Goal Weight**: Your target weight in pounds.
- **Goal Body Fat Percentage**: Your target body fat percentage.
- **Start and End Dates**: The period over which you want to achieve your goals.
- **Date of Birth**: Used to calculate your age.
- **Gender**: 'm' for male or 'f' for female.
- **Height**: Both in feet and inches, which will be converted to centimeters for calculations.
- **Daily Protein Intake**: Your average daily protein consumption in grams.
- **Activity Level**: A choice between different levels of physical activity.
- **Resistance Training**: Whether you engage in resistance training (yes/no).
- **Athletic Status**: Whether you are an athlete (yes/no).
- **Workout Type**: The type of workouts you primarily do (e.g., bodybuilding, cardio).
- **Job and Leisure Activity Levels**: Activity levels during your job and leisure time.
- **Experience Level**: Your experience level in physical training.

### Output and Reports

After collecting the inputs, the application will process the data and generate a comprehensive report. This report will include:
- **Personal Profile**: A summary of your input data.
- **Metabolic Calculations**: Details on your RMR, TDEE, and other metabolic factors.
- **Workout Analysis**: Insights into how your training affects your weight loss.
- **Weekly Progress Forecast**: Predicted changes in weight, body fat percentage, and more over each week.
- **Final Results**: A summary of your projected achievements by the end of the period.
- **Recommendations**: Personalized advice based on your predicted outcomes.

## Detailed Functionality

### Metabolic Calculations

The application uses advanced metabolic calculations to predict your weight loss progress. Key factors include:

- **Resting Metabolic Rate (RMR)**: Calculated based on the Mifflin-St Jeor equation, adjusted for athletic status.
- **Total Daily Energy Expenditure (TDEE)**: Includes RMR plus calories burned through physical activity, the Thermic Effect of Food (TEF), and Non-Exercise Activity Thermogenesis (NEAT).
- **Metabolic Adaptation**: Accounts for the slowing of metabolism over time as you lose weight.

### Predictive Modeling

The weight loss prediction is done through a detailed simulation of weekly progress:

- **Weight Loss Distribution**: The application distinguishes between fat loss and lean mass loss, factoring in protein intake and resistance training.
- **Muscle Gain Estimation**: For those engaged in resistance training, the application predicts potential muscle gain.
- **Caloric Intake Adjustment**: Adjusts daily caloric intake dynamically based on progress and metabolic adaptation.

### User Interaction

The application ensures a smooth and intuitive user experience:

- **Input Validation**: Every input is validated to prevent errors, ensuring accurate predictions.
- **Guided Interaction**: Users are guided step-by-step through the input process, with clear explanations for each required detail.

### Report Generation

Reports are generated to provide a clear, detailed summary of your predicted weight loss journey:

- **Markdown Reports**: Generated by default, easily readable and shareable.
- **PDF Reports**: Optional, providing a polished document suitable for formal use.

## Testing

To validate the correctness of the application, run the provided unit tests:

```bash
python -m unittest discover
```

These tests cover all major functions, ensuring that the predictions and calculations are accurate and reliable.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. **Fork the repository**.
2. **Create a new branch** (`git checkout -b feature-branch-name`).
3. **Make your changes** and commit them (`git commit -m 'Add some feature'`).
4. **Push to the branch** (`git push origin feature-branch-name`).
5. **Open a Pull Request**.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
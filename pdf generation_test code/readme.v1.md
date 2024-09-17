# Weight Loss Predictor Application

Welcome to the **Weight Loss Predictor** application, an advanced tool designed to estimate and predict weight loss progress for users based on a wide range of input variables. This application integrates multiple aspects of metabolic science, body composition analysis, and user interaction to provide personalized and detailed predictions. Below, you’ll find an in-depth explanation of the project structure, the purpose of each file, and the functionality of all the various functions inside these files.

## Table of Contents

- [Project Overview](#project-overview)
- [Directory Structure](#directory-structure)
- [File Descriptions](#file-descriptions)
  - [`.gitignore`](#gitignore)
  - [`main.py`](#mainpy)
  - [`calculations.py`](#calculationspy)
  - [`report_generation.py`](#report_generationpy)
  - [`test_weight_loss_predictor.py`](#test_weight_loss_predictorpy)
  - [`user_interaction.py`](#user_interactionpy)
  - [`utils.py`](#utilspy)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The **Weight Loss Predictor** is a Python-based application that assists users in estimating their weight loss progress over a specified period. The application requires users to input various details such as current and goal body metrics, activity levels, and dietary intake. Using this information, the application calculates and predicts weekly weight loss, body fat percentage reduction, and other key metrics, providing a comprehensive report of the user's journey towards their fitness goals.

## Directory Structure

The project directory is organized as follows:

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

The `.gitignore` file is crucial for maintaining a clean working directory. It specifies which files and directories should be ignored by Git, preventing them from being tracked or committed to the repository.

**Contents:**
- `.env`: Environment variables, often containing sensitive information.
- `config.ini`: Configuration file, potentially with custom settings.
- `secrets.json`: File possibly containing sensitive API keys or passwords.

### `main.py`

The `main.py` file is the central script that ties together all the other components of the application. It manages the user interaction process, gathers input data, calls the necessary calculation functions, and generates a report.

**Key Functions:**
- `run_user_interaction()`: This function is the main entry point of the application. It guides the user through a series of input prompts to gather all necessary data, such as current weight, goal weight, body fat percentages, and lifestyle information. It then calls the `predict_weight_loss()` function and generates a report based on the predictions.

### `calculations.py`

The `calculations.py` file contains all the core mathematical and scientific computations needed for the application. This includes calculations for Resting Metabolic Rate (RMR), Total Daily Energy Expenditure (TDEE), and weight loss prediction.

**Key Functions:**
- `estimate_muscle_gain()`: Estimates the rate of muscle gain based on user-specific factors such as age, gender, experience level, and protein intake.
- `calculate_lean_mass_preservation_scores()`: Computes scores related to workout volume, intensity, and frequency to assess how well lean mass is preserved during weight loss.
- `calculate_tdee()`: Calculates Total Daily Energy Expenditure, combining factors like RMR, Thermic Effect of Food (TEF), and Non-Exercise Activity Thermogenesis (NEAT).
- `predict_weight_loss()`: The core function that simulates weight loss progression over time, considering factors like metabolic adaptation, muscle gain, and fat loss.

### `report_generation.py`

The `report_generation.py` file is responsible for creating and saving detailed reports based on the predictions made by the application. It formats the output into user-friendly markdown and PDF reports.

**Key Functions:**
- `generate_comprehensive_report()`: Generates a detailed markdown report that summarizes the user’s weight loss journey, including weekly progress, metabolic calculations, and body composition changes.
- `save_report()`: Saves the generated report in the specified format (markdown or PDF) to the designated folder.
- `print_summary()`: Outputs a summary of the user’s weight loss predictions directly to the console.

### `test_weight_loss_predictor.py`

This file contains unit tests for validating the correctness of the application's calculations. Using Python’s `unittest` framework, it ensures that all calculations, such as RMR, TDEE, and weight loss predictions, fall within expected ranges.

**Key Tests:**
- `test_calculate_rmr()`: Verifies that the RMR calculation falls within a realistic range.
- `test_calculate_tdee()`: Checks that the TDEE is calculated correctly based on the provided inputs.
- `test_predict_weight_loss()`: Tests the full weight loss prediction process, ensuring that weekly weight loss and body fat percentage are correctly simulated.
- `test_verified_minimum_calories()`: Ensures that the predicted daily calorie intake does not fall below a safe minimum threshold.

### `user_interaction.py`

The `user_interaction.py` file handles all user inputs, ensuring data is collected in a structured and error-free manner. It provides various input validation functions for different data types.

**Key Functions:**
- `get_float_input()`, `get_int_input()`: These functions prompt the user to enter numerical data, ensuring the input is correctly formatted as either a float or integer.
- `get_experience_level_input()`: Guides the user through selecting their experience level, ensuring the choice is valid.
- `get_date_input()`: Validates and parses date input from the user.
- `get_yes_no_input()`: Ensures the user’s response is either ‘Y’ or ‘N’, preventing invalid entries.
- `get_choice_input()`: Presents a list of options to the user and validates the chosen input.

### `utils.py`

The `utils.py` file contains utility functions that support the main calculations. These functions perform auxiliary tasks, such as calculating age or estimating calorie requirements based on activity levels.

**Key Functions:**
- `calculate_age()`: Computes the user’s age based on their date of birth and the current date.
- `estimate_tef()`: Estimates the Thermic Effect of Food based on protein intake, a crucial factor in calculating TDEE.
- `estimate_neat()`: Estimates Non-Exercise Activity Thermogenesis based on job and leisure activity levels.
- `calculate_rmr()`: Computes Resting Metabolic Rate, accounting for user-specific factors like weight, age, gender, and athletic status.

## Installation

To install and run the Weight Loss Predictor application, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/weight-loss-predictor.git
   cd weight-loss-predictor
   ```

2. Set up a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## Usage

Follow the prompts in the terminal to input your details, such as current weight, goal weight, activity level, and more. The application will then process your information and generate a detailed report on your predicted weight loss progress.

## Testing

To ensure the application works correctly, you can run the included unit tests:

```bash
python -m unittest discover
```

This command will run all the tests defined in `test_weight_loss_predictor.py`, validating the accuracy of the calculations.

## Contributing

If you’d like to contribute to the development of this project, please follow these guidelines:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch-name`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch-name`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This README is designed to provide a comprehensive understanding of the application, from its purpose and functionality to installation and usage. By following this guide, users and developers alike can fully leverage the Weight Loss Predictor application.
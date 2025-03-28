# Enhanced User Profile

## Overview

The Enhanced User Profile is a comprehensive data collection module designed to fix critical missing field issues in the fitness app. This interface ensures that all required data for RMR (Resting Metabolic Rate) and body fat calculations is captured correctly, preventing the "missing key 'rmr'" error that previously occurred.

## Key Features

### Critical Fields Implementation

1. **Gender Selection**
   - Properly captures male/female for accurate RMR calculation
   - Required input for gender-specific metabolic formulas

2. **Height Input**
   - Separate fields for feet and inches as required
   - Essential for body composition and metabolic calculations

3. **Date of Birth**
   - Captures age data in MMDDYY format
   - Critical for age-based RMR formula adjustments

4. **Start Date**
   - Records program start date in MMDDYY format
   - Used for tracking progress duration and calculating rate of change

5. **Resistance Training Status**
   - Y/N toggle for resistance training participation
   - Affects recovery needs and caloric recommendations

6. **Workout Type Selection**
   - Dropdown for Bodybuilding/Cardio/General Fitness
   - Informs program recommendations and caloric distribution

7. **Weekly Workout Frequency**
   - Numeric input for training sessions per week
   - Used in activity multiplier calculations for TDEE

8. **Experience Level Selection**
   - 1-5 scale with tooltips for each level
   - Factors into recovery needs and progression expectations

### Dedicated Initial Measurements Section

- Separates baseline measurements from weekly tracking
- Includes:
  - Starting Weight
  - Starting Body Fat Percentage
  - Optional body measurements (waist, hips, chest, arms, etc.)
- Stores data separately from weekly updates

### Additional Enhancements

- **Contact Information Fields**
  - Email and phone for account management
  
- **Expanded Nutrition Section**
  - Protein, carbohydrate, and fat intake fields
  - Diet type selection dropdown

- **Automatic Calculations**
  - RMR based on the Mifflin-St Jeor equation:
    - Men: RMR = 88.362 + (13.397 × weight in kg) + (4.799 × height in cm) - (5.677 × age in years)
    - Women: RMR = 447.593 + (9.247 × weight in kg) + (3.098 × height in cm) - (4.330 × age in years)
  - TDEE (Total Daily Energy Expenditure) with proper activity multiplier
  - Lean body mass and fat mass calculations

## Using the Enhanced Profile UI

### Getting Started

1. Run the Enhanced Profile UI using the included batch file (`run_enhanced_profile.bat`)
2. The interface is organized into five tabs:
   - Personal Information
   - Initial Measurements
   - Goals & Training
   - Nutrition & Lifestyle
   - Summary

### Required Fields

Fields marked with tooltips (hover over the "?" icon) are especially important for calculations. At minimum, you must provide:
- Gender
- Date of Birth
- Height (feet and inches)
- Starting Weight
- Activity Level

### Data Storage

- All profile information is stored in the SQLite database (`history.db`)
- Data is organized in three tables:
  - `user_profiles` - Personal information and preferences
  - `initial_measurements` - Baseline body measurements
  - `weekly_updates` - Progress tracking data

### Calculation Functions

The Summary tab provides calculated metrics based on your input:
- Resting Metabolic Rate (RMR)
- Total Daily Energy Expenditure (TDEE)
- Lean Body Mass
- Fat Mass

## Troubleshooting

If you encounter any issues:

1. **Missing Calculations?** - Check for any required fields marked in red at the bottom of the Summary tab
2. **Database Errors?** - Ensure the application has write permissions to the directory
3. **Calculation Errors?** - Verify all numeric inputs are reasonable values within human physiological ranges

## Technical Notes

- The implementation uses the validated RMR calculations from the `rmr_calculations.py` module
- All critical fields are validated before calculations are performed
- Field tooltips provide guidance on required data format and purpose
- The UI automatically calculates derived values when possible

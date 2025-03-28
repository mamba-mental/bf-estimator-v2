# Diet Calculations Module for BF Estimator

This extension enhances the Body Fat Estimator with comprehensive diet-based calculations and projections. It analyzes macronutrient profiles and diet types to provide personalized fat loss and muscle gain projections.

## Features

- **Enhanced User Profile**: Added fields for gender, height, initial measurements, and comprehensive nutritional data
- **Diet-Specific Analysis**: Calculates how different diet types (Standard, Keto, Low-carb, Vegetarian, Vegan) impact body composition changes
- **Macronutrient Breakdown**: Analyzes protein, carb, and fat intake with percentage breakdown of total calories
- **Customized Projections**: Projects weekly fat loss and muscle gain rates based on:
  - Diet type
  - Resistance training status
  - Experience level
  - Body fat percentage
  - Protein intake
  - Activity level

## How to Use

1. Run `run_enhanced_bf_estimator_with_diet.bat` to launch the enhanced application
2. Fill in all profile fields in the Input Data tab, including:
   - Gender (critical for RMR calculations)
   - Height (feet and inches)
   - Initial weight and body fat
   - Training information
   - Nutrition information
3. Generate a report to see diet-specific projections 

## Diet Type Effects

Different diet types have varying effects on body composition changes:

| Diet Type | Fat Loss Effect | Muscle Gain Effect |
|-----------|----------------|-------------------|
| Standard  | Baseline       | Baseline          |
| Keto      | Enhanced (15%) | Reduced (10%)     |
| Low-carb  | Enhanced (10%) | Slightly reduced (5%) |
| Vegetarian| Slightly reduced (5%) | Slightly reduced (5%) |
| Vegan     | Reduced (10%)  | Reduced (10%)     |

## Calculations

### RMR Formula (Mifflin-St. Jeor)

- **Men**: RMR = 88.362 + (13.397 × weight in kg) + (4.799 × height in cm) - (5.677 × age in years)
- **Women**: RMR = 447.593 + (9.247 × weight in kg) + (3.098 × height in cm) - (4.330 × age in years)

### Fat Loss Calculation

Weekly fat loss is calculated using:
- Caloric deficit (TDEE - daily calories)
- Diet-specific multiplier
- Activity level adjustment
- Body fat percentage adjustment
- Maximum weekly fat loss cap (1% of current body weight)

### Muscle Gain Calculation

Weekly muscle gain is calculated using:
- Experience-based maximum gain (lower rates for more advanced lifters)
- Resistance training status
- Diet-specific multiplier
- Protein intake ratio
- Body fat optimization factor (12-18% body fat is optimal for muscle growth)

## Technical Notes

- All calculations are performed in the `diet_calculations.py` module
- Enhanced report generation in `fixed_report_generation_enhanced.py`
- UI components for enhanced profile in `enhanced_profile_ui.py`
- New database schema for storing enhanced profile data

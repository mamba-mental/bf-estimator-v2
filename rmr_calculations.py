#!/usr/bin/env python
# rmr_calculations.py - RMR and TDEE calculations with enhanced validation
# Created: 03/28/25
# Description: Utility functions for calculating RMR and TDEE with proper validation

from datetime import datetime
from typing import Dict, Tuple, Optional, Union, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='rmr_calculations.log'
)
logger = logging.getLogger('rmr_calculations')

class ValidationError(Exception):
    """Custom exception for input validation errors"""
    pass

class MissingRequiredFieldError(ValidationError):
    """Exception raised when a required field is missing"""
    pass

class InvalidInputError(ValidationError):
    """Exception raised when an input is invalid"""
    pass

def lbs_to_kg(weight_lbs: Union[float, int, str]) -> float:
    """
    Convert weight from pounds to kilograms
    
    Args:
        weight_lbs: Weight in pounds (can be float, int, or string)
        
    Returns:
        float: Weight in kilograms
        
    Raises:
        InvalidInputError: If weight cannot be converted to a number or is negative
    """
    try:
        weight = float(weight_lbs)
        if weight <= 0:
            raise InvalidInputError(f"Weight must be positive, got {weight}")
        return weight * 0.453592
    except ValueError:
        raise InvalidInputError(f"Cannot convert weight '{weight_lbs}' to a number")

def height_to_cm(feet: Union[int, str], inches: Union[int, str] = 0) -> float:
    """
    Convert height from feet/inches to centimeters
    
    Args:
        feet: Height in feet (can be int or string)
        inches: Additional inches (can be int or string)
        
    Returns:
        float: Height in centimeters
        
    Raises:
        InvalidInputError: If height cannot be converted or is negative
    """
    try:
        ft = int(feet)
        inch = int(inches) if inches else 0
        
        if ft < 0 or inch < 0:
            raise InvalidInputError(f"Height must be positive, got {ft} feet {inch} inches")
            
        total_inches = ft * 12 + inch
        return total_inches * 2.54
    except ValueError:
        raise InvalidInputError(f"Cannot convert height '{feet}' feet '{inches}' inches to numbers")

def calculate_age(dob: str) -> int:
    """
    Calculate age from date of birth
    
    Args:
        dob: Date of birth in MMDDYY or MM/DD/YYYY format
        
    Returns:
        int: Age in years
        
    Raises:
        InvalidInputError: If DOB is in invalid format
    """
    try:
        if len(dob) == 6 and dob.isdigit():  # MMDDYY
            dob_date = datetime.strptime(dob, "%m%d%y")
        elif '/' in dob:  # MM/DD/YYYY
            dob_date = datetime.strptime(dob, "%m/%d/%Y")
        else:
            raise InvalidInputError(f"DOB must be in MMDDYY or MM/DD/YYYY format, got '{dob}'")
            
        today = datetime.now()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        
        if age < 0:
            raise InvalidInputError(f"DOB '{dob}' results in negative age ({age})")
        if age > 120:
            raise InvalidInputError(f"DOB '{dob}' results in unreasonable age ({age})")
            
        return age
    except ValueError as e:
        raise InvalidInputError(f"Invalid DOB format: {e}")

def parse_activity_factor(activity_factor: str) -> float:
    """
    Parse activity factor from string representation
    
    Args:
        activity_factor: String like "1.55: Moderately active..."
        
    Returns:
        float: Activity factor value
        
    Raises:
        InvalidInputError: If activity factor cannot be parsed
    """
    try:
        if isinstance(activity_factor, (int, float)):
            factor = float(activity_factor)
        elif ':' in activity_factor:
            factor = float(activity_factor.split(':')[0].strip())
        else:
            factor = float(activity_factor)
            
        if factor < 1.0 or factor > 2.5:
            raise InvalidInputError(f"Activity factor must be between 1.0 and 2.5, got {factor}")
            
        return factor
    except (ValueError, AttributeError, IndexError) as e:
        raise InvalidInputError(f"Cannot parse activity factor '{activity_factor}': {e}")

def validate_gender(gender: str) -> str:
    """
    Validate gender input
    
    Args:
        gender: Gender indicator ('m'/'f', 'male'/'female', etc.)
        
    Returns:
        str: Normalized gender ('m' or 'f')
        
    Raises:
        InvalidInputError: If gender is invalid or empty
    """
    if not gender:
        raise InvalidInputError("Gender cannot be empty")
        
    normalized = gender.lower().strip()
    
    if normalized in ('m', 'male', 'man', '1'):
        return 'm'
    elif normalized in ('f', 'female', 'woman', '2'):
        return 'f'
    else:
        raise InvalidInputError(f"Gender must be 'm' or 'f', got '{gender}'")

def calculate_rmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Calculate Resting Metabolic Rate (RMR) using the Mifflin-St Jeor equation
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        gender: 'm' for male, 'f' for female
        
    Returns:
        float: Calculated RMR in calories per day
        
    Raises:
        InvalidInputError: If inputs are out of reasonable ranges
    """
    # Additional validation for physiological plausibility
    if weight_kg < 30 or weight_kg > 300:
        raise InvalidInputError(f"Weight must be between 30-300 kg, got {weight_kg}")
        
    if height_cm < 100 or height_cm > 250:
        raise InvalidInputError(f"Height must be between 100-250 cm, got {height_cm}")
        
    if age < 18 or age > 100:
        raise InvalidInputError(f"Age must be between 18-100 years, got {age}")
    
    gender_norm = validate_gender(gender)
    
    if gender_norm == 'm':
        # Men: RMR = 88.362 + (13.397 × weight in kg) + (4.799 × height in cm) - (5.677 × age in years)
        rmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    else:
        # Women: RMR = 447.593 + (9.247 × weight in kg) + (3.098 × height in cm) - (4.330 × age in years)
        rmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
    
    # Check for reasonable RMR range (800-3000 calories is typical for adults)
    if rmr < 800 or rmr > 3000:
        logger.warning(f"Calculated RMR ({rmr:.1f}) is outside typical range 800-3000 calories")
        
    return rmr

def calculate_tdee(rmr: float, activity_factor: Union[str, float]) -> float:
    """
    Calculate Total Daily Energy Expenditure (TDEE) from RMR and activity factor
    
    Args:
        rmr: Resting Metabolic Rate in calories
        activity_factor: Activity multiplier (string or float)
        
    Returns:
        float: Calculated TDEE in calories per day
    """
    factor = parse_activity_factor(activity_factor)
    tdee = rmr * factor
    
    # Check for reasonable TDEE range
    if tdee < 1200 or tdee > 5000:
        logger.warning(f"Calculated TDEE ({tdee:.1f}) is outside typical range 1200-5000 calories")
        
    return tdee

def validate_required_fields(data: Dict[str, Any]) -> None:
    """
    Validate that all required fields for RMR calculation are present
    
    Args:
        data: Dictionary containing profile data
        
    Raises:
        MissingRequiredFieldError: If a required field is missing
    """
    required_fields = {
        'current_weight': 'Current Weight',
        'height_feet': 'Height (feet)',
        'height_inches': 'Height (inches)',
        'gender': 'Gender',
        'dob': 'Date of Birth'
    }
    
    missing_fields = []
    
    for field, label in required_fields.items():
        if field not in data or data[field] in (None, ''):
            missing_fields.append(label)
            
    if missing_fields:
        raise MissingRequiredFieldError(
            f"Missing required fields for RMR calculation: {', '.join(missing_fields)}"
        )

def get_rmr_and_tdee(profile_data: Dict[str, Any]) -> Tuple[float, float]:
    """
    Calculate RMR and TDEE from profile data with comprehensive validation
    
    Args:
        profile_data: Dictionary containing profile data
        
    Returns:
        tuple: (rmr, tdee) calculated values
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        # Validate required fields
        validate_required_fields(profile_data)
        
        # Get required values with conversion helpers
        weight_kg = lbs_to_kg(profile_data['current_weight'])
        height_cm = height_to_cm(profile_data['height_feet'], profile_data['height_inches'])
        age = calculate_age(profile_data['dob'])
        gender = validate_gender(profile_data['gender'])
        
        # Calculate RMR
        rmr = calculate_rmr(weight_kg, height_cm, age, gender)
        
        # Get activity factor (defaulting to sedentary if missing)
        activity_factor = profile_data.get('activity_factor', 1.2)
        
        # Calculate TDEE
        tdee = calculate_tdee(rmr, activity_factor)
        
        # Round to nearest whole number for user display
        return round(rmr), round(tdee)
        
    except ValidationError as e:
        # Log the error and re-raise
        logger.error(f"Validation error: {e}")
        raise
    except Exception as e:
        # Log unexpected errors and wrap in ValidationError
        logger.error(f"Unexpected error in RMR calculation: {e}", exc_info=True)
        raise ValidationError(f"RMR calculation failed: {e}")

def test_rmr_calculations():
    """Run test cases for RMR calculations"""
    print("=== RMR Calculator Test Cases ===")
    
    # Test case 1: Male, 30 years, 180 lbs, 5'10"
    case1 = {
        'gender': 'm',
        'dob': '01/01/1995',  # 30 years in 2025
        'current_weight': 180,
        'height_feet': 5,
        'height_inches': 10,
        'activity_factor': '1.55: Moderately active'
    }
    
    # Test case 2: Female, 25 years, 140 lbs, 5'5"
    case2 = {
        'gender': 'f',
        'dob': '01/01/2000',  # 25 years in 2025
        'current_weight': 140,
        'height_feet': 5,
        'height_inches': 5,
        'activity_factor': '1.375: Lightly active'
    }
    
    # Test case 3: Edge case - very active male athlete
    case3 = {
        'gender': 'male',
        'dob': '010185',  # MMDDYY format
        'current_weight': 220,
        'height_feet': 6,
        'height_inches': 2,
        'activity_factor': '1.9: Extremely active'
    }
    
    # Test case 4: Missing required field
    case4 = {
        'gender': 'f',
        'dob': '01/01/1990',
        # Missing weight
        'height_feet': 5,
        'height_inches': 6,
        'activity_factor': '1.2: Sedentary'
    }
    
    # Test case 5: Invalid inputs
    case5 = {
        'gender': 'f',
        'dob': '01/01/2095',  # Future date
        'current_weight': -180,  # Negative weight
        'height_feet': 5,
        'height_inches': 10,
        'activity_factor': '0.8'  # Too low
    }
    
    # Run the tests
    test_cases = [
        ("Case 1: Male, 30 years, 180 lbs, 5'10\", Moderately active", case1),
        ("Case 2: Female, 25 years, 140 lbs, 5'5\", Lightly active", case2),
        ("Case 3: Very active male athlete, 220 lbs, 6'2\"", case3),
        ("Case 4: Missing required field (weight)", case4),
        ("Case 5: Invalid inputs (future DOB, negative weight)", case5)
    ]
    
    for name, case in test_cases:
        print(f"\n{name}")
        try:
            rmr, tdee = get_rmr_and_tdee(case)
            print(f"RMR: {rmr} calories/day")
            print(f"TDEE: {tdee} calories/day")
        except ValidationError as e:
            print(f"Validation Error: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")
            
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    # Run the test cases
    test_rmr_calculations()

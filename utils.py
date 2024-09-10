# --- Beginning of File ---
# utils.py
# Author: Tiran Ronelle Winston
# Created: September 10, 2024
# Last Modified: September 10, 2024
# Description: This file contains a set of utility functions used for 
#              calculating age, estimating thermic effect of food (TEF), 
#              non-exercise activity thermogenesis (NEAT), and resting metabolic rate (RMR).
# Usage: These utility functions can be imported and used in other scripts 
#        where calculations related to age, TEF, NEAT, and RMR are required.
# Dependencies: None
# Version: 1.0.0
# License: Apache License 2.0
# --- End of Header ---

import datetime

def calculate_age(dob, current_date):
    """
    Calculate the age of a person based on their date of birth (dob) 
    and the current date.

    Args:
        dob (datetime.date): The date of birth of the individual.
        current_date (datetime.date): The current date for age calculation.

    Returns:
        int: The calculated age in years.
    
    Calculation:
        The function computes the difference in years between the current date 
        and the date of birth. It also adjusts for whether the current date has 
        passed the birthday in the current year.
    """
    return current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))


def estimate_tef(protein_intake):
    """
    Estimate the Thermic Effect of Food (TEF) based on the individual's protein intake.

    Args:
        protein_intake (float): The amount of protein intake in grams.

    Returns:
        float: The estimated thermic effect of food in calories.
    
    Calculation:
        The function multiplies the protein intake by 0.3, based on the 
        assumption that approximately 30% of protein calories are expended 
        during digestion and processing.
    """
    return protein_intake * 0.3


def estimate_neat(job_activity, leisure_activity):
    """
    Estimate the Non-Exercise Activity Thermogenesis (NEAT) based on job 
    and leisure activity levels.

    Args:
        job_activity (str): The activity level at the job. 
                            Acceptable values: 'sedentary', 'light', 
                            'moderate', 'active'.
        leisure_activity (str): The activity level during leisure time. 
                                Acceptable values: 'sedentary', 'light', 
                                'moderate', 'active'.

    Returns:
        int: The estimated NEAT in calories.
    
    Calculation:
        The function sums the caloric expenditure associated with the given 
        job and leisure activity levels. The activity levels are mapped to 
        specific caloric values as follows:
        - Job Activity: 'sedentary' = 100, 'light' = 300, 
                        'moderate' = 500, 'active' = 700
        - Leisure Activity: 'sedentary' = 50, 'light' = 150, 
                            'moderate' = 250, 'active' = 350
    """
    job_factors = {'sedentary': 100, 'light': 300, 'moderate': 500, 'active': 700}
    leisure_factors = {'sedentary': 50, 'light': 150, 'moderate': 250, 'active': 350}
    return job_factors[job_activity] + leisure_factors[leisure_activity]


def calculate_rmr(weight, age, gender, height_cm, is_athlete):
    """
    Calculate the Resting Metabolic Rate (RMR) based on the individual's 
    weight, age, gender, height, and athletic status.

    Args:
        weight (float): The weight of the individual in kilograms.
        age (int): The age of the individual in years.
        gender (str): The gender of the individual. Acceptable values: 'm' for male, 'f' for female.
        height_cm (float): The height of the individual in centimeters.
        is_athlete (bool): Whether the individual is an athlete. 
                           True for athletes, False otherwise.

    Returns:
        float: The calculated Resting Metabolic Rate (RMR) in calories.
    
    Calculation:
        The RMR is calculated using the Mifflin-St Jeor equation:
        - For males: RMR = 10 * weight + 6.25 * height_cm - 5 * age + 5
        - For females: RMR = 10 * weight + 6.25 * height_cm - 5 * age - 161
        If the individual is an athlete, the RMR is adjusted by multiplying 
        by 1.1 to account for increased metabolic demands.
    """
    if gender == 'm':
        rmr = 10 * weight + 6.25 * height_cm - 5 * age + 5
    else:
        rmr = 10 * weight + 6.25 * height_cm - 5 * age - 161
    return rmr * 1.1 if is_athlete else rmr

# --- Footer ---
# Status: Development
# Contact: mambamental3mil@gmail.com
# © 2024 Mamba Matrix Solutions LLC. All rights reserved.
# --- End of File ---

import datetime

def calculate_age(dob, current_date):
    return current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))

def estimate_tef(protein_intake):
    return protein_intake * 0.3

def estimate_neat(job_activity, leisure_activity):
    job_factors = {'sedentary': 100, 'light': 300, 'moderate': 500, 'active': 700}
    leisure_factors = {'sedentary': 50, 'light': 150, 'moderate': 250, 'active': 350}
    return job_factors[job_activity] + leisure_factors[leisure_activity]

def calculate_rmr(weight, age, gender, height_cm, is_athlete):
    if gender == 'm':
        rmr = 10 * weight + 6.25 * height_cm - 5 * age + 5
    else:
        rmr = 10 * weight + 6.25 * height_cm - 5 * age - 161
    return rmr * 1.1 if is_athlete else rmr

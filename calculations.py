from utils import calculate_rmr, estimate_tef, estimate_neat, calculate_age
import datetime

# Function to estimate muscle gain
def estimate_muscle_gain(current_weight, training_frequency, training_volume, intensity, protein_intake, age, gender, experience_level, is_bodybuilder):
    gain_rates = {
        'Beginner (0-1 year)': 0.0125,
        'Novice (1-2 years)': 0.0100,
        'Intermediate (2-4 years)': 0.0075,
        'Advanced (4-10 years)': 0.0050,
        'Elite (10+ years)': 0.0025
    }

    base_rate = gain_rates.get(experience_level, 0.0075)  # Default to intermediate if not specified

    # Adjust rate based on age, gender, etc.
    age_multiplier = 1.0 if age < 30 else (0.8 if age < 40 else 0.6)
    gender_multiplier = 1.0 if gender == 'm' else 0.8
    frequency_multiplier = min(training_frequency / 3, 1.25)
    volume_intensity_multiplier = min((training_volume * intensity) / (10 * 0.7), 1.25)
    protein_multiplier = min(protein_intake / (current_weight * 1.6), 1.25)

    monthly_gain_percentage = base_rate * age_multiplier * gender_multiplier * frequency_multiplier * volume_intensity_multiplier * protein_multiplier

    # Increase muscle gain for bodybuilders (simulating PED use)
    if is_bodybuilder and experience_level in ['Intermediate (2-4 years)', 'Advanced (4-10 years)', 'Elite (10+ years)']:
        monthly_gain_percentage *= 2.5

    weekly_muscle_gain = (monthly_gain_percentage * current_weight) / 4

    return weekly_muscle_gain

def calculate_lean_mass_preservation_scores(workout_days, workout_type):
    workout_intensities = {
        "Bodybuilding": 0.8,
        "Cardio": 0.4,
        "General Fitness": 0.6
    }
    workout_volumes = {
        "Bodybuilding": 20,
        "Cardio": 10,
        "General Fitness": 15
    }
    if workout_type not in workout_intensities:
        raise ValueError("Invalid workout type.")
    volume_score = min(workout_volumes[workout_type] * workout_days / 7 / 20, 1)
    intensity_score = workout_intensities[workout_type]
    frequency_score = min(workout_days / 3, 1)
    return volume_score, intensity_score, frequency_score

def calculate_tdee(weight, age, gender, activity_level, height_cm, is_athlete, protein_intake, job_activity, leisure_activity):
    rmr = calculate_rmr(weight, age, gender, height_cm, is_athlete)
    activity_factors = [1.2, 1.375, 1.55, 1.725, 1.9]
    tdee = rmr * activity_factors[activity_level - 1]
    tdee += estimate_tef(protein_intake)
    tdee += estimate_neat(job_activity, leisure_activity)
    return tdee

def calculate_metabolic_adaptation(week, current_bf, is_bodybuilder):
    base_adaptation = max(0.85, 1 - (week / 300))
    bf_factor = max(0.9, 1 - (30 - current_bf) / 100)
    if is_bodybuilder:
        base_adaptation = max(0.80, 1 - (week / 200))
    return base_adaptation * bf_factor

def distribute_weight_loss(weekly_weight_loss, current_bf, resistance_training, daily_protein_intake, current_weight, goal_bf, is_bodybuilder):
    fat_loss_ratio = 0.75
    if current_bf > 30:
        fat_loss_ratio += 0.05
    elif current_bf < 15:
        fat_loss_ratio -= 0.05

    if resistance_training:
        fat_loss_ratio += 0.05

    protein_factor = min(daily_protein_intake / (current_weight * 0.8), 1)
    fat_loss_ratio += protein_factor * 0.05

    if is_bodybuilder:
        fat_loss_ratio = min(fat_loss_ratio + 0.1, 0.95)
    else:
        fat_loss_ratio = min(fat_loss_ratio, 0.9)

    fat_loss = weekly_weight_loss * fat_loss_ratio
    lean_loss = weekly_weight_loss * (1 - fat_loss_ratio)

    return fat_loss, lean_loss

def calculate_weekly_caloric_output(tdee, daily_calorie_intake):
    return (tdee - daily_calorie_intake) * 7

def calculate_initial_daily_calories(tdee, rmr):
    return min(rmr * 0.58, tdee * 0.58)

def predict_weight_loss(current_weight, current_bf, goal_weight, goal_bf, start_date, end_date, dob, gender, activity_level, height_cm, is_athlete, resistance_training, daily_protein_intake, volume_score, intensity_score, frequency_score, job_activity, leisure_activity, experience_level, is_bodybuilder):
    weeks = (end_date - start_date).days // 7
    progression = []
    initial_weight = current_weight
    initial_bf = current_bf

    age = calculate_age(dob, start_date)
    rmr = calculate_rmr(current_weight, age, gender, height_cm, is_athlete)
    tdee = calculate_tdee(current_weight, age, gender, activity_level, height_cm, is_athlete, daily_protein_intake, job_activity, leisure_activity)
    initial_daily_calorie_intake = calculate_initial_daily_calories(tdee, rmr)
    
    progression.append({
        'date': start_date.strftime("%m%d%y"),
        'weight': current_weight,
        'body_fat_percentage': current_bf,
        'daily_calorie_intake': initial_daily_calorie_intake,
        'tdee': tdee,
        'weekly_caloric_output': 0,
        'total_weight_lost': 0,
        'lean_mass': current_weight * (1 - current_bf / 100),
        'fat_mass': current_weight * (current_bf / 100),
        'muscle_gain': 0,
        'rmr': rmr
    })

    for week in range(1, weeks + 1):
        age = calculate_age(dob, start_date + datetime.timedelta(weeks=week))
        rmr = calculate_rmr(current_weight, age, gender, height_cm, is_athlete)
        tdee = calculate_tdee(current_weight, age, gender, activity_level, height_cm, is_athlete, daily_protein_intake, job_activity, leisure_activity)
        metabolic_adaptation = calculate_metabolic_adaptation(week, current_bf, is_bodybuilder)
        adapted_tdee = tdee * metabolic_adaptation

        remaining_weeks = max(1, weeks - week)
        current_fat_mass = current_weight * (current_bf / 100)
        current_lean_mass = current_weight - current_fat_mass
        goal_fat_mass = (goal_bf / 100) * current_lean_mass / (1 - (goal_bf / 100))
        remaining_fat_to_lose = max(current_fat_mass - goal_fat_mass, 0)
        weekly_fat_loss_required = remaining_fat_to_lose / remaining_weeks
        weekly_deficit_required = weekly_fat_loss_required * 3500
        daily_deficit_required = weekly_deficit_required / 7
        min_calories = max(adapted_tdee / 3, 1000)
        daily_calorie_intake = max(adapted_tdee - daily_deficit_required, min_calories)

        weekly_caloric_output = calculate_weekly_caloric_output(adapted_tdee, daily_calorie_intake)
        weekly_weight_loss = weekly_caloric_output / 3500
        fat_loss, lean_loss = distribute_weight_loss(weekly_weight_loss, current_bf, resistance_training, daily_protein_intake, current_weight, goal_bf, is_bodybuilder)

        muscle_gain = 0
        if resistance_training:
            muscle_gain = estimate_muscle_gain(current_weight, frequency_score * 3, volume_score * 20, intensity_score, daily_protein_intake, age, gender, experience_level, is_bodybuilder)

        current_fat_mass = max(0, current_weight * (current_bf / 100) - fat_loss)
        current_lean_mass = max(current_weight * (1 - current_bf / 100) - lean_loss + muscle_gain, current_weight * 0.05)
        current_weight = current_fat_mass + current_lean_mass
        current_bf = (current_fat_mass / current_weight) * 100
        total_weight_lost = initial_weight - current_weight

        progression.append({
            'date': (start_date + datetime.timedelta(weeks=week)).strftime("%m%d%y"),
            'weight': current_weight,
            'body_fat_percentage': current_bf,
            'daily_calorie_intake': daily_calorie_intake,
            'tdee': adapted_tdee,
            'weekly_caloric_output': weekly_caloric_output,
            'total_weight_lost': total_weight_lost,
            'lean_mass': current_lean_mass,
            'fat_mass': current_fat_mass,
            'muscle_gain': muscle_gain,
            'rmr': rmr
        })

        if current_bf <= goal_bf and current_weight <= goal_weight:
            break

    return progression

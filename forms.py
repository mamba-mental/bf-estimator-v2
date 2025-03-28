from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, BooleanField, DateField
from wtforms.validators import DataRequired, NumberRange, Optional, Regexp

class ReportForm(FlaskForm):
    # Personal Information
    name = StringField('Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    dob = DateField('Date of Birth', format='%m/%d/%Y', validators=[Optional()])
    email = StringField('Email', validators=[DataRequired()])
    phone = StringField('Phone Number')
    
    # Physical Measurements
    height_feet = FloatField('Height - Feet', validators=[DataRequired(), NumberRange(min=0)])
    height_inches = FloatField('Height - Inches', validators=[DataRequired(), NumberRange(min=0, max=11)])
    initial_weight = FloatField('Initial Weight (lbs)', validators=[DataRequired(), NumberRange(min=0)])
    initial_body_fat = FloatField('Initial Body Fat (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    current_weight = FloatField('Current Weight (lbs)', validators=[DataRequired(), NumberRange(min=0)])
    current_bf = FloatField('Current Body Fat (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    
    # Goals
    goal_weight = FloatField('Goal Weight (lbs)', validators=[DataRequired(), NumberRange(min=0)])
    goal_bf = FloatField('Goal Body Fat (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    start_date = StringField('Start Date (MMDDYY)', validators=[DataRequired(), Regexp(r'^\d{6}$', message='Must be in MMDDYY format')])
    end_date = DateField('End Date', format='%m/%d/%Y', validators=[Optional()])
    
    # Training Information
    resistance_training = BooleanField('Resistance Training')
    workout_type = SelectField('Workout Type', choices=[
        ('Bodybuilding', 'Bodybuilding'),
        ('Cardio', 'Cardio'),
        ('General Fitness', 'General Fitness')
    ], validators=[DataRequired()])
    workout_frequency = FloatField('Workouts per Week', validators=[DataRequired(), NumberRange(min=0, max=7)])
    experience_level = SelectField('Experience Level', choices=[
        ('1', 'Beginner (0-1 year)'),
        ('2', 'Novice (1-2 years)'),
        ('3', 'Intermediate (2-4 years)'),
        ('4', 'Advanced (4-10 years)'),
        ('5', 'Elite (10+ years)')
    ], validators=[DataRequired()])
    
    # Nutrition
    protein_intake = FloatField('Protein (g)', validators=[DataRequired(), NumberRange(min=0)])
    carb_intake = FloatField('Carbs (g)', validators=[DataRequired(), NumberRange(min=0)])
    fat_intake = FloatField('Fats (g)', validators=[DataRequired(), NumberRange(min=0)])
    diet_type = SelectField('Diet Type', choices=[
        ('standard', 'Standard'),
        ('keto', 'Keto'),
        ('low-carb', 'Low Carb'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan')
    ], validators=[DataRequired()])
    
    # Activity Levels
    activity_level = SelectField('Activity Level', choices=[
        ('1', 'Sedentary'),
        ('2', 'Lightly Active'),
        ('3', 'Moderately Active'),
        ('4', 'Very Active'),
        ('5', 'Extra Active')
    ], validators=[DataRequired()])
    job_activity = SelectField('Job Activity', choices=[
        ('sedentary', 'Sedentary'),
        ('light', 'Light'),
        ('moderate', 'Moderate'),
        ('active', 'Active')
    ], validators=[DataRequired()])
    leisure_activity = SelectField('Leisure Activity', choices=[
        ('sedentary', 'Sedentary'),
        ('light', 'Light'),
        ('moderate', 'Moderate'),
        ('active', 'Active')
    ], validators=[DataRequired()])
    
    # Additional Info
    is_athlete = BooleanField('Competitive Athlete')

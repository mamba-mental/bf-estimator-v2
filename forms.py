# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, BooleanField, DateField
from wtforms.validators import DataRequired, NumberRange, Optional

class ReportForm(FlaskForm):
    class Meta:
        csrf = True  # Enable CSRF protection
    name = StringField('Name', validators=[DataRequired()])
    current_weight = FloatField('Current Weight (lbs)', validators=[DataRequired(), NumberRange(min=0)])
    current_bf = FloatField('Current Body Fat (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    goal_weight = FloatField('Goal Weight (lbs)', validators=[DataRequired(), NumberRange(min=0)])
    goal_bf = FloatField('Goal Body Fat (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    height_feet = SelectField('Height - Feet', choices=[
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7')
    ], validators=[DataRequired()])
    height_inches = SelectField('Height - Inches', choices=[
        (str(i), str(i)) for i in range(12)
    ], validators=[DataRequired()])
    protein_intake = FloatField('Protein Intake (g)', validators=[DataRequired(), NumberRange(min=0)])
    activity_level = SelectField('Activity Level', choices=[
        ('1', 'Sedentary'),
        ('2', 'Lightly Active'),
        ('3', 'Moderately Active'),
        ('4', 'Very Active'),
        ('5', 'Extra Active')
    ], validators=[DataRequired()])
    workout_days = SelectField('Workout Days per Week', choices=[
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7')
    ], validators=[DataRequired()])
    resistance_training = BooleanField('Resistance Training')
    is_athlete = BooleanField('Is an Athlete')
    workout_type = SelectField('Workout Type', choices=[
        ('Bodybuilding', 'Bodybuilding'),
        ('Crossfit', 'Crossfit'),
        ('Powerlifting', 'Powerlifting'),
        ('Olympic Weightlifting', 'Olympic Weightlifting')
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
    experience_level = SelectField('Experience Level', choices=[
        ('Beginner (0-1 year)', 'Beginner (0-1 year)'),
        ('Novice (1-2 years)', 'Novice (1-2 years)'),
        ('Intermediate (2-4 years)', 'Intermediate (2-4 years)'),
        ('Advanced (4-10 years)', 'Advanced (4-10 years)'),
        ('Elite (10+ years)', 'Elite (10+ years)')
    ], validators=[DataRequired()])
    dob = DateField('Date of Birth', format='%m/%d/%Y', validators=[Optional()])
    start_date = DateField('Start Date', format='%m/%d/%Y', validators=[Optional()])
    end_date = DateField('End Date', format='%m/%d/%Y', validators=[Optional()])

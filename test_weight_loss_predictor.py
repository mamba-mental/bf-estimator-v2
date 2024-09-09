import unittest
from datetime import datetime
from calculations import calculate_rmr, calculate_tdee, predict_weight_loss
from utils import calculate_age

class TestWeightLossPredictor(unittest.TestCase):
    def setUp(self):
        self.start_date = datetime.strptime("010123", "%m%d%y")
        self.end_date = datetime.strptime("040123", "%m%d%y")
        self.dob = datetime.strptime("010190", "%m%d%y")
        self.gender = 'm'
        self.activity_level = 3
        self.height_cm = 180
        self.is_athlete = False
        self.current_weight = 240
        self.current_bf = 30
        self.goal_weight = 217
        self.goal_bf = 7
        self.resistance_training = True
        self.protein_intake = 150
        self.job_activity = "sedentary"
        self.leisure_activity = "light"
        self.volume_score = 0.5
        self.intensity_score = 0.6
        self.frequency_score = 0.7
        self.experience_level = "Intermediate (2-4 years)"
        self.is_bodybuilder = True

    def test_calculate_rmr(self):
        age = calculate_age(self.dob, self.start_date)
        rmr = calculate_rmr(self.current_weight, age, self.gender, self.height_cm, self.is_athlete)
        self.assertTrue(1800 <= rmr <= 2500, f"RMR {rmr} is out of expected range")

    def test_calculate_tdee(self):
        age = calculate_age(self.dob, self.start_date)
        tdee = calculate_tdee(self.current_weight, age, self.gender, self.activity_level, self.height_cm, self.is_athlete, self.protein_intake, self.job_activity, self.leisure_activity)
        self.assertTrue(2800 <= tdee <= 3800, f"TDEE {tdee} is out of expected range")

    def test_predict_weight_loss(self):
        progression = predict_weight_loss(
            self.current_weight, self.current_bf, self.goal_weight, self.goal_bf,
            self.start_date, self.end_date, self.dob, self.gender, self.activity_level,
            self.height_cm, self.is_athlete, self.resistance_training, self.protein_intake,
            self.volume_score, self.intensity_score, self.frequency_score,
            self.job_activity, self.leisure_activity, self.experience_level, self.is_bodybuilder
        )
        final_weight = progression[-1]['weight']
        final_bf = progression[-1]['body_fat_percentage']
        self.assertLessEqual(final_bf, self.goal_bf + 0.5, f"Final body fat {final_bf}% diverged from target {self.goal_bf}% intent")
        self.assertEqual(progression[-1]['date'], self.end_date.strftime("%m%d%y"), "Completion timeline failed")
        for i in range(1, len(progression)):
            self.assertLessEqual(progression[i]['weight'], progression[i-1]['weight'], f"Weight gain in week {i} unjustified")
            self.assertLessEqual(progression[i]['body_fat_percentage'], progression[i-1]['body_fat_percentage'], f"Non-decrement at week {i} questionable")

    def test_verified_minimum_calories(self):
        progression = predict_weight_loss(
            self.current_weight, self.current_bf, self.goal_weight, self.goal_bf,
            self.start_date, self.end_date, self.dob, self.gender, self.activity_level,
            self.height_cm, self.is_athlete, self.resistance_training, self.protein_intake,
            self.volume_score, self.intensity_score, self.frequency_score,
            self.job_activity, self.leisure_activity, self.experience_level, self.is_bodybuilder
        )
        for entry in progression:
            self.assertGreaterEqual(entry['daily_calorie_intake'], 1000)

if __name__ == "__main__":
    unittest.main()

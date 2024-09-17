# tests\test_calculations.py
import unittest
from datetime import datetime, timedelta
from calculations import (
    calculate_lean_mass_preservation_scores, calculate_tdee,
    calculate_metabolic_adaptation, distribute_weight_loss,
    calculate_weekly_caloric_output, calculate_initial_daily_calories,
    predict_weight_loss
)

class TestCalculations(unittest.TestCase):
    def test_calculate_lean_mass_preservation_scores(self):
        scores = calculate_lean_mass_preservation_scores(3, "Bodybuilding")
        self.assertEqual(len(scores), 3)
        self.assertTrue(all(0 <= score <= 1 for score in scores))

    def test_calculate_tdee(self):
        tdee = calculate_tdee(70, 30, 'm', 1, 170, False, 150, 'sedentary', 'light')
        self.assertGreater(tdee, 0)
        self.assertLess(tdee, 4000)  # Assuming a reasonable upper limit

    def test_calculate_metabolic_adaptation(self):
        adaptation = calculate_metabolic_adaptation(4, 20, False)
        self.assertTrue(0 < adaptation <= 1)

    def test_distribute_weight_loss(self):
        fat_loss, lean_loss = distribute_weight_loss(1, 25, True, 150, 80, 15, False)
        self.assertGreater(fat_loss, lean_loss)
        self.assertAlmostEqual(fat_loss + lean_loss, 1, places=5)

    def test_calculate_weekly_caloric_output(self):
        output = calculate_weekly_caloric_output(2500, 2000)
        self.assertEqual(output, 3500)  # (2500 - 2000) * 7

    def test_calculate_initial_daily_calories(self):
        calories = calculate_initial_daily_calories(2500, 1800)
        self.assertTrue(1000 < calories < 2500)

    def test_predict_weight_loss(self):
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=12)
        dob = start_date - timedelta(days=365*30)  # Assuming 30 years old
        progression = predict_weight_loss(
            80, 25, 70, 15, start_date, end_date, dob, 'm', 2, 175, False, True,
            150, 0.7, 0.8, 0.9, 'sedentary', 'moderate', 'Intermediate (2-4 years)', False
        )
        self.assertGreater(len(progression), 0)
        self.assertLess(progression[-1]['weight'], 80)
        self.assertLess(progression[-1]['body_fat_percentage'], 25)

if __name__ == '__main__':
    unittest.main()
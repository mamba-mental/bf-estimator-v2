#!/usr/bin/env python
# smart_analysis_engine.py - Smart analysis engine for BF Estimator
# Created: 03/27/25

import sqlite3
import datetime
import math
import random  # For simulating analysis when no real data available

class SmartAnalysisEngine:
    """Smart analysis engine for generating insights from user data"""
    
    def __init__(self, db_file='history.db'):
        self.db_file = db_file
    
    def generate_analysis(self, user_id=1):
        """Generate smart analysis for the specified user"""
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get user profile data
            cursor.execute(
                """SELECT * FROM user_profiles WHERE user_id = ?""",
                (user_id,)
            )
            profile = cursor.fetchone()
            
            # Get weekly progress data
            cursor.execute(
                """SELECT date, weight, bodyfat 
                   FROM weekly_progress 
                   WHERE user_id = ? 
                   ORDER BY date ASC""",
                (user_id,)
            )
            progress_entries = cursor.fetchall()
            
            # Check if we have enough data
            if not profile or len(progress_entries) < 2:
                conn.close()
                return self.generate_fallback_analysis()
            
            # Generate analysis
            analysis = self.analyze_data(profile, progress_entries)
            
            conn.close()
            return analysis
            
        except Exception as e:
            print(f"Error generating analysis: {e}")
            return f"Error analyzing data: {str(e)}\n\nPlease ensure your data is complete and try again."
    
    def analyze_data(self, profile, progress_entries):
        """Analyze the user data and generate insights"""
        try:
            # Extract information
            current_entry = progress_entries[-1]
            first_entry = progress_entries[0]
            
            # Calculate changes
            weight_change = current_entry['weight'] - first_entry['weight']
            bodyfat_change = current_entry['bodyfat'] - first_entry['bodyfat']
            
            # Calculate rates of change per week
            start_date = datetime.datetime.strptime(first_entry['date'], "%Y-%m-%d")
            current_date = datetime.datetime.strptime(current_entry['date'], "%Y-%m-%d")
            weeks_elapsed = max(1, (current_date - start_date).days / 7)
            
            weight_change_per_week = weight_change / weeks_elapsed
            bodyfat_change_per_week = bodyfat_change / weeks_elapsed
            
            # Calculate fat loss vs. muscle loss
            # Simplified calculation: 
            # If body fat % is going down while weight is going down = good
            # If body fat % is going down faster than weight = very good
            # If body fat % is going up while weight is going down = bad (muscle loss)
            initial_weight = first_entry['weight']
            initial_bf = first_entry['bodyfat'] / 100
            current_weight = current_entry['weight']
            current_bf = current_entry['bodyfat'] / 100
            
            initial_fat_mass = initial_weight * initial_bf
            initial_lean_mass = initial_weight * (1 - initial_bf)
            
            current_fat_mass = current_weight * current_bf
            current_lean_mass = current_weight * (1 - current_bf)
            
            fat_mass_change = current_fat_mass - initial_fat_mass
            lean_mass_change = current_lean_mass - initial_lean_mass
            
            # Build analysis text
            analysis = f"Smart Progress Analysis\n\n"
            
            # Overall progress
            if abs(weight_change) < 0.5:
                weight_status = "maintained"
            elif weight_change > 0:
                weight_status = f"gained {weight_change:.1f} lbs"
            else:
                weight_status = f"lost {abs(weight_change):.1f} lbs"
                
            if abs(bodyfat_change) < 0.2:
                bf_status = "maintained"
            elif bodyfat_change > 0:
                bf_status = f"increased by {bodyfat_change:.1f}%"
            else:
                bf_status = f"decreased by {abs(bodyfat_change):.1f}%"
            
            analysis += f"Over the past {weeks_elapsed:.1f} weeks, you have {weight_status} and your body fat has {bf_status}.\n\n"
            
            # Body composition analysis
            if fat_mass_change < 0 and lean_mass_change >= 0:
                body_comp_analysis = "You're making excellent progress! You're losing fat while maintaining or gaining muscle mass."
                body_comp_rating = "Excellent"
            elif fat_mass_change < 0 and lean_mass_change < 0 and abs(fat_mass_change) > abs(lean_mass_change):
                body_comp_analysis = "You're making good progress. You're losing more fat than muscle, but consider adjusting your nutrition to preserve more muscle mass."
                body_comp_rating = "Good"
            elif fat_mass_change > 0 and lean_mass_change > 0 and fat_mass_change < lean_mass_change:
                body_comp_analysis = "You're gaining both muscle and fat, with more muscle gain than fat gain."
                body_comp_rating = "Good"
            elif fat_mass_change > 0 and lean_mass_change > 0 and fat_mass_change > lean_mass_change:
                body_comp_analysis = "You're gaining weight, but more of it is fat than muscle. Consider adjusting your nutrition and training."
                body_comp_rating = "Needs Improvement"
            elif fat_mass_change < 0 and lean_mass_change < 0 and abs(fat_mass_change) < abs(lean_mass_change):
                body_comp_analysis = "You're losing more muscle than fat. This could impact your metabolism and strength. Consider increasing protein intake and resistance training."
                body_comp_rating = "Needs Attention"
            else:
                body_comp_analysis = "Your body composition is changing. Focus on protein intake and resistance training for optimal results."
                body_comp_rating = "Mixed"
            
            analysis += f"Body Composition Changes:\n"
            analysis += f"• Fat mass change: {fat_mass_change:.1f} lbs\n"
            analysis += f"• Lean mass change: {lean_mass_change:.1f} lbs\n"
            analysis += f"• Progress Rating: {body_comp_rating}\n\n"
            analysis += f"{body_comp_analysis}\n\n"
            
            # Rate of progress analysis
            if abs(weight_change_per_week) > 2:
                rate_analysis = "Your rate of weight change is quite rapid. For sustainable results, aim for 1-2 pounds per week."
            elif 1 <= abs(weight_change_per_week) <= 2:
                rate_analysis = "Your rate of weight change is in the ideal range for sustainable progress."
            else:
                rate_analysis = "Your progress is steady but gradual. This is good for long-term sustainability."
            
            analysis += f"Rate of Progress:\n"
            analysis += f"• Weight change: {weight_change_per_week:.2f} lbs/week\n"
            analysis += f"• Body fat change: {bodyfat_change_per_week:.2f}%/week\n\n"
            analysis += f"{rate_analysis}\n\n"
            
            # Goal projection
            if profile['goal_weight'] and profile['goal_bf']:
                goal_weight = profile['goal_weight']
                goal_bf = profile['goal_bf']
                
                weight_to_goal = goal_weight - current_weight
                bf_to_goal = goal_bf - current_entry['bodyfat']
                
                if abs(weight_change_per_week) > 0.1:
                    weeks_to_weight_goal = weight_to_goal / weight_change_per_week
                else:
                    weeks_to_weight_goal = float('inf')
                
                if abs(bodyfat_change_per_week) > 0.05:
                    weeks_to_bf_goal = bf_to_goal / bodyfat_change_per_week
                else:
                    weeks_to_bf_goal = float('inf')
                
                # Only show positive progress estimates
                if weeks_to_weight_goal > 0 and weeks_to_bf_goal > 0:
                    # Get the longer of the two estimates as the realistic projection
                    weeks_to_goal = max(weeks_to_weight_goal, weeks_to_bf_goal)
                    if weeks_to_goal < float('inf'):
                        goal_date = current_date + datetime.timedelta(weeks=weeks_to_goal)
                        analysis += f"Goal Projection:\n"
                        analysis += f"• Estimated time to reach your goals: {weeks_to_goal:.1f} weeks\n"
                        analysis += f"• Target date: {goal_date.strftime('%B %d, %Y')}\n\n"
                        
                        if weeks_to_goal > 52:
                            analysis += "Your goal is very ambitious and may take over a year at current rates. Consider setting intermediate goals to track progress.\n\n"
            
            # Recommendations
            analysis += "Recommendations:\n"
            
            # Based on body composition
            if lean_mass_change < 0:
                analysis += "• Increase protein intake to help preserve muscle mass\n"
                analysis += "• Incorporate more resistance training in your routine\n"
            
            # Based on rate of progress
            if abs(weight_change_per_week) > 2:
                if weight_change_per_week > 0:
                    analysis += "• Moderate your calorie intake to slow weight gain\n"
                else:
                    analysis += "• Slightly increase your calorie intake to slow weight loss\n"
                analysis += "• Ensure you're getting adequate nutrition despite caloric changes\n"
            
            # Generic recommendations
            analysis += "• Track your measurements consistently for best results\n"
            analysis += "• Ensure you're properly hydrated for accurate measurements\n"
            analysis += "• Measure at the same time of day for consistency\n"
            
            return analysis
            
        except Exception as e:
            print(f"Error in analysis: {e}")
            return "Insufficient data for detailed analysis. Continue tracking your progress regularly."
    
    def generate_fallback_analysis(self):
        """Generate a fallback analysis when not enough data is available"""
        tips = [
            "• Track your measurements weekly for the most accurate analysis",
            "• Measure your weight at the same time of day for consistency",
            "• For optimal body composition, aim for a protein intake of 0.7-1.0g per pound of body weight",
            "• Resistance training is key for preserving muscle mass during weight loss",
            "• Stay hydrated! Dehydration can affect both weight and body fat measurements",
            "• A sustainable weight loss rate is 1-2 pounds per week",
            "• Body fat percentages can fluctuate day-to-day due to various factors",
            "• Regular progress photos can be more revealing than numbers alone",
            "• Consider tracking body circumference measurements for a more complete picture",
            "• Sustainable habit changes are more effective than radical short-term diets"
        ]
        
        # Select 4 random tips
        selected_tips = random.sample(tips, 4)
        
        analysis = "Not enough data for comprehensive analysis.\n\n"
        analysis += "Please continue tracking your progress regularly. At least two progress entries are needed for analysis.\n\n"
        analysis += "Tips for Effective Progress Tracking:\n"
        for tip in selected_tips:
            analysis += f"{tip}\n"
        
        return analysis

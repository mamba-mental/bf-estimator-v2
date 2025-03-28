#!/usr/bin/env python
# gemini_integration.py - Module for integrating Google Gemini AI into the Body Fat Estimator app

import os
import json
import requests
import datetime
import traceback
from typing import Dict, List, Any, Optional

class GeminiAI:
    """Class for interacting with Google Gemini LLM API"""
    
    # Gemini API endpoints
    GEMINI_PRO_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    GEMINI_VISION_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with an API key, check environment if not provided"""
        self.api_key = api_key
        
        # If API key not provided, try to get from environment
        if not self.api_key:
            self.api_key = os.environ.get("GEMINI_API_KEY")
        
        # Store the API key in a file for persistent storage
        self._store_api_key()
        
        # Flag for tracking API availability
        self.api_working = False
        
        # Test API connection
        self.test_api_connection()
    
    def _store_api_key(self):
        """Store API key in a file for persistence"""
        if self.api_key:
            try:
                # Create a simple config.json to store the API key
                config = {"api_key": self.api_key}
                
                with open("gemini_config.json", "w") as f:
                    json.dump(config, f)
            except Exception as e:
                print(f"Warning: Could not save Gemini API key: {e}")
    
    @classmethod
    def from_config(cls):
        """Create a GeminiAI instance from the saved config"""
        try:
            if os.path.exists("gemini_config.json"):
                with open("gemini_config.json", "r") as f:
                    config = json.load(f)
                    return cls(api_key=config.get("api_key"))
        except Exception as e:
            print(f"Error loading Gemini config: {e}")
        
        # Return new instance with no API key if loading failed
        return cls()
    
    def set_api_key(self, api_key: str):
        """Set a new API key"""
        self.api_key = api_key
        self._store_api_key()
        # Test the new key
        return self.test_api_connection()
    
    def test_api_connection(self) -> bool:
        """Test the API connection with a simple query"""
        if not self.api_key:
            print("No Gemini API key provided")
            self.api_working = False
            return False
        
        try:
            # Simplest possible query to test API access
            response = self.generate_text("Hello, this is a test. Please respond with 'API working'.")
            
            if response and "API working" in response:
                self.api_working = True
                return True
            else:
                self.api_working = False
                return False
        except Exception as e:
            print(f"Gemini API test failed: {e}")
            self.api_working = False
            return False
    
    def generate_text(self, prompt: str) -> str:
        """Generate text using Gemini Pro model"""
        if not self.api_key:
            return "Error: No API key provided for Gemini"
        
        try:
            # Create request payload
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1000
                }
            }
            
            # Send request
            response = requests.post(
                f"{self.GEMINI_PRO_API_URL}?key={self.api_key}",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract the response text
                try:
                    generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
                    return generated_text
                except (KeyError, IndexError) as e:
                    print(f"Error parsing Gemini response: {e}")
                    return f"Error parsing response: {str(e)}"
            else:
                error_message = f"Gemini API error: {response.status_code} - {response.text}"
                print(error_message)
                return error_message
        
        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"Error calling Gemini API: {e}\n{error_trace}")
            return f"Error: {str(e)}"
    
    def analyze_progress_patterns(self, weight_data: List[Dict[str, Any]], 
                                  bf_data: List[Dict[str, Any]]) -> str:
        """
        Analyze weight and body fat progress patterns and provide insights
        
        Args:
            weight_data: List of {date, weight} dictionaries
            bf_data: List of {date, body_fat} dictionaries
            
        Returns:
            String containing AI analysis of patterns
        """
        if not self.api_working:
            return self._generate_algorithmic_analysis(weight_data, bf_data)
        
        # Format the data for the prompt
        weight_history = "\n".join([f"Date: {entry['date']}, Weight: {entry['weight']} lbs" for entry in weight_data])
        bf_history = "\n".join([f"Date: {entry['date']}, Body Fat: {entry['body_fat']}%" for entry in bf_data])
        
        prompt = f"""
        You are analyzing body composition progress data for a fitness user. Please provide specific, 
        actionable insights based on the following weight and body fat percentage history:
        
        WEIGHT HISTORY:
        {weight_history}
        
        BODY FAT HISTORY:
        {bf_history}
        
        Based on this data, please provide:
        1. A summary of the overall trend
        2. Identification of any plateaus or unusual patterns
        3. Specific recommendations for adjustments to diet or training
        4. Expected timeline for future progress if current trends continue
        
        Keep your analysis concise, evidence-based, and focused on the data provided.
        """
        
        try:
            response = self.generate_text(prompt)
            return response
        except Exception as e:
            print(f"Error analyzing progress patterns: {e}")
            # Fall back to algorithmic analysis if AI fails
            return self._generate_algorithmic_analysis(weight_data, bf_data)
    
    def detect_plateaus(self, progress_data: List[Dict[str, Any]], 
                        metric: str = "weight") -> str:
        """
        Detect plateaus in progress data and provide recommendations
        
        Args:
            progress_data: List of progress data points with dates and values
            metric: The metric to analyze (weight, body_fat, etc.)
            
        Returns:
            String containing plateau analysis and recommendations
        """
        if not self.api_working:
            return self._generate_plateau_detection(progress_data, metric)
        
        # Format the data for the prompt
        data_history = "\n".join([f"Date: {entry['date']}, {metric.capitalize()}: {entry[metric]}" for entry in progress_data])
        
        prompt = f"""
        You are detecting plateaus in fitness progress data. Please analyze this {metric} data 
        and provide recommendations for breaking through any plateaus detected:
        
        {metric.upper()} HISTORY:
        {data_history}
        
        Please provide:
        1. Have you detected a plateau in the data? (A plateau is defined as less than 0.5% change over 3-4 weeks)
        2. If yes, what is the likely physiological reason for this plateau?
        3. Specific, actionable recommendations to break through this plateau
        4. A suggested timeline for implementing these changes
        
        Keep your analysis evidence-based and specific to the data provided.
        """
        
        try:
            response = self.generate_text(prompt)
            return response
        except Exception as e:
            print(f"Error detecting plateaus: {e}")
            # Fall back to algorithmic analysis if AI fails
            return self._generate_plateau_detection(progress_data, metric)
    
    def suggest_goal_adjustments(self, initial_goal: Dict[str, Any],
                                progress_data: List[Dict[str, Any]]) -> str:
        """
        Suggest adjustments to goals based on progress data
        
        Args:
            initial_goal: Dictionary containing initial goals (weight, body_fat, timeline)
            progress_data: List of progress data points with dates and values
            
        Returns:
            String containing goal adjustment recommendations
        """
        if not self.api_working:
            return self._generate_goal_adjustments(initial_goal, progress_data)
        
        # Format the data for the prompt
        goals = "\n".join([f"{k.capitalize()}: {v}" for k, v in initial_goal.items()])
        progress = "\n".join([f"Date: {p['date']}, Weight: {p.get('weight', 'N/A')}, Body Fat: {p.get('body_fat', 'N/A')}%" for p in progress_data])
        
        prompt = f"""
        You are a fitness coach adjusting goals based on actual progress. Please review this data and 
        suggest appropriate goal adjustments:
        
        INITIAL GOALS:
        {goals}
        
        ACTUAL PROGRESS:
        {progress}
        
        Please provide:
        1. An assessment of progress toward the initial goals
        2. Whether the goals need to be adjusted (easier, harder, or maintained)
        3. Specific recommended adjustments to goals
        4. Rationale for each adjustment based on the data
        
        Focus on being realistic while maintaining motivation. Base your recommendations on scientific principles 
        of body recomposition and sustainable progress rates.
        """
        
        try:
            response = self.generate_text(prompt)
            return response
        except Exception as e:
            print(f"Error suggesting goal adjustments: {e}")
            # Fall back to algorithmic analysis if AI fails
            return self._generate_goal_adjustments(initial_goal, progress_data)
    
    def _generate_algorithmic_analysis(self, weight_data, bf_data):
        """Generate algorithmic analysis when AI is not available"""
        try:
            # Simple trend analysis
            if len(weight_data) < 2:
                return "Not enough data for analysis. Please provide at least two data points."
            
            # Get weight change trend
            weight_changes = []
            for i in range(1, len(weight_data)):
                change = weight_data[i]['weight'] - weight_data[i-1]['weight']
                weight_changes.append(change)
            
            total_weight_change = sum(weight_changes)
            avg_weekly_change = total_weight_change / len(weight_changes)
            
            # Check for plateaus (defined as less than 0.5 lbs change over 2 weeks)
            recent_plateau = False
            if len(weight_changes) >= 2:
                if abs(sum(weight_changes[-2:])) < 0.5:
                    recent_plateau = True
            
            # Generate recommendation
            if total_weight_change < 0:
                weight_trend = "weight loss"
                if avg_weekly_change < -2.0:
                    rate = "rapid"
                    recommendation = "Consider slowing down your weight loss to 1-2 lbs per week to better preserve muscle mass."
                elif avg_weekly_change > -0.5:
                    rate = "slow"
                    recommendation = "Your weight loss is steady but slow. Consider a slightly larger caloric deficit if faster progress is desired."
                else:
                    rate = "moderate"
                    recommendation = "You're losing weight at a healthy, sustainable rate. Keep up the good work!"
            elif total_weight_change > 0:
                weight_trend = "weight gain"
                if avg_weekly_change > 1.0:
                    rate = "rapid"
                    recommendation = "You're gaining weight quickly. If muscle gain is your goal, consider slowing down to minimize fat gain."
                else:
                    rate = "moderate"
                    recommendation = "You're gaining weight at a reasonable pace for muscle building."
            else:
                weight_trend = "weight maintenance"
                rate = "stable"
                recommendation = "Your weight has remained stable."
            
            # Add plateau recommendation
            if recent_plateau:
                plateau_advice = "\n\nYou appear to have hit a plateau in the last 2 weeks. Consider the following adjustments:\n"
                plateau_advice += "- Recalculate your caloric needs as your metabolism may have adapted\n"
                plateau_advice += "- Increase your activity level or adjust your workout intensity\n"
                plateau_advice += "- Ensure you're getting enough protein and quality sleep\n"
                plateau_advice += "- Consider a diet break at maintenance calories for 1-2 weeks to reset hormones"
                recommendation += plateau_advice
            
            analysis = f"Analysis of Your Progress Data\n\n"
            analysis += f"Overall Trend: {rate.capitalize()} {weight_trend} averaging {abs(avg_weekly_change):.1f} lbs per week\n\n"
            analysis += f"Recommendation: {recommendation}\n\n"
            analysis += "Note: This is an algorithmic analysis based on statistical patterns in your data."
            
            return analysis
        
        except Exception as e:
            print(f"Error in algorithmic analysis: {e}")
            return "Unable to analyze data due to an error. Please ensure your data is complete and try again."
    
    def _generate_plateau_detection(self, progress_data, metric):
        """Generate algorithmic plateau detection when AI is not available"""
        try:
            if len(progress_data) < 3:
                return "Not enough data for plateau detection. Please provide at least three weeks of data."
            
            # Extract values for the specified metric
            values = [entry.get(metric, 0) for entry in progress_data]
            
            # Check for plateau (less than 0.5% change over last 3 entries)
            recent_values = values[-3:]
            max_val = max(recent_values)
            min_val = min(recent_values)
            
            # Calculate percentage change
            if min_val == 0:  # Avoid division by zero
                perc_change = 0
            else:
                perc_change = (max_val - min_val) / min_val * 100
            
            is_plateau = perc_change < 0.5
            
            if is_plateau:
                response = f"Plateau Detected in {metric.capitalize()}\n\n"
                response += f"Your {metric} has changed less than 0.5% over the past 3 measurements, indicating a plateau.\n\n"
                response += "Recommendations to Break Through:\n"
                
                if metric.lower() == "weight":
                    response += "1. Recalculate your daily caloric needs and adjust your deficit\n"
                    response += "2. Increase your daily activity (steps, NEAT)\n"
                    response += "3. Try changing up your workout routine to challenge your body differently\n"
                    response += "4. Consider a diet break at maintenance calories for 1-2 weeks\n"
                elif metric.lower() == "body_fat":
                    response += "1. Ensure your protein intake is sufficient (0.8-1g per lb of bodyweight)\n"
                    response += "2. Focus on progressive overload in your resistance training\n"
                    response += "3. Consider adjusting your carb/fat ratio while maintaining caloric deficit\n"
                    response += "4. Improve sleep quality and stress management\n"
                else:
                    response += "1. Review your nutrition to ensure it supports your goals\n"
                    response += "2. Adjust your training to focus specifically on this measurement\n"
                    response += "3. Ensure proper recovery between workouts\n"
                
                response += "\nImplement these changes for 2-3 weeks and monitor your progress."
            else:
                response = f"No Plateau Detected in {metric.capitalize()}\n\n"
                response += f"Your {metric} is still changing at a rate greater than 0.5% over the past 3 measurements.\n\n"
                response += "Recommendation: Continue with your current approach as it appears to be working."
            
            return response
            
        except Exception as e:
            print(f"Error in plateau detection: {e}")
            return f"Unable to analyze {metric} data due to an error. Please ensure your data is complete and try again."
    
    def _generate_goal_adjustments(self, initial_goal, progress_data):
        """Generate algorithmic goal adjustments when AI is not available"""
        try:
            if len(progress_data) < 2:
                return "Not enough progress data to suggest goal adjustments. Please provide at least two weeks of data."
            
            # Extract goal values
            target_weight = initial_goal.get('weight', 0)
            target_bf = initial_goal.get('body_fat', 0)
            target_weeks = initial_goal.get('weeks', 12)  # Default to 12 weeks if not specified
            
            # Extract current values from latest progress entry
            current_weight = progress_data[-1].get('weight', 0)
            current_bf = progress_data[-1].get('body_fat', 0)
            
            # Calculate weeks elapsed
            try:
                start_date = datetime.datetime.strptime(progress_data[0]['date'], '%m/%d/%Y')
                current_date = datetime.datetime.strptime(progress_data[-1]['date'], '%m/%d/%Y')
                weeks_elapsed = (current_date - start_date).days / 7
            except (ValueError, KeyError):
                # Fallback if date parsing fails
                weeks_elapsed = len(progress_data) - 1
            
            # Calculate weekly rates needed to hit targets
            remaining_weeks = max(0.1, target_weeks - weeks_elapsed)  # Avoid division by zero
            
            weight_needed_per_week = (target_weight - current_weight) / remaining_weeks
            bf_needed_per_week = (target_bf - current_bf) / remaining_weeks
            
            # Calculate actual weekly rates of change
            if len(progress_data) > 1:
                actual_weight_change = progress_data[-1].get('weight', 0) - progress_data[0].get('weight', 0)
                actual_bf_change = progress_data[-1].get('body_fat', 0) - progress_data[0].get('body_fat', 0)
                
                actual_weight_per_week = actual_weight_change / weeks_elapsed if weeks_elapsed > 0 else 0
                actual_bf_per_week = actual_bf_change / weeks_elapsed if weeks_elapsed > 0 else 0
            else:
                actual_weight_per_week = 0
                actual_bf_per_week = 0
            
            # Generate goal adjustment suggestions
            response = "Goal Adjustment Analysis\n\n"
            
            # Weight goal adjustment
            if abs(weight_needed_per_week) > 2.0:  # More than 2 lbs per week is aggressive
                response += "Weight Goal Adjustment Needed:\n"
                if weight_needed_per_week < 0:  # Weight loss goal
                    new_weight_goal = current_weight + (-2.0 * remaining_weeks)  # Max 2 lbs loss per week
                    response += f"Your current weight loss goal is too aggressive. Adjust target weight from {target_weight} to {new_weight_goal:.1f} lbs "
                    response += "for a safer rate of 1-2 lbs per week.\n\n"
                else:  # Weight gain goal
                    new_weight_goal = current_weight + (1.0 * remaining_weeks)  # Max 1 lb gain per week
                    response += f"Your current weight gain goal is too aggressive. Adjust target weight from {target_weight} to {new_weight_goal:.1f} lbs "
                    response += "for a better muscle-to-fat ratio gain.\n\n"
            else:
                response += "Weight Goal Assessment:\n"
                response += f"Your current weight goal of {target_weight} lbs remains appropriate based on your progress.\n\n"
            
            # Body fat goal adjustment
            max_bf_change_per_week = 0.5  # Max 0.5% body fat reduction per week is realistic
            if abs(bf_needed_per_week) > max_bf_change_per_week:
                response += "Body Fat Goal Adjustment Needed:\n"
                if bf_needed_per_week < 0:  # BF reduction goal
                    new_bf_goal = current_bf + (-max_bf_change_per_week * remaining_weeks)
                    response += f"Your body fat reduction goal is too aggressive. Adjust target from {target_bf}% to {new_bf_goal:.1f}% "
                    response += "for a more realistic goal that preserves muscle mass.\n\n"
                else:  # BF increase goal (rare)
                    response += f"Increasing body fat percentage is an unusual goal. Please review if this is actually intended.\n\n"
            else:
                response += "Body Fat Goal Assessment:\n"
                response += f"Your current body fat goal of {target_bf}% remains appropriate based on your progress.\n\n"
            
            # Timeline adjustment
            if (abs(weight_needed_per_week) > 2.0 or abs(bf_needed_per_week) > max_bf_change_per_week) and target_weeks > 0:
                # Calculate more realistic timeline
                if weight_needed_per_week < 0:  # Weight loss
                    realistic_weeks = abs(current_weight - target_weight) / 1.5  # Assume 1.5 lbs per week
                else:  # Weight gain
                    realistic_weeks = abs(current_weight - target_weight) / 0.5  # Assume 0.5 lbs per week
                
                bf_weeks = abs(current_bf - target_bf) / 0.5  # Assume 0.5% BF change per week
                
                # Take the longer timeline
                new_timeline = max(realistic_weeks, bf_weeks)
                
                response += "Timeline Adjustment Recommendation:\n"
                response += f"Consider extending your timeline from {target_weeks} to {new_timeline:.1f} weeks "
                response += "for more sustainable progress.\n"
            
            return response
            
        except Exception as e:
            print(f"Error generating goal adjustments: {e}")
            return "Unable to suggest goal adjustments due to an error. Please ensure your goal and progress data are complete and try again."

# For testing
if __name__ == "__main__":
    # Example API key - this is not real
    api_key = "AIzaSyCRrI2gmCtSx3FUS1vm8If67xoupGz2Ph0"
    
    # Create the Gemini AI instance
    gemini = GeminiAI(api_key=api_key)
    
    # Test API connection
    if gemini.test_api_connection():
        print("Gemini API is working!")
        
        # Generate a simple text response
        response = gemini.generate_text("What are the best strategies for fat loss while preserving muscle?")
        print("\nGemini Response:")
        print(response)
    else:
        print("Gemini API is not working. Using algorithmic analysis fallback.")
        
        # Test algorithmic analysis
        weight_data = [
            {"date": "01/01/2025", "weight": 200},
            {"date": "01/08/2025", "weight": 198},
            {"date": "01/15/2025", "weight": 196},
            {"date": "01/22/2025", "weight": 194},
            {"date": "01/29/2025", "weight": 193.8},
            {"date": "02/05/2025", "weight": 193.6}
        ]
        
        bf_data = [
            {"date": "01/01/2025", "body_fat": 25},
            {"date": "01/08/2025", "body_fat": 24.5},
            {"date": "01/15/2025", "body_fat": 24},
            {"date": "01/22/2025", "body_fat": 23.5},
            {"date": "01/29/2025", "body_fat": 23.4},
            {"date": "02/05/2025", "body_fat": 23.3}
        ]
        
        analysis = gemini._generate_algorithmic_analysis(weight_data, bf_data)
        print("\nAlgorithmic Analysis:")
        print(analysis)

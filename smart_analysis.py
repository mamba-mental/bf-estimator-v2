#!/usr/bin/env python
# smart_analysis.py - AI-powered progress analysis features
# Created: 03/27/25

import sqlite3
import datetime
import numpy as np
import math
from collections import defaultdict

# Constants for analysis
MIN_DATA_POINTS = 4  # Minimum number of data points needed for meaningful analysis
PLATEAU_THRESHOLD = 0.5  # % change threshold to consider a plateau (in either direction)
PLATEAU_DURATION_WEEKS = 3  # Number of consecutive weeks with minimal change to identify plateau
HEALTHY_WEIGHT_LOSS_RATE = 1.0  # Healthy weight loss per week in lbs
HEALTHY_BF_LOSS_RATE = 0.5  # Healthy body fat % loss per week

def analyze_progress(db_conn, user_id=None):
    """
    Analyze user progress data and generate insights and recommendations.
    
    Args:
        db_conn: SQLite database connection
        user_id: Optional user ID to analyze. If None, analyzes the most active user.
        
    Returns:
        str: Formatted analysis text with insights and recommendations
    """
    # Get user data
    if user_id is None:
        user_id = _get_most_active_user(db_conn)
        if not user_id:
            return "No user data available for analysis."
    
    # Get user profile data
    user_data = _get_user_profile(db_conn, user_id)
    if not user_data:
        return "User profile not found."
    
    # Get progress data
    progress_data = _get_progress_data(db_conn, user_id)
    if not progress_data or len(progress_data) < MIN_DATA_POINTS:
        return f"Insufficient data for analysis. At least {MIN_DATA_POINTS} data points are needed."
    
    # Perform analyses
    analysis_results = {}
    
    # Weight trend analysis
    weight_analysis = _analyze_weight_trend(progress_data, user_data)
    if weight_analysis:
        analysis_results["weight"] = weight_analysis
    
    # Body fat trend analysis
    bf_analysis = _analyze_body_fat_trend(progress_data, user_data)
    if bf_analysis:
        analysis_results["body_fat"] = bf_analysis
    
    # Plateau detection
    plateau_analysis = _detect_plateaus(progress_data)
    if plateau_analysis:
        analysis_results["plateaus"] = plateau_analysis
    
    # Goal adjustments
    goal_analysis = _analyze_goal_feasibility(progress_data, user_data)
    if goal_analysis:
        analysis_results["goals"] = goal_analysis
    
    # Format results into readable text
    report_text = _format_analysis_report(analysis_results, user_data)
    
    return report_text

def _get_most_active_user(db_conn):
    """Get the user ID with the most progress entries."""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT user_id, COUNT(*) as entry_count 
        FROM weekly_progress 
        GROUP BY user_id 
        ORDER BY entry_count DESC 
        LIMIT 1
    """)
    result = cursor.fetchone()
    return result[0] if result else None

def _get_user_profile(db_conn, user_id):
    """Get user profile data from the database."""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT name, gender, age, height, goal_weight, goal_bf,
               activity_level, experience_level
        FROM user_profiles
        WHERE user_id = ?
    """, (user_id,))
    
    row = cursor.fetchone()
    if not row:
        return None
    
    # Convert tuple to dict if using sqlite3.Row factory
    if isinstance(row, tuple):
        keys = ["name", "gender", "age", "height", "goal_weight", "goal_bf", 
                "activity_level", "experience_level"]
        return dict(zip(keys, row))
    
    return dict(row)

def _get_progress_data(db_conn, user_id):
    """Get user progress data sorted by date."""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT date, weight, body_fat_percentage, muscle_gain
        FROM weekly_progress
        WHERE user_id = ?
        ORDER BY date ASC
    """, (user_id,))
    
    results = cursor.fetchall()
    progress_data = []
    
    # Convert to list of dicts
    for row in results:
        if isinstance(row, tuple):
            entry = {
                "date": row[0],
                "weight": row[1],
                "body_fat": row[2],
                "muscle_gain": row[3] if len(row) > 3 and row[3] is not None else 0
            }
        else:
            entry = dict(row)
            if "body_fat_percentage" in entry:
                entry["body_fat"] = entry.pop("body_fat_percentage")
            if "muscle_gain" not in entry or entry["muscle_gain"] is None:
                entry["muscle_gain"] = 0
        
        # Convert date string to datetime object for calculations
        if isinstance(entry["date"], str):
            try:
                entry["date"] = datetime.datetime.strptime(entry["date"], "%Y-%m-%d").date()
            except ValueError:
                continue  # Skip invalid dates
        
        progress_data.append(entry)
    
    return progress_data

def _analyze_weight_trend(progress_data, user_data):
    """
    Analyze weight trends over time.
    
    Returns a dict with insights about weight changes.
    """
    weights = [entry["weight"] for entry in progress_data]
    dates = [entry["date"] for entry in progress_data]
    
    if len(weights) < MIN_DATA_POINTS:
        return None
    
    # Calculate total and average weekly change
    total_change = weights[-1] - weights[0]
    
    # Calculate weeks between first and last entry
    days_diff = (dates[-1] - dates[0]).days
    weeks_diff = max(1, days_diff / 7)  # At least 1 week to avoid division by zero
    
    avg_weekly_change = total_change / weeks_diff
    
    # Calculate consistency of change (using standard deviation of weekly changes)
    weekly_changes = []
    for i in range(1, len(weights)):
        days_between = (dates[i] - dates[i-1]).days
        weeks_between = max(0.1, days_between / 7)  # At least 0.1 weeks to avoid extreme values
        weekly_change = (weights[i] - weights[i-1]) / weeks_between
        weekly_changes.append(weekly_change)
    
    consistency = np.std(weekly_changes) if weekly_changes else 0
    
    # Determine if trend is in the desired direction
    is_losing = avg_weekly_change < 0
    is_gaining = avg_weekly_change > 0
    
    # Check if aligned with goal (assuming goal_weight exists)
    has_goal = user_data.get("goal_weight") is not None
    goal_direction = None
    if has_goal:
        goal_weight = user_data["goal_weight"]
        start_weight = weights[0]
        current_weight = weights[-1]
        
        goal_requires_loss = start_weight > goal_weight
        goal_requires_gain = start_weight < goal_weight
        
        if (goal_requires_loss and is_losing) or (goal_requires_gain and is_gaining):
            goal_direction = "aligned"
        elif (goal_requires_loss and is_gaining) or (goal_requires_gain and is_losing):
            goal_direction = "opposite"
        else:
            goal_direction = "neutral"
    
    # Calculate projected timeline to goal
    weeks_to_goal = None
    if has_goal and abs(avg_weekly_change) > 0.1:  # Only if there's meaningful change
        remaining_change = user_data["goal_weight"] - weights[-1]
        if (remaining_change < 0 and avg_weekly_change < 0) or (remaining_change > 0 and avg_weekly_change > 0):
            weeks_to_goal = abs(remaining_change / avg_weekly_change)
    
    # Calculate predicted weight in 4 weeks if trend continues
    predicted_weight = weights[-1] + (avg_weekly_change * 4)
    
    # Determine if rate of change is healthy (for weight loss)
    is_healthy_rate = True
    if is_losing and abs(avg_weekly_change) > HEALTHY_WEIGHT_LOSS_RATE * 1.5:
        is_healthy_rate = False
    
    return {
        "total_change": total_change,
        "avg_weekly_change": avg_weekly_change,
        "consistency": consistency,
        "trend_direction": "losing" if is_losing else "gaining" if is_gaining else "maintaining",
        "goal_alignment": goal_direction,
        "weeks_to_goal": weeks_to_goal,
        "predicted_weight": predicted_weight,
        "is_healthy_rate": is_healthy_rate
    }

def _analyze_body_fat_trend(progress_data, user_data):
    """
    Analyze body fat percentage trends over time.
    
    Returns a dict with insights about body fat changes.
    """
    body_fats = [entry["body_fat"] for entry in progress_data if entry.get("body_fat") is not None]
    dates = [entry["date"] for entry in progress_data if entry.get("body_fat") is not None]
    
    if len(body_fats) < MIN_DATA_POINTS:
        return None
    
    # Calculate total and average weekly change
    total_change = body_fats[-1] - body_fats[0]
    
    # Calculate weeks between first and last entry
    days_diff = (dates[-1] - dates[0]).days
    weeks_diff = max(1, days_diff / 7)  # At least 1 week to avoid division by zero
    
    avg_weekly_change = total_change / weeks_diff
    
    # Calculate consistency of change
    weekly_changes = []
    for i in range(1, len(body_fats)):
        days_between = (dates[i] - dates[i-1]).days
        weeks_between = max(0.1, days_between / 7)  # At least 0.1 weeks
        weekly_change = (body_fats[i] - body_fats[i-1]) / weeks_between
        weekly_changes.append(weekly_change)
    
    consistency = np.std(weekly_changes) if weekly_changes else 0
    
    # Determine if trend is in the desired direction (usually decreasing for body fat)
    is_losing = avg_weekly_change < 0
    is_gaining = avg_weekly_change > 0
    
    # Check if aligned with goal
    has_goal = user_data.get("goal_bf") is not None
    goal_direction = None
    if has_goal:
        goal_bf = user_data["goal_bf"]
        start_bf = body_fats[0]
        current_bf = body_fats[-1]
        
        goal_requires_loss = start_bf > goal_bf
        goal_requires_gain = start_bf < goal_bf  # Unusual but possible
        
        if (goal_requires_loss and is_losing) or (goal_requires_gain and is_gaining):
            goal_direction = "aligned"
        elif (goal_requires_loss and is_gaining) or (goal_requires_gain and is_losing):
            goal_direction = "opposite"
        else:
            goal_direction = "neutral"
    
    # Calculate projected timeline to goal
    weeks_to_goal = None
    if has_goal and abs(avg_weekly_change) > 0.05:  # Only if there's meaningful change
        remaining_change = user_data["goal_bf"] - body_fats[-1]
        if (remaining_change < 0 and avg_weekly_change < 0) or (remaining_change > 0 and avg_weekly_change > 0):
            weeks_to_goal = abs(remaining_change / avg_weekly_change)
    
    # Calculate predicted body fat in 4 weeks if trend continues
    predicted_bf = body_fats[-1] + (avg_weekly_change * 4)
    
    # Determine if rate of change is healthy (for body fat loss)
    is_healthy_rate = True
    if is_losing and abs(avg_weekly_change) > HEALTHY_BF_LOSS_RATE * 1.5:
        is_healthy_rate = False
    
    return {
        "total_change": total_change,
        "avg_weekly_change": avg_weekly_change,
        "consistency": consistency,
        "trend_direction": "losing" if is_losing else "gaining" if is_gaining else "maintaining",
        "goal_alignment": goal_direction,
        "weeks_to_goal": weeks_to_goal,
        "predicted_bf": predicted_bf,
        "is_healthy_rate": is_healthy_rate
    }

def _detect_plateaus(progress_data):
    """
    Detect plateaus in weight and body fat progress.
    
    Returns a dict with plateau information.
    """
    weights = [(entry["date"], entry["weight"]) for entry in progress_data]
    body_fats = [(entry["date"], entry["body_fat"]) for entry in progress_data if entry.get("body_fat") is not None]
    
    plateaus = {}
    
    # Check for weight plateaus
    if len(weights) >= PLATEAU_DURATION_WEEKS + 1:
        weight_plateau = _check_plateau_sequence(weights)
        if weight_plateau:
            plateaus["weight"] = weight_plateau
    
    # Check for body fat plateaus
    if len(body_fats) >= PLATEAU_DURATION_WEEKS + 1:
        bf_plateau = _check_plateau_sequence(body_fats)
        if bf_plateau:
            plateaus["body_fat"] = bf_plateau
    
    return plateaus if plateaus else None

def _check_plateau_sequence(data_points):
    """
    Check if the most recent sequence of data points indicates a plateau.
    
    Args:
        data_points: List of (date, value) tuples sorted by date
        
    Returns:
        Dict with plateau details if detected, None otherwise
    """
    # Check only the most recent values
    recent_points = data_points[-PLATEAU_DURATION_WEEKS-1:]
    
    # Calculate percent changes
    changes = []
    for i in range(1, len(recent_points)):
        prev_date, prev_value = recent_points[i-1]
        curr_date, curr_value = recent_points[i]
        
        days_between = (curr_date - prev_date).days if isinstance(curr_date, datetime.date) else 7
        weeks_between = max(0.1, days_between / 7)
        
        # Percent change per week
        pct_change = (curr_value - prev_value) * 100 / (prev_value * weeks_between)
        changes.append(abs(pct_change))
    
    # Check if all recent changes are below threshold
    is_plateau = all(change < PLATEAU_THRESHOLD for change in changes)
    
    if is_plateau:
        start_date = recent_points[0][0]
        end_date = recent_points[-1][0]
        duration_days = (end_date - start_date).days if isinstance(end_date, datetime.date) else 7 * (len(recent_points) - 1)
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "duration_days": duration_days,
            "duration_weeks": duration_days / 7,
            "avg_value": sum(point[1] for point in recent_points) / len(recent_points)
        }
    
    return None

def _analyze_goal_feasibility(progress_data, user_data):
    """
    Analyze the feasibility of current goals based on progress trends.
    
    Returns a dict with goal adjustment recommendations.
    """
    goal_analysis = {}
    
    # Need both current goals and sufficient progress data
    if (user_data.get("goal_weight") is None and user_data.get("goal_bf") is None) or len(progress_data) < MIN_DATA_POINTS:
        return None
    
    # Weight goal analysis
    if user_data.get("goal_weight") is not None:
        weights = [entry["weight"] for entry in progress_data]
        dates = [entry["date"] for entry in progress_data]
        
        # Current state
        current_weight = weights[-1]
        goal_weight = user_data["goal_weight"]
        
        # Gap to goal
        weight_gap = current_weight - goal_weight
        
        # Historical rate of change
        days_diff = (dates[-1] - dates[0]).days
        weeks_diff = max(1, days_diff / 7)
        historical_rate = (weights[-1] - weights[0]) / weeks_diff
        
        # Time to goal at current rate
        if abs(historical_rate) > 0.1:  # Only if there's meaningful change
            weeks_to_goal = abs(weight_gap / historical_rate) if historical_rate != 0 else float('inf')
            realistic_timeframe = abs(weight_gap / HEALTHY_WEIGHT_LOSS_RATE) if weight_gap < 0 else abs(weight_gap / (HEALTHY_WEIGHT_LOSS_RATE / 2))
            
            is_realistic = True
            if weeks_to_goal > realistic_timeframe * 1.5:  # 50% buffer
                is_realistic = False
            
            # Propose intermediate goal if needed
            intermediate_goal = None
            if not is_realistic and weight_gap < 0:  # Weight loss goal
                # Suggest a 12-week goal as intermediate
                achievable_loss = HEALTHY_WEIGHT_LOSS_RATE * 12
                if abs(weight_gap) > achievable_loss:
                    intermediate_goal = current_weight - achievable_loss
            
            goal_analysis["weight"] = {
                "current_gap": weight_gap,
                "historical_rate": historical_rate,
                "weeks_to_goal": weeks_to_goal,
                "is_realistic": is_realistic,
                "intermediate_goal": intermediate_goal
            }
    
    # Body fat goal analysis
    if user_data.get("goal_bf") is not None:
        body_fats = [entry["body_fat"] for entry in progress_data if entry.get("body_fat") is not None]
        dates = [entry["date"] for entry in progress_data if entry.get("body_fat") is not None]
        
        if len(body_fats) >= MIN_DATA_POINTS:
            # Current state
            current_bf = body_fats[-1]
            goal_bf = user_data["goal_bf"]
            
            # Gap to goal
            bf_gap = current_bf - goal_bf
            
            # Historical rate of change
            days_diff = (dates[-1] - dates[0]).days
            weeks_diff = max(1, days_diff / 7)
            historical_rate = (body_fats[-1] - body_fats[0]) / weeks_diff
            
            # Time to goal at current rate
            if abs(historical_rate) > 0.05:  # Only if there's meaningful change
                weeks_to_goal = abs(bf_gap / historical_rate) if historical_rate != 0 else float('inf')
                realistic_timeframe = abs(bf_gap / HEALTHY_BF_LOSS_RATE) if bf_gap < 0 else abs(bf_gap / (HEALTHY_BF_LOSS_RATE / 2))
                
                is_realistic = True
                if weeks_to_goal > realistic_timeframe * 1.5:  # 50% buffer
                    is_realistic = False
                
                # Propose intermediate goal if needed
                intermediate_goal = None
                if not is_realistic and bf_gap < 0:  # BF reduction goal
                    # Suggest a 12-week goal as intermediate
                    achievable_loss = HEALTHY_BF_LOSS_RATE * 12
                    if abs(bf_gap) > achievable_loss:
                        intermediate_goal = current_bf - achievable_loss
                
                goal_analysis["body_fat"] = {
                    "current_gap": bf_gap,
                    "historical_rate": historical_rate,
                    "weeks_to_goal": weeks_to_goal,
                    "is_realistic": is_realistic,
                    "intermediate_goal": intermediate_goal
                }
    
    return goal_analysis if goal_analysis else None

def _format_analysis_report(analysis_results, user_data):
    """
    Format analysis results into a readable report.
    
    Args:
        analysis_results: Dict of analysis results
        user_data: Dict of user profile data
        
    Returns:
        str: Formatted analysis report
    """
    report = []
    
    # Add personalized greeting
    name = user_data.get("name", "there")
    report.append(f"Hi {name}! Here's your personalized progress analysis:")
    report.append("")
    
    # Weight analysis
    if "weight" in analysis_results:
        weight = analysis_results["weight"]
        report.append("🏋️ WEIGHT PROGRESS:")
        
        # Overall trend
        total_change = weight["total_change"]
        change_direction = "lost" if total_change < 0 else "gained"
        report.append(f"• You've {change_direction} {abs(total_change):.1f} lbs overall.")
        
        # Weekly rate
        weekly = weight["avg_weekly_change"]
        weekly_direction = "losing" if weekly < 0 else "gaining"
        report.append(f"• You're {weekly_direction} an average of {abs(weekly):.1f} lbs per week.")
        
        # Health check
        if not weight["is_healthy_rate"] and weekly < 0:
            report.append(f"⚠️ Your weight loss rate may be too aggressive. Aim for 1-2 lbs per week for sustainable results.")
        
        # Goal alignment
        if weight["goal_alignment"] == "opposite":
            report.append(f"⚠️ Your current trend is moving away from your goal weight. Let's adjust your approach.")
        elif weight["goal_alignment"] == "aligned" and weight["weeks_to_goal"] is not None:
            report.append(f"• At this rate, you'll reach your goal weight in approximately {int(weight['weeks_to_goal'])} weeks.")
        
        report.append("")
    
    # Body fat analysis
    if "body_fat" in analysis_results:
        bf = analysis_results["body_fat"]
        report.append("📊 BODY FAT PROGRESS:")
        
        # Overall trend
        total_change = bf["total_change"]
        change_direction = "lost" if total_change < 0 else "gained"
        report.append(f"• You've {change_direction} {abs(total_change):.1f}% body fat overall.")
        
        # Weekly rate
        weekly = bf["avg_weekly_change"]
        weekly_direction = "losing" if weekly < 0 else "gaining"
        report.append(f"• You're {weekly_direction} an average of {abs(weekly):.2f}% body fat per week.")
        
        # Health check
        if not bf["is_healthy_rate"] and weekly < 0:
            report.append(f"⚠️ Your body fat reduction rate may be too aggressive. Aim for 0.5-1% per week for best results.")
        
        # Goal alignment
        if bf["goal_alignment"] == "opposite":
            report.append(f"⚠️ Your current trend is moving away from your goal body fat percentage. Let's review your approach.")
        elif bf["goal_alignment"] == "aligned" and bf["weeks_to_goal"] is not None:
            report.append(f"• At this rate, you'll reach your goal body fat in approximately {int(bf['weeks_to_goal'])} weeks.")
        
        report.append("")
    
    # Plateau detection
    if "plateaus" in analysis_results:
        plateaus = analysis_results["plateaus"]
        report.append("🔍 PLATEAU DETECTION:")
        
        if "weight" in plateaus:
            wp = plateaus["weight"]
            report.append(f"• Your weight has plateaued at around {wp['avg_value']:.1f} lbs for {int(wp['duration_days'])} days.")
            report.append("  Recommendations to break through:")
            report.append("  - Slightly adjust your calorie intake (try reducing by 100-200 calories)")
            report.append("  - Add variety to your workouts (try HIIT or different exercises)")
            report.append("  - Ensure you're getting enough sleep and managing stress")
        
        if "body_fat" in plateaus:
            bp = plateaus["body_fat"]
            report.append(f"• Your body fat has plateaued at around {bp['avg_value']:.1f}% for {int(bp['duration_days'])} days.")
            report.append("  Recommendations to break through:")
            report.append("  - Focus on resistance training to preserve muscle mass")
            report.append("  - Consider carb cycling or intermittent fasting if appropriate")
            report.append("  - Review your protein intake (aim for 0.8-1g per pound of lean body mass)")
        
        report.append("")
    
    # Goal adjustments
    if "goals" in analysis_results:
        goals = analysis_results["goals"]
        report.append("🎯 GOAL ASSESSMENT:")
        
        if "weight" in goals and not goals["weight"]["is_realistic"]:
            wg = goals["weight"]
            if wg["intermediate_goal"] is not None:
                report.append(f"• Your current weight goal may be challenging to reach at your current pace.")
                report.append(f"  Consider an intermediate goal of {wg['intermediate_goal']:.1f} lbs before targeting your final goal.")
        
        if "body_fat" in goals and not goals["body_fat"]["is_realistic"]:
            bg = goals["body_fat"]
            if bg["intermediate_goal"] is not None:
                report.append(f"• Your current body fat goal may be challenging to reach at your current pace.")
                report.append(f"  Consider an intermediate goal of {bg['intermediate_goal']:.1f}% before targeting your final goal.")
        
        report.append("")
    
    # Add encouraging conclusion
    report.append("Keep up the great work! Remember that consistency is key, and small adjustments can lead to big results over time.")
    
    return "\n".join(report)

# Example usage
if __name__ == "__main__":
    # This can be used to test the module
    db_path = "history.db" 
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    analysis = analyze_progress(conn)
    print(analysis)
    
    conn.close()

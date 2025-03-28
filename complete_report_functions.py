def get_body_fat_info(gender, body_fat_percentage):
    """
    Get information about body fat percentage including category, time to six-pack, and description.
    
    Args:
        gender (str): The gender of the user ('m' or 'f').
        body_fat_percentage (float): The user's body fat percentage.
        
    Returns:
        tuple: (category_name, time_to_six_pack, description)
    """
    categories = [
        {"name": "Very Lean", "men": 10, "women": 18, "time": "3-4 weeks", "description": "Visible abs, vascularity, striations"},
        {"name": "Lean", "men": 14, "women": 22, "time": "2-3 months", "description": "Some muscle definition, less visible abs"},
        {"name": "Average", "men": 19, "women": 27, "time": "3-4 months", "description": "Little muscle definition, soft look"},
        {"name": "Above Average", "men": 24, "women": 32, "time": "4-6 months", "description": "No visible abs, excess fat"},
        {"name": "High Body Fat", "men": 29, "women": 37, "time": "6-12 months", "description": "Excess fat all around, round physique"},
        {"name": "Obese", "men": float('inf'), "women": float('inf'), "time": "12+ months", "description": "Significant excess fat all around"}
    ]
    
    threshold_key = "men" if gender.lower() == 'm' else "women"
    
    for category in categories:
        if body_fat_percentage < category[threshold_key]:
            return category["name"], category["time"], category["description"]
    
    # Default to the highest category if no match found
    return categories[-1]["name"], categories[-1]["time"], categories[-1]["description"]

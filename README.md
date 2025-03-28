# Enhanced Body Fat Estimator v2.0

## Overview

The Enhanced Body Fat Estimator is a comprehensive tool for tracking body composition changes, estimating body fat percentage, and visualizing progress over time. This enhanced version includes smart analysis features, expanded metrics tracking, and significant user experience improvements.

## New Features

### Smart Analysis Features

- **AI-powered feedback** on progress patterns using Google's Gemini API (with algorithmic fallback)
- **Plateau detection** with personalized recommendations
- **Adaptive goal adjustments** based on progress data
- **Muscle loss detection** with prevention strategies

### Expanded Metrics

- **Additional body measurements tracking** including:
  - Waist
  - Hips
  - Chest
  - Arms (left/right)
  - Thighs (left/right)
  - Calves (left/right)
  - Neck
- **Measurement history** visualization

### User Experience Improvements

- **User accounts** with personal data persistence
- **Customizable dashboard** with draggable widget layout options
- **Multiple theme options**:
  - Enhanced Blue (default)
  - Midnight OLED (true black for OLED screens)
  - Forest (green-themed)
  - Lavender (purple-themed)
  - Sunset (orange/red-themed)
  - Batman (dark gray/black/yellow)
- **Voice input** for quick data entry
- **Guided walkthrough tutorials** for new users
- **Progress visualization** improvements

### Cut Timing Presets

- Added preset cut duration options (8, 10, 12, 16 weeks)
- Descriptions for different cut approaches

## Installation

1. Ensure you have Python 3.9+ installed
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   .\run_enhanced_bf_estimator.bat
   ```

## Integrations

### Gemini API (Optional)

For AI-powered analysis, you can set the `GEMINI_API_KEY` environment variable with your Google Gemini API key.

```
set GEMINI_API_KEY=your_api_key_here
```

The application will fall back to algorithmic analysis if no API key is provided.

## File Structure

- **simple_enhanced_app.py**: Main application
- **user_auth.py**: User authentication system
- **theme_manager.py**: Theme management
- **login_interface.py**: Login and registration UI
- **smart_analysis.py**: Progress analysis engine
- **fixed_report_generation.py**: Enhanced report generation
- **update_database.py**: Database schema management
- **complete_report_functions.py**: Helper functions for reports
- **Theme files**: Various .json theme files

## Usage Guide

### Login/Registration

When you first start the application, you'll be prompted to log in or register. You can also use Guest Mode to explore the app without creating an account.

### Dashboard

The dashboard provides a customizable overview of your progress. In Edit mode, you can:
- Drag widgets to your preferred positions
- Toggle widgets on/off
- Resize the layout

### Inputting Data

1. Use the "Input Data" tab to enter your weekly progress data
2. Add additional body measurements for comprehensive tracking
3. Optionally use voice input for hands-free data entry

### Progress Analysis

The application provides:
- Visual charts of your weight and body fat progression
- Smart analysis of your progress patterns
- Personalized recommendations based on your data
- Adaptive goal adjustments

### Reports

Generate comprehensive reports in various formats:
- PDF
- Markdown
- JSON

### Settings

Customize the application to your preferences:
- Theme selection
- Voice input toggle
- Appearance mode (Light/Dark/System)
- User profile settings

## Troubleshooting

- **Theme Issues**: If you experience theme transparency errors, try switching to a different theme and back
- **Voice Input**: Ensure your microphone is properly configured
- **Report Generation**: If report generation fails, check the error message for specific issues

## License

© 2025 Mamba Matrix Solutions LLC. All rights reserved.

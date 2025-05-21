# Enhanced BF Estimator React Application PRD

## 1. Introduction & Goals

The Enhanced BF Estimator React application aims to provide a modern, user-friendly interface for estimating body fat percentage and tracking fitness progress. The application will incorporate advanced features such as AI-powered recommendations, detailed reporting, and robust data persistence.

## 2. Target Audience

The target audience for this application includes fitness enthusiasts, athletes, and individuals seeking to monitor their body composition and health metrics.

## 3. Functional Requirements

### 3.1 User Authentication

*   Implement user authentication using Supabase.
*   Allow users to create accounts, log in, and manage their profiles.

### 3.2 Profile Management

*   Enable users to input their height using dropdowns for feet and inches.
*   Store height in cm internally, calculated as `(feet * 12 + inches) * 2.54`.
*   Allow users to select their activity level from a dropdown with descriptions for levels 1-5.

### 3.3 Goal Setting

*   Provide functionality for users to set fitness goals (e.g., weight loss, muscle gain).
*   Allow users to track progress towards these goals.

### 3.4 Progress Tracking

*   Enable users to log their weight and body fat percentage over time.
*   Display progress through detailed dashboard widgets.

### 3.5 Reporting

*   Generate reports in JSON, PDF, and MD formats.
*   Include comprehensive data, charts, and visualizations in the reports.
*   Ensure reports match or exceed the detail of the terminal app's PDF report.

### 3.6 Dashboard & Widgets

*   Create a detailed dashboard with widgets for weight and body fat loss progression.
*   Utilize modern UI/UX components from `21st-dev/magic` and `shadcn-ui`.

### 3.7 AI-Powered Features

*   Integrate DeepSeek AI and ChatGPT o4-mini-hi for personalized fitness/nutrition tips.
*   Provide AI-generated commentary on progress reports.
*   Offer meal planning suggestions based on user data and TDEE.

## 4. Non-Functional Requirements

### 4.1 UI/UX

*   Implement a modern look using `21st-dev/magic` and `shadcn-ui` components.
*   Ensure a responsive design for various screen sizes and devices.

### 4.2 Data Persistence

*   Use Supabase for storing all user data, progress, and goals.

### 4.3 Performance

*   Optimize the application for fast loading times and smooth interactions.

### 4.4 Security

*   Implement robust security measures to protect user data.
*   Ensure compliance with relevant data protection regulations.

## 5. Technical Stack

*   Frontend: React, Vite, TypeScript
*   UI Components: `21st-dev/magic`, `shadcn-ui`
*   Data Persistence: Supabase
*   Styling: TailwindCSS
*   AI Integration: DeepSeek AI, ChatGPT o4-mini-hi

## 6. Future Considerations

*   Potential integration with wearable devices or health apps.
*   Expansion of AI-powered features for more personalized recommendations.
*   Continuous improvement of UI/UX based on user feedback.
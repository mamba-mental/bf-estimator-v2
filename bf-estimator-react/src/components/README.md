# Profile Management Implementation

This directory contains the UI components and implementation for the profile management feature of the BF Estimator application.

## Components Added

1. **Select Component**: Used for the feet and inches dropdowns in the height input.
2. **RadioGroup Component**: Used for the activity level selection with descriptions.

## Utility Files Added

1. **height-utils.ts**: Contains functions for converting between centimeters and feet/inches.
2. **activity-levels.ts**: Contains the activity level descriptions and multipliers.

## Dependencies Required

To resolve the TypeScript errors, the following dependencies need to be installed:

```bash
npm install @radix-ui/react-select @radix-ui/react-radio-group lucide-react
```

These are required for the Select and RadioGroup components from shadcn-ui.

## Implementation Details

### Height Input

- Replaced the single height input with two dropdowns for feet (4-7) and inches (0-11).
- Height is stored in centimeters in Supabase, calculated as `(feet * 12 + inches) * 2.54`.
- The current height in centimeters is displayed below the dropdowns.

### Activity Level Input

- Replaced the number input with a radio group that displays the full descriptions for each activity level.
- The activity level is stored as a number (1-5) in Supabase.

### Data Persistence

- Profile data is fetched from Supabase on page load.
- When the form is submitted, the profile data is saved to Supabase using an upsert operation.
- The user's ID from the authentication context is used to identify the profile.

## Usage

1. Navigate to the Profile page.
2. Update your personal information, including height (feet and inches) and activity level.
3. Click "Save Changes" to persist the data to Supabase.
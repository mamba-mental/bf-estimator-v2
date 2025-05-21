-- Create the profiles table if it doesn't exist already
-- This table is referenced by the goals and progress_entries tables
CREATE TABLE IF NOT EXISTS profiles (
  id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  name TEXT,
  email TEXT,
  height NUMERIC, -- Height in cm
  gender TEXT,
  activity_level INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create the goals table
CREATE TABLE IF NOT EXISTS goals (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  target_weight NUMERIC NOT NULL, -- Weight in lbs
  target_body_fat NUMERIC NOT NULL, -- Body fat percentage
  target_date DATE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Add a unique constraint on user_id to ensure one active goal per user
  -- This supports the upsert operation in the code
  CONSTRAINT unique_user_goal UNIQUE (user_id)
);

-- Create the progress_entries table
CREATE TABLE IF NOT EXISTS progress_entries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  date DATE NOT NULL,
  weight NUMERIC NOT NULL, -- Weight in lbs
  body_fat_percentage NUMERIC, -- Body fat percentage
  neck NUMERIC, -- Neck measurement in inches
  waist NUMERIC, -- Waist measurement in inches
  hips NUMERIC, -- Hips measurement in inches
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Add a unique constraint to prevent duplicate entries for the same date
  CONSTRAINT unique_user_date UNIQUE (user_id, date)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals (user_id);
CREATE INDEX IF NOT EXISTS idx_progress_entries_user_id ON progress_entries (user_id);
CREATE INDEX IF NOT EXISTS idx_progress_entries_date ON progress_entries (date);

-- Set up Row Level Security (RLS) policies
-- Enable RLS on the tables
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE progress_entries ENABLE ROW LEVEL SECURITY;

-- Create policies for the goals table
CREATE POLICY "Users can view their own goals" 
  ON goals FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own goals" 
  ON goals FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own goals" 
  ON goals FOR UPDATE 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own goals" 
  ON goals FOR DELETE 
  USING (auth.uid() = user_id);

-- Create policies for the progress_entries table
CREATE POLICY "Users can view their own progress entries" 
  ON progress_entries FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own progress entries" 
  ON progress_entries FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own progress entries" 
  ON progress_entries FOR UPDATE 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own progress entries" 
  ON progress_entries FOR DELETE 
  USING (auth.uid() = user_id);

-- Create or replace function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update the updated_at column
CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_goals_updated_at
  BEFORE UPDATE ON goals
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_progress_entries_updated_at
  BEFORE UPDATE ON progress_entries
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
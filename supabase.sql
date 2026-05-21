-- Run this in the Supabase SQL Editor to create the traffic_logs table

CREATE TABLE IF NOT EXISTS traffic_logs (
  id         BIGSERIAL PRIMARY KEY,
  timestamp  TIMESTAMPTZ DEFAULT now(),
  source_ip  TEXT,
  dest_ip    TEXT,
  protocol   TEXT,
  prediction TEXT,   -- 'Normal' or 'Malicious'
  action     TEXT,   -- 'Allowed' or 'Blocked'
  user_id    UUID    -- Tracks which user owns the log
);

-- In case the table already existed before we added user_id
ALTER TABLE traffic_logs ADD COLUMN IF NOT EXISTS user_id UUID;

-- Optional: Create an index on timestamp for faster queries
CREATE INDEX IF NOT EXISTS idx_traffic_logs_timestamp ON traffic_logs(timestamp DESC);

-- ==============================================================
-- 2. Profiles Table (For User Management / Auth UI)
-- Maps to the register.html which collects First Name and Last Name
-- ==============================================================
CREATE TABLE IF NOT EXISTS profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  first_name TEXT,
  last_name TEXT,
  email TEXT UNIQUE,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Set up Row Level Security (RLS)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
CREATE POLICY "Users can view own profile" 
ON profiles FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
CREATE POLICY "Users can update own profile" 
ON profiles FOR UPDATE USING (auth.uid() = id);

-- Trigger to automatically create a profile when a new user signs up via Supabase Auth
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, first_name, last_name, email)
  VALUES (
    new.id, 
    new.raw_user_meta_data->>'first_name', 
    new.raw_user_meta_data->>'last_name', 
    new.email
  );
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- ==============================================================
-- 3. Allow Public API Inserts for Traffic Logs
-- ==============================================================
ALTER TABLE traffic_logs ENABLE ROW LEVEL SECURITY;

-- Allow anonymous API backend to insert new traffic logs
DROP POLICY IF EXISTS "Enable insert for all users" ON traffic_logs;
CREATE POLICY "Enable insert for all users" 
ON traffic_logs FOR INSERT 
TO public
WITH CHECK (true);

-- Allow anonymous API backend to read traffic logs
DROP POLICY IF EXISTS "Enable read for all users" ON traffic_logs;
CREATE POLICY "Enable read for all users" 
ON traffic_logs FOR SELECT 
TO public
USING (true);

-- Allow anonymous API backend to delete traffic logs
DROP POLICY IF EXISTS "Enable delete for all users" ON traffic_logs;
CREATE POLICY "Enable delete for all users" 
ON traffic_logs FOR DELETE 
TO public
USING (true);


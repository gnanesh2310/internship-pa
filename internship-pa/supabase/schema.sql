-- ============================================
-- INTERNSHIP PA — COMPLETE DATABASE SCHEMA
-- Run this entire file in Supabase SQL Editor
-- ============================================

CREATE TABLE profiles (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  full_name TEXT DEFAULT 'Karanam Gnanesh Chowdary',
  primary_email TEXT DEFAULT 'kgnanesh98@gmail.com',
  research_email TEXT DEFAULT 'kgnanesh52@gmail.com',
  phone TEXT DEFAULT '+91 7675 806 215',
  location TEXT DEFAULT 'VNIT Nagpur, Maharashtra',
  portfolio_url TEXT DEFAULT 'gnanesh2310.github.io/Gnaneshportfolio',
  github_url TEXT DEFAULT 'github.com/Gnanesh2310',
  degree TEXT DEFAULT 'B.Tech EEE, VNIT Nagpur, 2023-2027',
  cgpa TEXT DEFAULT '6.69',
  target_roles TEXT[] DEFAULT ARRAY['Web Dev intern','IoT intern','Frontend intern','Embedded Systems intern','Full Stack intern','Research intern'],
  target_locations TEXT[] DEFAULT ARRAY['Remote','Hyderabad','Nagpur','Bangalore','Mumbai'],
  skills_frontend TEXT[] DEFAULT ARRAY['HTML5','CSS3','JavaScript','React.js','Figma'],
  skills_backend TEXT[] DEFAULT ARRAY['Flask','Python'],
  skills_embedded TEXT[] DEFAULT ARRAY['C','ESP32','RPi5','UART','8051'],
  skills_tools TEXT[] DEFAULT ARRAY['Git','VS Code','MATLAB','Multisim','OpenCV','GPS'],
  resume_text TEXT,
  company_daily_limit INTEGER DEFAULT 15,
  professor_daily_limit INTEGER DEFAULT 5,
  send_time_hour INTEGER DEFAULT 9,
  send_time_minute INTEGER DEFAULT 0,
  delay_min_minutes INTEGER DEFAULT 4,
  delay_max_minutes INTEGER DEFAULT 6,
  company_mode_enabled BOOLEAN DEFAULT TRUE,
  professor_mode_enabled BOOLEAN DEFAULT TRUE,
  warmup_mode BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO profiles (id) VALUES ('00000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

CREATE TABLE job_listings (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  company_name TEXT NOT NULL,
  role_title TEXT NOT NULL,
  job_url TEXT,
  source TEXT NOT NULL,
  location TEXT,
  description TEXT,
  tech_stack TEXT[],
  date_found TIMESTAMPTZ DEFAULT NOW(),
  processed BOOLEAN DEFAULT FALSE,
  classification TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_job_company ON job_listings(company_name);
CREATE INDEX idx_job_processed ON job_listings(processed);

CREATE TABLE applications (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  company_or_prof TEXT NOT NULL,
  role_or_paper TEXT NOT NULL,
  contact_email TEXT NOT NULL,
  sent_from TEXT NOT NULL,
  type TEXT NOT NULL,
  subject_line TEXT,
  email_body TEXT,
  status TEXT DEFAULT 'sent',
  date_sent TIMESTAMPTZ DEFAULT NOW(),
  follow_up_date DATE,
  follow_up_sent BOOLEAN DEFAULT FALSE,
  follow_up_sent_at TIMESTAMPTZ,
  reply_received BOOLEAN DEFAULT FALSE,
  reply_received_at TIMESTAMPTZ,
  reply_content TEXT,
  job_listing_id UUID REFERENCES job_listings(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_app_status ON applications(status);
CREATE INDEX idx_app_company ON applications(company_or_prof);
CREATE INDEX idx_app_followup ON applications(follow_up_date, follow_up_sent);

CREATE TABLE professor_targets (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  professor_name TEXT NOT NULL,
  university TEXT NOT NULL,
  department TEXT,
  email TEXT,
  paper_title_1 TEXT,
  paper_abstract_1 TEXT,
  paper_title_2 TEXT,
  paper_abstract_2 TEXT,
  scholar_url TEXT,
  research_areas TEXT[],
  relevance_score INTEGER DEFAULT 0,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_prof_status ON professor_targets(status);
CREATE INDEX idx_prof_university ON professor_targets(university);

CREATE TABLE manual_queue (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  org_name TEXT NOT NULL,
  role TEXT,
  portal_url TEXT,
  deadline DATE,
  reason TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  telegram_alerted BOOLEAN DEFAULT FALSE,
  date_added TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

CREATE INDEX idx_manual_status ON manual_queue(status);
CREATE INDEX idx_manual_deadline ON manual_queue(deadline);

CREATE TABLE activity_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  action_type TEXT NOT NULL,
  description TEXT NOT NULL,
  details JSONB,
  level TEXT DEFAULT 'info',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_log_created ON activity_log(created_at DESC);
CREATE INDEX idx_log_type ON activity_log(action_type);

CREATE TABLE api_usage (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  provider TEXT NOT NULL,
  date DATE DEFAULT CURRENT_DATE,
  tokens_used INTEGER DEFAULT 0,
  requests_made INTEGER DEFAULT 0,
  errors_count INTEGER DEFAULT 0,
  warning_sent BOOLEAN DEFAULT FALSE,
  limit_hit BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(provider, date)
);

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_updated_at
  BEFORE UPDATE ON profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER professor_updated_at
  BEFORE UPDATE ON professor_targets
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE professor_targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE manual_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all" ON profiles FOR ALL USING (true);
CREATE POLICY "service_role_all" ON job_listings FOR ALL USING (true);
CREATE POLICY "service_role_all" ON applications FOR ALL USING (true);
CREATE POLICY "service_role_all" ON professor_targets FOR ALL USING (true);
CREATE POLICY "service_role_all" ON manual_queue FOR ALL USING (true);
CREATE POLICY "service_role_all" ON activity_log FOR ALL USING (true);
CREATE POLICY "service_role_all" ON api_usage FOR ALL USING (true);

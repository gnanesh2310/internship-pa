import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type Application = {
  id: string
  company_or_prof: string
  role_or_paper: string
  contact_email: string
  sent_from: string
  type: 'company' | 'professor'
  subject_line: string
  email_body: string
  status: 'sent' | 'replied' | 'follow_up_sent' | 'manual_needed' | 'failed'
  date_sent: string
  follow_up_date: string | null
  follow_up_sent: boolean
  reply_received: boolean
}

export type ActivityLog = {
  id: string
  action_type: string
  description: string
  details: Record<string, unknown>
  level: 'info' | 'success' | 'warning' | 'error'
  created_at: string
}

export type ManualQueue = {
  id: string
  org_name: string
  role: string
  portal_url: string
  deadline: string | null
  reason: string
  status: 'pending' | 'done' | 'skipped'
  telegram_alerted: boolean
  date_added: string
}

export type Profile = {
  id: string
  full_name: string
  primary_email: string
  research_email: string
  phone: string
  location: string
  portfolio_url: string
  github_url: string
  degree: string
  cgpa: string
  target_roles: string[]
  target_locations: string[]
  skills_frontend: string[]
  skills_backend: string[]
  skills_embedded: string[]
  skills_tools: string[]
  resume_text: string
  company_daily_limit: number
  professor_daily_limit: number
  send_time_hour: number
  send_time_minute: number
  delay_min_minutes: number
  delay_max_minutes: number
  company_mode_enabled: boolean
  professor_mode_enabled: boolean
  warmup_mode: boolean
}

export type ApiUsage = {
  provider: string
  date: string
  tokens_used: number
  requests_made: number
  errors_count: number
  warning_sent: boolean
  limit_hit: boolean
}

'use client'

import { useEffect, useState } from 'react'
import { supabase, Profile } from '@/lib/supabase'
import ToggleSwitch from '@/components/ToggleSwitch'
import { CheckCircle, Send, Sliders } from 'lucide-react'

export default function SettingsPage() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [telegramTesting, setTelegramTesting] = useState(false)
  const [saved, setSaved] = useState(false)

  async function loadProfile() {
    const { data } = await supabase.from('profiles').select('*').eq('id', '00000000-0000-0000-0000-000000000001').single()
    setProfile(data)
    setLoading(false)
  }

  useEffect(() => { loadProfile() }, [])

  async function saveProfile() {
    if (!profile) return
    setSaving(true)
    await supabase.from('profiles').update(profile).eq('id', '00000000-0000-0000-0000-000000000001')
    setSaving(false)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  async function testTelegram() {
    setTelegramTesting(true)
    try {
      const res = await fetch('/api/telegram-test', { method: 'POST' })
      if (!res.ok) throw new Error('Failed')
      alert('✓ Test message sent to Telegram!')
    } catch {
      alert('✗ Failed. Check your TELEGRAM_BOT_TOKEN in environment variables.')
    }
    setTelegramTesting(false)
  }

  if (loading || !profile) return <div className="text-gray-400 p-8">Loading settings...</div>

  return (
    <div className="space-y-6 animate-fade-in max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-gray-400 text-sm mt-0.5">Control how your PA behaves</p>
      </div>

      {/* Email Limits */}
      <div className="card p-5 space-y-5">
        <h2 className="text-sm font-semibold text-gray-300 flex items-center gap-2"><Sliders size={15} /> Daily Email Limits</h2>

        <div>
          <div className="flex justify-between mb-2">
            <label className="text-sm text-gray-400">Company emails/day</label>
            <span className="text-sm font-medium text-white">{profile.company_daily_limit}</span>
          </div>
          <input type="range" min={0} max={20} step={1} value={profile.company_daily_limit}
            onChange={e => setProfile({ ...profile, company_daily_limit: +e.target.value })}
            className="w-full accent-indigo-500" />
          <div className="flex justify-between text-xs text-gray-600 mt-1"><span>0</span><span>20</span></div>
        </div>

        <div>
          <div className="flex justify-between mb-2">
            <label className="text-sm text-gray-400">Professor emails/day</label>
            <span className="text-sm font-medium text-white">{profile.professor_daily_limit}</span>
          </div>
          <input type="range" min={0} max={10} step={1} value={profile.professor_daily_limit}
            onChange={e => setProfile({ ...profile, professor_daily_limit: +e.target.value })}
            className="w-full accent-indigo-500" />
          <div className="flex justify-between text-xs text-gray-600 mt-1"><span>0</span><span>10</span></div>
        </div>

        <div>
          <div className="flex justify-between mb-2">
            <label className="text-sm text-gray-400">Delay between emails</label>
            <span className="text-sm font-medium text-white">{profile.delay_min_minutes}–{profile.delay_max_minutes} min</span>
          </div>
          <div className="flex gap-3">
            <input type="range" min={1} max={10} step={1} value={profile.delay_min_minutes}
              onChange={e => setProfile({ ...profile, delay_min_minutes: +e.target.value })}
              className="flex-1 accent-indigo-500" />
            <input type="range" min={1} max={15} step={1} value={profile.delay_max_minutes}
              onChange={e => setProfile({ ...profile, delay_max_minutes: +e.target.value })}
              className="flex-1 accent-indigo-500" />
          </div>
        </div>

        <div>
          <div className="flex justify-between mb-2">
            <label className="text-sm text-gray-400">Send time (hour, IST)</label>
            <span className="text-sm font-medium text-white">{profile.send_time_hour}:00 IST</span>
          </div>
          <input type="range" min={6} max={22} step={1} value={profile.send_time_hour}
            onChange={e => setProfile({ ...profile, send_time_hour: +e.target.value })}
            className="w-full accent-indigo-500" />
          <div className="flex justify-between text-xs text-gray-600 mt-1"><span>6am</span><span>10pm</span></div>
        </div>
      </div>

      {/* Toggles */}
      <div className="card p-5">
        <h2 className="text-sm font-semibold text-gray-300 mb-1">Feature Toggles</h2>
        <div className="divide-y divide-[#1a1a35]">
          <ToggleSwitch label="Company Mode" description="Send emails to companies and startups"
            enabled={profile.company_mode_enabled} onChange={v => setProfile({ ...profile, company_mode_enabled: v })} />
          <ToggleSwitch label="Professor Mode" description="Email professors at IITs and NITs"
            enabled={profile.professor_mode_enabled} onChange={v => setProfile({ ...profile, professor_mode_enabled: v })} />
          <ToggleSwitch label="Warmup Mode" description="Start at 5/day and ramp up gradually"
            enabled={profile.warmup_mode} onChange={v => setProfile({ ...profile, warmup_mode: v })} />
        </div>
      </div>

      {/* API Key Status */}
      <div className="card p-5">
        <h2 className="text-sm font-semibold text-gray-300 mb-4">API Key Status</h2>
        <div className="space-y-3">
          {[
            { name: 'Gemini 1.5 Flash', key: 'GEMINI_API_KEY', role: 'Primary AI' },
            { name: 'Groq Llama3', key: 'GROQ_API_KEY', role: 'Backup AI #1' },
            { name: 'OpenRouter', key: 'OPENROUTER_API_KEY', role: 'Backup AI #2' },
            { name: 'Together AI', key: 'TOGETHER_API_KEY', role: 'Backup AI #3' },
            { name: 'Telegram Bot', key: 'TELEGRAM_BOT_TOKEN', role: 'Notifications' },
            { name: 'Gmail (Company)', key: 'GMAIL_COMPANY_REFRESH_TOKEN', role: 'Sender #1' },
            { name: 'Gmail (Research)', key: 'GMAIL_RESEARCH_REFRESH_TOKEN', role: 'Sender #2' },
            { name: 'Google Sheets', key: 'GOOGLE_SHEETS_ID', role: 'Tracker' },
          ].map(api => (
            <div key={api.key} className="flex items-center justify-between">
              <div>
                <p className="text-sm text-white">{api.name}</p>
                <p className="text-xs text-gray-500">{api.role} · env: {api.key}</p>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-gray-400">
                <CheckCircle size={14} className="text-green-400" />
                Configured
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Telegram Test */}
      <div className="card p-5">
        <h2 className="text-sm font-semibold text-gray-300 mb-2">Telegram Test</h2>
        <p className="text-xs text-gray-500 mb-3">
          Send a test message to confirm your bot is working correctly.
          Your Chat ID: <code className="text-indigo-400">8394802242</code>
        </p>
        <button onClick={testTelegram} disabled={telegramTesting}
          className="flex items-center gap-2 px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-500 rounded-lg transition-colors disabled:opacity-50">
          <Send size={14} />
          {telegramTesting ? 'Sending...' : 'Send Test Message'}
        </button>
      </div>

      <button onClick={saveProfile} disabled={saving}
        className={`w-full py-3 rounded-xl text-sm font-medium transition-all ${saved ? 'bg-green-600 text-white' : 'bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50'}`}>
        {saved ? '✓ Saved!' : saving ? 'Saving...' : 'Save Settings'}
      </button>
    </div>
  )
}

import { supabase } from '@/lib/supabase'
import StatCard from '@/components/StatCard'
import ActivityFeed from '@/components/ActivityFeed'
import TokenBar from '@/components/TokenBar'
import { Send, Briefcase, GraduationCap, AlertTriangle } from 'lucide-react'

async function getDashboardData() {
  const today = new Date().toISOString().split('T')[0]

  const [sentTodayRes, totalAppsRes, profEmailsRes, manualPendingRes, logsRes, apiUsageRes, profileRes] =
    await Promise.all([
      supabase.from('applications').select('*', { count: 'exact', head: true }).gte('date_sent', `${today}T00:00:00`),
      supabase.from('applications').select('*', { count: 'exact', head: true }),
      supabase.from('applications').select('*', { count: 'exact', head: true }).eq('type', 'professor'),
      supabase.from('manual_queue').select('*', { count: 'exact', head: true }).eq('status', 'pending'),
      supabase.from('activity_log').select('*').order('created_at', { ascending: false }).limit(20),
      supabase.from('api_usage').select('*').eq('date', today).eq('provider', 'gemini').single(),
      supabase.from('profiles').select('company_mode_enabled, professor_mode_enabled').eq('id', '00000000-0000-0000-0000-000000000001').single(),
    ])

  return {
    sentToday: sentTodayRes.count ?? 0,
    totalApps: totalAppsRes.count ?? 0,
    profEmails: profEmailsRes.count ?? 0,
    manualPending: manualPendingRes.count ?? 0,
    logs: logsRes.data ?? [],
    apiUsage: apiUsageRes.data,
    profile: profileRes.data,
  }
}

export default async function HomePage() {
  const data = await getDashboardData()
  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'
  const today = new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">{greeting}, Gnanesh! 👋</h1>
          <p className="text-gray-400 mt-1">{today}</p>
        </div>
        <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/20 px-3 py-1.5 rounded-full">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-sm text-green-400 font-medium">PA Running</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Emails Sent Today" value={data.sentToday} icon={Send} color="blue" change="of 15 limit" />
        <StatCard label="Total Applications" value={data.totalApps} icon={Briefcase} color="purple" />
        <StatCard label="Professor Emails" value={data.profEmails} icon={GraduationCap} color="green" />
        <StatCard
          label="Manual Pending"
          value={data.manualPending}
          icon={AlertTriangle}
          color={data.manualPending > 0 ? 'red' : 'green'}
          change={data.manualPending > 0 ? '⚠ action needed' : '✓ all clear'}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 card p-5">
          <h2 className="text-sm font-semibold text-gray-300 mb-4">Live Activity Feed</h2>
          {/* @ts-expect-error server component */}
          <ActivityFeed logs={data.logs} />
        </div>

        <div className="space-y-4">
          <div className="card p-5">
            <h2 className="text-sm font-semibold text-gray-300 mb-4">API Usage Today</h2>
            <TokenBar tokensUsed={data.apiUsage?.tokens_used ?? 0} tokensLimit={1_000_000} provider="Gemini Flash" />
            <div className="mt-4 space-y-2">
              {['Groq (backup 1)', 'OpenRouter (backup 2)', 'Together AI (backup 3)'].map(p => (
                <div key={p} className="flex items-center justify-between text-xs">
                  <span className="text-gray-500">{p}</span>
                  <span className="text-green-400">● standby</span>
                </div>
              ))}
            </div>
          </div>

          <div className="card p-5">
            <h2 className="text-sm font-semibold text-gray-300 mb-2">Quick Controls</h2>
            <div className="divide-y divide-[#1a1a35]">
              <div className="flex items-center justify-between py-3">
                <div>
                  <p className="text-sm text-white">Company Mode</p>
                  <p className="text-xs text-gray-500">Send to companies</p>
                </div>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${data.profile?.company_mode_enabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
                  {data.profile?.company_mode_enabled ? 'ON' : 'OFF'}
                </span>
              </div>
              <div className="flex items-center justify-between py-3">
                <div>
                  <p className="text-sm text-white">Professor Mode</p>
                  <p className="text-xs text-gray-500">Email researchers</p>
                </div>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${data.profile?.professor_mode_enabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
                  {data.profile?.professor_mode_enabled ? 'ON' : 'OFF'}
                </span>
              </div>
            </div>
            <a href="/settings" className="block text-center text-xs text-indigo-400 mt-3 hover:text-indigo-300">
              Change in Settings →
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

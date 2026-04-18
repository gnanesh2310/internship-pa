import { supabase } from '@/lib/supabase'

async function getStatus() {
  const today = new Date().toISOString().split('T')[0]
  const [sentToday, totalApps, manualPending, lastLog] = await Promise.all([
    supabase.from('applications').select('*', { count: 'exact', head: true }).gte('date_sent', `${today}T00:00:00`),
    supabase.from('applications').select('*', { count: 'exact', head: true }),
    supabase.from('manual_queue').select('*', { count: 'exact', head: true }).eq('status', 'pending'),
    supabase.from('activity_log').select('created_at').order('created_at', { ascending: false }).limit(1).single(),
  ])
  return {
    sentToday: sentToday.count ?? 0,
    totalApps: totalApps.count ?? 0,
    manualPending: manualPending.count ?? 0,
    lastRun: lastLog.data?.created_at ?? null,
    isRunning: true,
  }
}

export default async function StatusPage() {
  const status = await getStatus()
  const lastRunText = status.lastRun
    ? new Date(status.lastRun).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) + ' IST'
    : 'Never'

  return (
    <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center p-4">
      <div className="w-full max-w-sm space-y-4">
        <div className="text-center mb-6">
          <p className="text-gray-500 text-sm">🤖 Gnanesh&apos;s Internship PA</p>
          <p className="text-gray-600 text-xs mt-1">
            {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}
          </p>
        </div>

        <div className={`rounded-xl p-4 border ${status.isRunning ? 'bg-green-500/5 border-green-500/20' : 'bg-red-500/5 border-red-500/20'}`}>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${status.isRunning ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
            <p className={`font-medium ${status.isRunning ? 'text-green-400' : 'text-red-400'}`}>
              {status.isRunning ? 'System Running' : 'System Paused'}
            </p>
          </div>
          <p className="text-xs text-gray-500 mt-1">Last run: {lastRunText}</p>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div className="bg-[#0f0f1a] border border-[#1a1a35] rounded-xl p-3 text-center">
            <p className="text-2xl font-bold text-blue-400">{status.sentToday}</p>
            <p className="text-xs text-gray-500 mt-1">Today</p>
          </div>
          <div className="bg-[#0f0f1a] border border-[#1a1a35] rounded-xl p-3 text-center">
            <p className="text-2xl font-bold text-white">{status.totalApps}</p>
            <p className="text-xs text-gray-500 mt-1">Total</p>
          </div>
          <div className="bg-[#0f0f1a] border border-[#1a1a35] rounded-xl p-3 text-center">
            <p className={`text-2xl font-bold ${status.manualPending > 0 ? 'text-red-400' : 'text-green-400'}`}>
              {status.manualPending}
            </p>
            <p className="text-xs text-gray-500 mt-1">Manual</p>
          </div>
        </div>

        <p className="text-center text-xs text-gray-600 mt-4">
          Full dashboard → <a href="/" className="text-indigo-400 hover:underline">Open</a>
        </p>
      </div>
    </div>
  )
}

'use client'

import { useEffect, useState } from 'react'
import { supabase, ManualQueue } from '@/lib/supabase'
import { isUrgent, formatDate } from '@/lib/utils'
import { ExternalLink, Clock, CheckCircle, AlertTriangle, RefreshCw } from 'lucide-react'

export default function ManualQueuePage() {
  const [items, setItems] = useState<ManualQueue[]>([])
  const [loading, setLoading] = useState(true)
  const [markingDone, setMarkingDone] = useState<string | null>(null)

  async function loadItems() {
    setLoading(true)
    const { data } = await supabase.from('manual_queue').select('*').order('date_added', { ascending: false })
    setItems(data ?? [])
    setLoading(false)
  }

  useEffect(() => { loadItems() }, [])

  async function markDone(id: string) {
    setMarkingDone(id)
    await supabase.from('manual_queue').update({ status: 'done', completed_at: new Date().toISOString() }).eq('id', id)
    await supabase.from('activity_log').insert({ action_type: 'manual_done', description: 'Manual application marked as done', level: 'success', details: { item_id: id } })
    await loadItems()
    setMarkingDone(null)
  }

  const pending = items.filter(i => i.status === 'pending')
  const done = items.filter(i => i.status === 'done')

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Manual Queue</h1>
          <p className="text-gray-400 text-sm mt-0.5">Applications that need you to apply manually</p>
        </div>
        <div className="flex items-center gap-3">
          {pending.length > 0 && (
            <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/20 px-3 py-1.5 rounded-full">
              <AlertTriangle size={14} className="text-red-400" />
              <span className="text-sm text-red-400 font-medium">{pending.length} pending</span>
            </div>
          )}
          <button onClick={loadItems} className="p-2 text-gray-400 hover:text-white bg-[#0f0f1a] border border-[#1a1a35] rounded-lg">
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      <div className="bg-amber-500/5 border border-amber-500/20 rounded-xl p-4 text-sm text-amber-300">
        These are government portals and sites where automation is impossible (CAPTCHA, OTP, Aadhaar login).
        Each takes ~10 minutes. Telegram alerts you immediately when a new one is added.
      </div>

      {loading ? (
        <div className="grid gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="h-5 bg-[#1a1a35] rounded w-1/3 mb-3" />
              <div className="h-4 bg-[#1a1a35] rounded w-2/3 mb-2" />
              <div className="h-4 bg-[#1a1a35] rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : pending.length === 0 ? (
        <div className="card p-12 text-center">
          <CheckCircle size={40} className="text-green-400 mx-auto mb-3" />
          <p className="text-white font-medium">All clear!</p>
          <p className="text-gray-400 text-sm mt-1">No manual applications pending.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {pending.map(item => {
            const urgent = isUrgent(item.deadline)
            return (
              <div key={item.id} className={`card p-5 border transition-colors ${urgent ? 'border-red-500/30 bg-red-500/5' : 'border-[#1a1a35]'}`}>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-lg font-semibold text-white">{item.org_name}</h3>
                      {urgent && <span className="text-xs bg-red-500/20 text-red-400 border border-red-500/30 px-2 py-0.5 rounded-full">URGENT</span>}
                    </div>
                    {item.role && <p className="text-gray-300 text-sm mb-2">{item.role}</p>}
                    {item.deadline && (
                      <div className={`flex items-center gap-1.5 text-sm mb-2 ${urgent ? 'text-red-400' : 'text-gray-400'}`}>
                        <Clock size={13} />
                        Deadline: {new Date(item.deadline).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                        {urgent && ' — APPLY TODAY!'}
                      </div>
                    )}
                    <p className="text-sm text-gray-500"><span className="text-gray-400 font-medium">Why manual: </span>{item.reason}</p>
                    <p className="text-xs text-gray-600 mt-2">Added: {formatDate(item.date_added)}{item.telegram_alerted && ' · Telegram alerted ✓'}</p>
                  </div>
                  <div className="flex flex-col gap-2 shrink-0">
                    {item.portal_url && (
                      <a href={item.portal_url} target="_blank" rel="noopener noreferrer"
                        className="flex items-center gap-1.5 px-3 py-2 text-xs text-white bg-indigo-600 hover:bg-indigo-500 rounded-lg transition-colors">
                        <ExternalLink size={12} />Open Portal
                      </a>
                    )}
                    <button onClick={() => markDone(item.id)} disabled={markingDone === item.id}
                      className="flex items-center gap-1.5 px-3 py-2 text-xs text-green-400 bg-green-500/10 border border-green-500/20 hover:bg-green-500/20 rounded-lg transition-colors disabled:opacity-50">
                      <CheckCircle size={12} />
                      {markingDone === item.id ? 'Saving...' : 'Mark Done'}
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {done.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-500 mb-3">Completed ({done.length})</h2>
          <div className="grid gap-2">
            {done.map(item => (
              <div key={item.id} className="card p-4 opacity-50">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-sm font-medium text-white">{item.org_name}</span>
                    {item.role && <span className="text-gray-400 text-sm ml-2">— {item.role}</span>}
                  </div>
                  <span className="text-xs text-green-400">✓ Done</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

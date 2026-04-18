'use client'

import { useEffect, useState, useMemo } from 'react'
import { supabase, Application } from '@/lib/supabase'
import StatusBadge from '@/components/StatusBadge'
import { formatDate } from '@/lib/utils'
import { Search, Download, RefreshCw } from 'lucide-react'

type FilterType = 'all' | 'company' | 'professor' | 'manual_pending' | 'replied'

export default function ApplicationsPage() {
  const [apps, setApps] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<FilterType>('all')
  const [search, setSearch] = useState('')

  async function loadApps() {
    setLoading(true)
    const { data } = await supabase
      .from('applications')
      .select('*')
      .order('date_sent', { ascending: false })
    setApps(data ?? [])
    setLoading(false)
  }

  useEffect(() => { loadApps() }, [])

  const filtered = useMemo(() => {
    return apps.filter(app => {
      if (filter === 'company' && app.type !== 'company') return false
      if (filter === 'professor' && app.type !== 'professor') return false
      if (filter === 'manual_pending' && app.status !== 'manual_needed') return false
      if (filter === 'replied' && app.status !== 'replied') return false
      if (search) {
        const q = search.toLowerCase()
        return (
          app.company_or_prof.toLowerCase().includes(q) ||
          app.role_or_paper.toLowerCase().includes(q) ||
          app.contact_email.toLowerCase().includes(q)
        )
      }
      return true
    })
  }, [apps, filter, search])

  function exportCSV() {
    const headers = ['Company/Prof', 'Role/Paper', 'Date', 'Email Used', 'Status', 'Reply', 'Follow-up']
    const rows = filtered.map(a => [
      a.company_or_prof, a.role_or_paper, formatDate(a.date_sent),
      a.sent_from, a.status, a.reply_received ? 'Yes' : 'No', a.follow_up_sent ? 'Yes' : 'No',
    ])
    const csv = [headers, ...rows].map(r => r.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `applications-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
  }

  const filterTabs: { key: FilterType; label: string }[] = [
    { key: 'all', label: 'All' },
    { key: 'company', label: 'Companies' },
    { key: 'professor', label: 'Professors' },
    { key: 'manual_pending', label: 'Manual Pending' },
    { key: 'replied', label: 'Replied' },
  ]

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Applications</h1>
          <p className="text-gray-400 text-sm mt-0.5">{filtered.length} of {apps.length} total</p>
        </div>
        <div className="flex gap-2">
          <button onClick={loadApps} className="flex items-center gap-2 px-3 py-2 text-sm text-gray-400 hover:text-white bg-[#0f0f1a] border border-[#1a1a35] rounded-lg transition-colors">
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
          <button onClick={exportCSV} className="flex items-center gap-2 px-3 py-2 text-sm text-indigo-400 hover:text-white bg-indigo-600/10 border border-indigo-600/20 rounded-lg hover:bg-indigo-600/20 transition-colors">
            <Download size={14} />
            Export CSV
          </button>
        </div>
      </div>

      <div className="card p-4 flex flex-col sm:flex-row gap-3">
        <div className="flex gap-1 flex-wrap">
          {filterTabs.map(tab => (
            <button key={tab.key} onClick={() => setFilter(tab.key)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${filter === tab.key ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:text-white hover:bg-[#1a1a35]'}`}>
              {tab.label}
            </button>
          ))}
        </div>
        <div className="relative flex-1 min-w-[200px]">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input type="text" placeholder="Search company, role, email..." value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-sm bg-[#0a0a0f] border border-[#1a1a35] rounded-lg text-white placeholder-gray-600 focus:border-indigo-500 outline-none transition-colors" />
        </div>
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#1a1a35]">
                {['Company / Professor', 'Role / Paper', 'Date', 'Email Account', 'Status', 'Reply', 'Follow-up'].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="border-b border-[#1a1a35]">
                    {Array.from({ length: 7 }).map((_, j) => (
                      <td key={j} className="px-4 py-3"><div className="h-4 bg-[#1a1a35] rounded animate-pulse" /></td>
                    ))}
                  </tr>
                ))
              ) : filtered.length === 0 ? (
                <tr><td colSpan={7} className="text-center py-12 text-gray-500">No applications found.</td></tr>
              ) : (
                filtered.map(app => (
                  <tr key={app.id} className="border-b border-[#1a1a35] hover:bg-[#0f0f1a] transition-colors">
                    <td className="px-4 py-3 font-medium text-white">{app.company_or_prof}</td>
                    <td className="px-4 py-3 text-gray-300 max-w-xs truncate">{app.role_or_paper}</td>
                    <td className="px-4 py-3 text-gray-400 whitespace-nowrap">{formatDate(app.date_sent)}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{app.sent_from}</td>
                    <td className="px-4 py-3"><StatusBadge status={app.status} /></td>
                    <td className="px-4 py-3"><span className={app.reply_received ? 'text-green-400' : 'text-gray-600'}>{app.reply_received ? '✓ Yes' : '—'}</span></td>
                    <td className="px-4 py-3"><span className={app.follow_up_sent ? 'text-yellow-400' : 'text-gray-600'}>{app.follow_up_sent ? '✓ Sent' : '—'}</span></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

'use client'

import { ActivityLog } from '@/lib/supabase'
import { levelColor, levelDot, timeAgo } from '@/lib/utils'

type Props = { logs: ActivityLog[] }

export default function ActivityFeed({ logs }: Props) {
  if (logs.length === 0) {
    return (
      <div className="text-center py-10 text-gray-500 text-sm">
        No activity yet. Start the PA to see logs here.
      </div>
    )
  }

  return (
    <div className="space-y-0 max-h-80 overflow-y-auto pr-1">
      {logs.map((log, index) => (
        <div
          key={log.id}
          className="flex items-start gap-3 py-3 border-b border-[#1a1a35] last:border-0 animate-fade-in"
          style={{ animationDelay: `${index * 30}ms` }}
        >
          <div className="mt-1.5 shrink-0">
            <div className={`w-2 h-2 rounded-full ${levelDot(log.level)}`} />
          </div>
          <div className="flex-1 min-w-0">
            <p className={`text-sm ${levelColor(log.level)}`}>{log.description}</p>
            {log.details && Object.keys(log.details).length > 0 && (
              <p className="text-xs text-gray-600 mt-0.5">
                {Object.entries(log.details).map(([k, v]) => `${k}: ${v}`).join(' · ')}
              </p>
            )}
          </div>
          <span className="text-xs text-gray-600 shrink-0 mt-0.5">{timeAgo(log.created_at)}</span>
        </div>
      ))}
    </div>
  )
}

import { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

type Props = {
  label: string
  value: number | string
  icon: LucideIcon
  color?: 'blue' | 'green' | 'yellow' | 'purple' | 'red'
  change?: string
}

const colorMap = {
  blue:   'bg-blue-500/15 text-blue-400',
  green:  'bg-green-500/15 text-green-400',
  yellow: 'bg-yellow-500/15 text-yellow-400',
  purple: 'bg-indigo-500/15 text-indigo-400',
  red:    'bg-red-500/15 text-red-400',
}

export default function StatCard({ label, value, icon: Icon, color = 'blue', change }: Props) {
  return (
    <div className="card p-5 hover:border-[#252550] transition-colors">
      <div className="flex items-start justify-between">
        <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center', colorMap[color])}>
          <Icon size={18} />
        </div>
        {change && <span className="text-xs text-gray-500">{change}</span>}
      </div>
      <p className="text-3xl font-bold text-white mt-3">{value}</p>
      <p className="text-sm text-gray-400 mt-1">{label}</p>
    </div>
  )
}

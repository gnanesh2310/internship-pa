import { statusColor } from '@/lib/utils'
import { cn } from '@/lib/utils'

type Props = { status: string }

const statusLabel: Record<string, string> = {
  sent:           'Sent',
  replied:        'Replied',
  follow_up_sent: 'Follow-up Sent',
  manual_needed:  'Manual Needed',
  failed:         'Failed',
}

export default function StatusBadge({ status }: Props) {
  return (
    <span className={cn(
      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
      statusColor(status)
    )}>
      {statusLabel[status] ?? status}
    </span>
  )
}

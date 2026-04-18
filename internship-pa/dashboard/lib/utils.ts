import { clsx, type ClassValue } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-IN', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function timeAgo(dateString: string): string {
  const now = new Date()
  const date = new Date(dateString)
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  return `${diffDays}d ago`
}

export function isUrgent(deadline: string | null): boolean {
  if (!deadline) return false
  const now = new Date()
  const deadlineDate = new Date(deadline)
  const diffDays = (deadlineDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
  return diffDays <= 7 && diffDays >= 0
}

export function statusColor(status: string): string {
  const map: Record<string, string> = {
    sent: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    replied: 'bg-green-500/20 text-green-400 border-green-500/30',
    follow_up_sent: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    manual_needed: 'bg-red-500/20 text-red-400 border-red-500/30',
    failed: 'bg-red-500/20 text-red-400 border-red-500/30',
  }
  return map[status] ?? 'bg-gray-500/20 text-gray-400 border-gray-500/30'
}

export function levelColor(level: string): string {
  const map: Record<string, string> = {
    info: 'text-blue-400',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    error: 'text-red-400',
  }
  return map[level] ?? 'text-gray-400'
}

export function levelDot(level: string): string {
  const map: Record<string, string> = {
    info: 'bg-blue-400',
    success: 'bg-green-400',
    warning: 'bg-yellow-400',
    error: 'bg-red-400',
  }
  return map[level] ?? 'bg-gray-400'
}

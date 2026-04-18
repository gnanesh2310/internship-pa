'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, FileText, AlertCircle, User, Settings, Bot, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'

const navLinks = [
  { href: '/',             icon: LayoutDashboard, label: 'Home' },
  { href: '/applications', icon: FileText,         label: 'Applications' },
  { href: '/manual-queue', icon: AlertCircle,      label: 'Manual Queue' },
  { href: '/profile',      icon: User,             label: 'Profile' },
  { href: '/settings',     icon: Settings,         label: 'Settings' },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-60 bg-[#0f0f1a] border-r border-[#1a1a35] flex flex-col py-6 px-4 shrink-0">
      <div className="flex items-center gap-3 px-2 mb-8">
        <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center">
          <Bot size={20} className="text-white" />
        </div>
        <div>
          <p className="font-semibold text-sm text-white">Internship PA</p>
          <p className="text-xs text-gray-500">Gnanesh&apos;s bot</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1">
        {navLinks.map(({ href, icon: Icon, label }) => {
          const isActive = pathname === href
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-150',
                isActive
                  ? 'bg-indigo-600/20 text-indigo-400 font-medium'
                  : 'text-gray-400 hover:text-white hover:bg-[#1a1a35]'
              )}
            >
              <Icon size={17} />
              {label}
            </Link>
          )
        })}
      </nav>

      <div className="px-2 pt-4 border-t border-[#1a1a35]">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs text-gray-400">PA Running</span>
          <Zap size={12} className="ml-auto text-yellow-400" />
        </div>
      </div>
    </aside>
  )
}

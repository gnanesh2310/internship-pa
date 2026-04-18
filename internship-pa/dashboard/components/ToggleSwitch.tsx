'use client'

type Props = {
  label: string
  description?: string
  enabled: boolean
  onChange: (enabled: boolean) => void
  loading?: boolean
}

export default function ToggleSwitch({ label, description, enabled, onChange, loading }: Props) {
  return (
    <div className="flex items-center justify-between py-3">
      <div>
        <p className="text-sm font-medium text-white">{label}</p>
        {description && <p className="text-xs text-gray-500 mt-0.5">{description}</p>}
      </div>
      <button
        onClick={() => !loading && onChange(!enabled)}
        disabled={loading}
        className={`relative w-11 h-6 rounded-full transition-all duration-200 focus:outline-none
          ${enabled ? 'bg-indigo-600' : 'bg-[#252550]'}
          ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        aria-label={`${label}: ${enabled ? 'on' : 'off'}`}
      >
        <span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-all duration-200
          ${enabled ? 'left-5' : 'left-0.5'}`} />
      </button>
    </div>
  )
}

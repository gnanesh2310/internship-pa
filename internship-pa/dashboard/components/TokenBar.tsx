type Props = {
  tokensUsed: number
  tokensLimit: number
  provider?: string
}

export default function TokenBar({ tokensUsed, tokensLimit, provider = 'Gemini' }: Props) {
  const pct = Math.min((tokensUsed / tokensLimit) * 100, 100)
  const barColor = pct < 60 ? 'bg-green-500' : pct < 80 ? 'bg-yellow-500' : 'bg-red-500'
  const textColor = pct < 60 ? 'text-green-400' : pct < 80 ? 'text-yellow-400' : 'text-red-400'

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between items-center">
        <span className="text-xs text-gray-400">{provider} API Usage</span>
        <span className={`text-xs font-medium ${textColor}`}>{pct.toFixed(1)}%</span>
      </div>
      <div className="h-2 bg-[#1a1a35] rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-500 ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
      <div className="flex justify-between text-xs text-gray-600">
        <span>{tokensUsed.toLocaleString()} used</span>
        <span>{tokensLimit.toLocaleString()} limit</span>
      </div>
    </div>
  )
}

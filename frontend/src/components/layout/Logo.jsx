export default function Logo({ size = 'md', white = false }) {
  const sizes = { sm: 28, md: 36, lg: 48 }
  const s = sizes[size]
  const textClass = white ? 'text-white' : 'text-[#1E3A5F]'
  const subClass = white ? 'text-blue-200' : 'text-slate-500'

  return (
    <div className="flex items-center gap-2.5">
      <svg width={s} height={s} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        {/* Hexagon background */}
        <path d="M20 2L36 11V29L20 38L4 29V11L20 2Z"
              fill={white ? 'rgba(255,255,255,0.15)' : '#1E3A5F'}
              stroke={white ? 'rgba(255,255,255,0.4)' : 'none'} strokeWidth="1"/>
        {/* M letter mark */}
        <path d="M11 27V13L20 21L29 13V27"
              stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
        {/* Data dot accent */}
        <circle cx="20" cy="21" r="2.5" fill="#38bdf8"/>
        {/* Chart bars */}
        <rect x="13" y="22" width="3" height="5" rx="1" fill="rgba(255,255,255,0.5)"/>
        <rect x="18.5" y="19" width="3" height="8" rx="1" fill="rgba(255,255,255,0.7)"/>
        <rect x="24" y="21" width="3" height="6" rx="1" fill="rgba(255,255,255,0.5)"/>
      </svg>
      <div>
        <div className={`font-bold leading-tight tracking-tight ${textClass} ${size === 'lg' ? 'text-xl' : size === 'sm' ? 'text-sm' : 'text-base'}`}>
          Murex Insights
        </div>
        {size !== 'sm' && (
          <div className={`text-xs leading-none mt-0.5 ${subClass}`}>Survey Platform</div>
        )}
      </div>
    </div>
  )
}

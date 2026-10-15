import { cn } from '../../lib/cn'

interface ProgressBarProps {
  value: number
  tone?: 'accent' | 'success' | 'muted'
  size?: 'xs' | 'sm'
  label?: string
  className?: string
}

const tones = {
  accent: 'bg-accent',
  success: 'bg-success',
  muted: 'bg-subtle',
}

export function ProgressBar({ value, tone = 'accent', size = 'sm', label, className }: ProgressBarProps) {
  const pct = Math.round(Math.min(Math.max(value, 0), 1) * 100)
  return (
    <div
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={pct}
      aria-label={label}
      className={cn('w-full overflow-hidden rounded-full bg-elevated', size === 'xs' ? 'h-1' : 'h-1.5', className)}
    >
      <div
        className={cn('h-full origin-left rounded-full animate-fill transition-[width] duration-500', tones[tone])}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}

interface RingProps {
  value: number
  size?: number
  stroke?: number
  label?: string
  children?: React.ReactNode
}

export function ProgressRing({ value, size = 64, stroke = 5, label, children }: RingProps) {
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const clamped = Math.min(Math.max(value, 0), 1)
  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90" role="img" aria-label={label}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" strokeWidth={stroke} className="stroke-elevated" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - clamped)}
          className="stroke-accent transition-[stroke-dashoffset] duration-700"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">{children}</div>
    </div>
  )
}

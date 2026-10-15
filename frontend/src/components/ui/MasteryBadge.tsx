import { MASTERY_LABEL } from '../../lib/progress'
import { cn } from '../../lib/cn'
import type { MasteryStatus } from '../../types'

const styles: Record<MasteryStatus, string> = {
  not_started: 'text-subtle',
  in_progress: 'text-accent-strong',
  mastered: 'text-success',
}

const dots: Record<MasteryStatus, string> = {
  not_started: 'border border-subtle',
  in_progress: 'bg-accent',
  mastered: 'bg-success',
}

export function MasteryBadge({ status, className }: { status: MasteryStatus; className?: string }) {
  return (
    <span className={cn('inline-flex items-center gap-1.5 text-[12px] font-medium', styles[status], className)}>
      <span className={cn('size-1.5 rounded-full', dots[status])} aria-hidden="true" />
      {MASTERY_LABEL[status]}
    </span>
  )
}

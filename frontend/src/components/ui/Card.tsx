import type { HTMLAttributes, ReactNode } from 'react'
import { cn } from '../../lib/cn'

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('rounded-[var(--radius-card)] border border-line bg-surface', className)}
      {...props}
    />
  )
}

interface SectionHeaderProps {
  title: string
  description?: ReactNode
  action?: ReactNode
  as?: 'h2' | 'h3'
}

export function SectionHeader({ title, description, action, as: Heading = 'h2' }: SectionHeaderProps) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-x-4 gap-y-2">
      <div className="min-w-0">
        <Heading className="text-[15px] font-semibold tracking-tight text-fg">{title}</Heading>
        {description && <p className="mt-0.5 text-[13px] text-muted">{description}</p>}
      </div>
      {action}
    </div>
  )
}

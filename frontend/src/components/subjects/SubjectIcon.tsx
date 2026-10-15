import { BookOpen, Code2, Sigma, type LucideIcon } from 'lucide-react'
import { cn } from '../../lib/cn'

const ICONS: Record<string, LucideIcon> = {
  informatics: Code2,
  math: Sigma,
}

export function SubjectIcon({ slug, className }: { slug: string; className?: string }) {
  const Icon = ICONS[slug] ?? BookOpen
  return (
    <span className={cn('grid size-9 shrink-0 place-items-center rounded-lg border border-line-strong bg-surface-2 text-accent-strong', className)} aria-hidden="true">
      <Icon className="size-[18px]" />
    </span>
  )
}

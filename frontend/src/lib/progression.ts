import type { ProgressStats } from '../types'

/** Формула совпадает с backend/app/services/profile_service.py: порог выхода с уровня L. */
export function xpForLevel(level: number): number {
  return Math.floor((100 * level * (level + 1)) / 2)
}

export function calculateLevel(xp: number): number {
  let level = 1
  while (xp >= xpForLevel(level)) level += 1
  return level
}

export interface LevelProgress {
  level: number
  xp: number
  floor: number
  ceil: number
  ratio: number
  remaining: number
}

export function levelProgress(xp: number, level = calculateLevel(xp)): LevelProgress {
  const floor = level > 1 ? xpForLevel(level - 1) : 0
  const ceil = xpForLevel(level)
  const span = Math.max(ceil - floor, 1)
  return {
    level,
    xp,
    floor,
    ceil,
    ratio: Math.min(Math.max((xp - floor) / span, 0), 1),
    remaining: Math.max(ceil - xp, 0),
  }
}

/* Ранг по предмету — отдельная от глобального уровня сущность, зависит только от прогресса в предмете. */

export interface SubjectRank {
  index: number
  title: string
  /** Минимальная доля решённых задач предмета */
  threshold: number
}

export const SUBJECT_RANKS: SubjectRank[] = [
  { index: 0, title: 'Новичок', threshold: 0 },
  { index: 1, title: 'Ученик', threshold: 0.1 },
  { index: 2, title: 'Практик', threshold: 0.25 },
  { index: 3, title: 'Знаток', threshold: 0.45 },
  { index: 4, title: 'Эксперт', threshold: 0.7 },
  { index: 5, title: 'Мейстер', threshold: 0.9 },
]

export interface SubjectRankProgress {
  rank: SubjectRank
  next: SubjectRank | null
  /** Прогресс внутри текущего ранга, 0–1 */
  ratio: number
}

export function subjectRank(stats: ProgressStats): SubjectRankProgress | null {
  if (stats.totalTasks === 0) return null
  const completion = stats.completion
  let current = SUBJECT_RANKS[0]
  for (const rank of SUBJECT_RANKS) if (completion >= rank.threshold) current = rank
  const next = SUBJECT_RANKS[current.index + 1] ?? null
  const ratio = next ? (completion - current.threshold) / (next.threshold - current.threshold) : 1
  return { rank: current, next, ratio: Math.min(Math.max(ratio, 0), 1) }
}

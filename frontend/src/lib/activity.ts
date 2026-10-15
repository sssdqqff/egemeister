import type { ActivityDay } from '../types'
import { addDays, startOfDay, toDateKey } from './dates'

export type HeatLevel = 0 | 1 | 2 | 3 | 4

/** Уровни интенсивности — по числу попыток за день. */
export function heatLevel(day: ActivityDay | undefined): HeatLevel {
  const value = day?.attempts ?? 0
  if (value === 0) return 0
  if (value < 6) return 1
  if (value < 14) return 2
  if (value < 25) return 3
  return 4
}

export function indexActivity(days: ActivityDay[]): Map<string, ActivityDay> {
  return new Map(days.map((day) => [day.date, day]))
}

export interface PeriodSummary {
  activeDays: number
  totalDays: number
  attempts: number
  correct: number
  xp: number
  minutes: number
}

export function summarizePeriod(
  index: Map<string, ActivityDay>,
  from: Date,
  to: Date,
): PeriodSummary {
  const summary: PeriodSummary = { activeDays: 0, totalDays: 0, attempts: 0, correct: 0, xp: 0, minutes: 0 }
  for (let d = startOfDay(from); d <= to; d = addDays(d, 1)) {
    summary.totalDays += 1
    const day = index.get(toDateKey(d))
    if (!day || day.attempts === 0) continue
    summary.activeDays += 1
    summary.attempts += day.attempts
    summary.correct += day.correct
    summary.xp += day.xp
    summary.minutes += day.minutes
  }
  return summary
}

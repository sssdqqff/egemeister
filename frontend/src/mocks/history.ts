import { toTestScore } from '../lib/scoreScales'
import { addDays, startOfDay, toDateKey } from '../lib/dates'
import type { ActivityDay, Attempt, Difficulty, MockExamResult, Task } from '../types'
import { createRng } from './generators/shared'

export const DEMO_CURRENT_STREAK = 12
export const DEMO_BEST_STREAK = 23
const HISTORY_DAYS = 371
const REGISTERED_DAYS_AGO = 286

/** Демо-правило начисления XP: только за первое верное решение задачи. */
export const DEMO_XP_REWARD: Record<Difficulty, number> = { easy: 5, medium: 8, hard: 12 }

export function demoRegistrationDate(today = new Date()): Date {
  return addDays(startOfDay(today), -REGISTERED_DAYS_AGO)
}

/**
 * История активности генерируется детерминированно и согласована с заявленными
 * стриками: текущая серия длится DEMO_CURRENT_STREAK дней, лучшая — DEMO_BEST_STREAK.
 */
export function buildDemoActivity(today = new Date()): ActivityDay[] {
  const rng = createRng(20260101)
  const end = startOfDay(today)
  const active = new Array<boolean>(HISTORY_DAYS).fill(false)
  const last = HISTORY_DAYS - 1
  const registered = last - REGISTERED_DAYS_AGO

  let on = false
  for (let i = registered; i <= last; i += 1) {
    const date = addDays(end, i - last)
    const weekend = date.getDay() === 0 || date.getDay() === 6
    on = on ? rng.chance(weekend ? 0.66 : 0.8) : rng.chance(weekend ? 0.25 : 0.45)
    active[i] = on
  }

  const bestStart = registered + 110
  const bestEnd = bestStart + DEMO_BEST_STREAK - 1
  for (let i = bestStart; i <= bestEnd; i += 1) active[i] = true
  active[bestStart - 1] = false
  active[bestEnd + 1] = false

  const currentStart = last - DEMO_CURRENT_STREAK + 1
  for (let i = currentStart; i <= last; i += 1) active[i] = true
  active[currentStart - 1] = false

  let runStart = -1
  for (let i = 0; i <= last + 1; i += 1) {
    if (i <= last && active[i]) {
      if (runStart < 0) runStart = i
      continue
    }
    if (runStart >= 0) {
      const isProtected = runStart === bestStart || runStart === currentStart
      if (!isProtected) {
        for (let j = runStart + 18; j < i; j += 19) active[j] = false
      }
      runStart = -1
    }
  }

  const days: ActivityDay[] = []
  for (let i = 0; i <= last; i += 1) {
    const date = addDays(end, i - last)
    if (!active[i]) {
      days.push({ date: toDateKey(date), attempts: 0, correct: 0, xp: 0, minutes: 0 })
      continue
    }
    const intensity = rng.next()
    const attempts = intensity < 0.35 ? rng.int(2, 6) : intensity < 0.75 ? rng.int(7, 15) : rng.int(16, 34)
    const correct = Math.round(attempts * (0.55 + rng.next() * 0.35))
    days.push({
      date: toDateKey(date),
      attempts,
      correct,
      xp: correct * rng.int(4, 8),
      minutes: attempts * rng.int(2, 4),
    })
  }
  return days
}

/** Стартовые попытки по каталогу: разные задания на разных стадиях освоения. */
const TOPIC_COVERAGE: Record<number, number> = {
  111: 1,
  114: 0.85,
  115: 0.75,
  116: 0.6,
  105: 0.5,
  107: 0.3,
  108: 0.15,
  206: 0.45,
}

export function buildDemoAttempts(
  tasks: Task[],
  answers: Map<number, string>,
  activity: ActivityDay[],
): Attempt[] {
  const rng = createRng(4242)
  const activeDates = activity.filter((d) => d.attempts > 0).slice(-40).map((d) => d.date)
  const attempts: Attempt[] = []
  const entries: { taskId: number; answer: string; correct: boolean }[] = []

  for (const task of tasks) {
    const coverage = TOPIC_COVERAGE[task.topic_id]
    if (!coverage || !rng.chance(coverage)) continue
    const answer = answers.get(task.id) ?? ''
    const skill = coverage
    if (!rng.chance(skill)) entries.push({ taskId: task.id, answer: wrongAnswer(answer, rng.int(1, 9)), correct: false })
    if (rng.chance(0.2 + skill * 0.6)) entries.push({ taskId: task.id, answer, correct: true })
    else entries.push({ taskId: task.id, answer: wrongAnswer(answer, rng.int(10, 40)), correct: false })
  }

  entries.forEach((entry, i) => {
    const dateKey = activeDates[Math.min(Math.floor((i / entries.length) * activeDates.length), activeDates.length - 1)]
    const [y, m, d] = dateKey.split('-').map(Number)
    attempts.push({
      id: i + 1,
      task_id: entry.taskId,
      session_id: null,
      user_answer: entry.answer,
      is_correct: entry.correct,
      created_at: new Date(y, m - 1, d, 17 + (i % 5), (i * 7) % 60).toISOString(),
    })
  })
  return attempts
}

function wrongAnswer(answer: string, delta: number): string {
  const n = Number(answer)
  if (Number.isFinite(n) && answer.trim() !== '') {
    return Number.isInteger(n) ? String(n + delta) : String(Math.round((n + delta / 100) * 100) / 100)
  }
  return `${answer}${delta}`
}

export function buildDemoMockExams(today = new Date()): MockExamResult[] {
  const results: [number, number][] = [
    [128, 13],
    [97, 16],
    [66, 17],
    [38, 20],
    [12, 22],
  ]
  return results.map(([daysAgo, primary], i) => ({
    id: `demo-${i + 1}`,
    subjectId: 1,
    date: toDateKey(addDays(today, -daysAgo)),
    title: `Пробник №${i + 1}`,
    primaryScore: primary,
    maxPrimaryScore: 29,
    testScore: toTestScore('informatics', primary) ?? 0,
  }))
}

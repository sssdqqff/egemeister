import type { Attempt, MasteryStatus, ProgressStats, Task, UserTaskProgress } from '../types'

export type ProgressIndex = Map<number, UserTaskProgress>

/** Попытки упорядочиваются по id: так же их создаёт backend. */
export function buildProgressIndex(attempts: Attempt[]): ProgressIndex {
  const index: ProgressIndex = new Map()
  const sorted = [...attempts].sort((a, b) => a.id - b.id)
  for (const attempt of sorted) {
    const entry = index.get(attempt.task_id) ?? {
      taskId: attempt.task_id,
      attempts: [],
      correctAttempts: 0,
      solved: false,
      lastAnswer: null,
      lastResult: null,
    }
    entry.attempts.push(attempt)
    if (attempt.is_correct) {
      entry.correctAttempts += 1
      entry.solved = true
    }
    entry.lastAnswer = attempt.user_answer
    entry.lastResult = attempt.is_correct
    index.set(attempt.task_id, entry)
  }
  return index
}

/** Статистика по набору уникальных задач — исключает двойной учёт. */
export function computeStats(tasks: Task[], index: ProgressIndex): ProgressStats {
  const unique = new Map(tasks.map((task) => [task.id, task]))
  let solvedTasks = 0
  let attemptedTasks = 0
  let attempts = 0
  let correctAttempts = 0
  for (const id of unique.keys()) {
    const progress = index.get(id)
    if (!progress) continue
    attemptedTasks += 1
    attempts += progress.attempts.length
    correctAttempts += progress.correctAttempts
    if (progress.solved) solvedTasks += 1
  }
  const totalTasks = unique.size
  return {
    totalTasks,
    solvedTasks,
    attemptedTasks,
    attempts,
    correctAttempts,
    accuracy: attempts > 0 ? correctAttempts / attempts : null,
    completion: totalTasks > 0 ? solvedTasks / totalTasks : 0,
  }
}

export const MASTERY_THRESHOLDS = {
  /** Доля решённых задач задания */
  completion: 0.7,
  /** Доля верных попыток */
  accuracy: 0.75,
} as const

export function masteryStatus(stats: ProgressStats): MasteryStatus {
  if (stats.attempts === 0) return 'not_started'
  if (
    stats.completion >= MASTERY_THRESHOLDS.completion &&
    (stats.accuracy ?? 0) >= MASTERY_THRESHOLDS.accuracy
  ) {
    return 'mastered'
  }
  return 'in_progress'
}

export const MASTERY_LABEL: Record<MasteryStatus, string> = {
  not_started: 'Не начато',
  in_progress: 'В процессе',
  mastered: 'Освоено',
}

export function percent(value: number | null): string {
  if (value === null) return '—'
  return `${Math.round(value * 100)}%`
}

/* Сущности, совпадающие с ответами FastAPI (backend/app/schemas). */

export type Difficulty = 'easy' | 'medium' | 'hard'

export interface User {
  id: number
  telegram_id: number | null
  first_name: string | null
  username: string | null
  email: string | null
  is_active: boolean
  role: 'user' | 'admin'
  created_at: string
}

export interface Profile {
  id: number
  avatar_url: string | null
  xp: number
  level: number
  streak: number
  last_login: string | null
}

export interface Subject {
  id: number
  name: string
  slug: string
  description: string
  is_active: boolean
}

/** Номер задания КИМ ЕГЭ (в backend — Topic). */
export interface Topic {
  id: number
  number: number
  name: string
  slug: string
  description: string | null
  is_active: boolean
  subject_id: number
}

/** Тип задач внутри одного номера задания. */
export interface Prototype {
  id: number
  name: string
  code: string
  description: string | null
  exam_number: number
  is_active: boolean
}

export interface Task {
  id: number
  condition: string
  difficulty: Difficulty
  is_active: boolean
  topic_id: number
  prototype_id: number
  /** Нет в API — заполняется только демо-каталогом. */
  hint?: string
  /** Нет в API — заполняется только демо-каталогом. */
  solution?: string
}

export interface Attempt {
  id: number
  task_id: number
  session_id: number | null
  user_answer: string
  is_correct: boolean
  /** Нет в AttemptResponse — заполняется только демо-слоем. */
  created_at?: string
}

export interface AttemptCreate {
  task_id: number
  user_answer: string
  session_id?: number | null
}

/* Производные сущности, вычисляемые на клиенте. */

export interface UserTaskProgress {
  taskId: number
  attempts: Attempt[]
  correctAttempts: number
  solved: boolean
  lastAnswer: string | null
  lastResult: boolean | null
}

export interface ProgressStats {
  totalTasks: number
  solvedTasks: number
  attemptedTasks: number
  attempts: number
  correctAttempts: number
  /** Доля верных попыток, null — если попыток не было. */
  accuracy: number | null
  /** Доля решённых задач от общего числа. */
  completion: number
}

export type MasteryStatus = 'not_started' | 'in_progress' | 'mastered'

export interface ActivityDay {
  /** YYYY-MM-DD в локальном времени */
  date: string
  attempts: number
  correct: number
  xp: number
  minutes: number
}

export interface StreakInfo {
  current: number
  best: number | null
}

export type AchievementIcon = 'spark' | 'flame' | 'target' | 'trophy' | 'medal' | 'star' | 'award'

export interface Achievement {
  id: string
  title: string
  description: string
  icon: AchievementIcon
  unlocked: boolean
  progress: { current: number; target: number } | null
}

export interface MockExamResult {
  id: string
  subjectId: number
  date: string
  title: string
  /** Первичный балл (сумма баллов за задания КИМ). */
  primaryScore: number
  maxPrimaryScore: number
  /** Тестовый балл по 100-балльной шкале. */
  testScore: number
}

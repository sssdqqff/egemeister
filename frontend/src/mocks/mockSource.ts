import { isAnswerCorrect } from '../lib/answers'
import { toDateKey } from '../lib/dates'
import { calculateLevel } from '../lib/progression'
import type { CatalogSource, InsightsSource } from '../services/types'
import type { ActivityDay, Attempt, MockExamResult, Profile, User } from '../types'
import { demoCatalog } from './catalog'
import {
  buildDemoActivity,
  buildDemoAttempts,
  buildDemoMockExams,
  DEMO_BEST_STREAK,
  DEMO_CURRENT_STREAK,
  DEMO_XP_REWARD,
  demoRegistrationDate,
} from './history'

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

/** Состояние демо-режима живёт только в памяти вкладки и сбрасывается при перезагрузке. */
const state = (() => {
  const activity = buildDemoActivity()
  const attempts = buildDemoAttempts(demoCatalog.tasks, demoCatalog.answers, activity)
  return {
    signedIn: true,
    activity: new Map<string, ActivityDay>(activity.map((day) => [day.date, day])),
    attempts,
    xp: activity.reduce((sum, day) => sum + day.xp, 0),
    exams: buildDemoMockExams(),
  }
})()

const demoUser: User = {
  id: 1,
  telegram_id: 100200300,
  first_name: 'Егор',
  username: 'egor_k',
  email: null,
  is_active: true,
  role: 'user',
  created_at: demoRegistrationDate().toISOString(),
}

function requireSession() {
  if (!state.signedIn) throw new Error('Требуется вход')
}

export const mockCatalog: CatalogSource = {
  async getCurrentUser() {
    await delay(200)
    return state.signedIn ? demoUser : null
  },
  async login(code) {
    await delay(500)
    if (!/^\d{4,12}$/.test(code)) throw new Error('Неверный код')
    state.signedIn = true
    return demoUser
  },
  async logout() {
    await delay(150)
    state.signedIn = false
  },
  async getProfile(): Promise<Profile> {
    await delay(250)
    requireSession()
    return {
      id: 1,
      avatar_url: null,
      xp: state.xp,
      level: calculateLevel(state.xp),
      streak: DEMO_CURRENT_STREAK,
      last_login: new Date().toISOString(),
    }
  },
  async getSubjects() {
    await delay(250)
    return demoCatalog.subjects
  },
  async getTopics() {
    await delay(250)
    return demoCatalog.topics
  },
  async getPrototypes() {
    await delay(250)
    return demoCatalog.prototypes
  },
  async getTasks() {
    await delay(300)
    return demoCatalog.tasks
  },
  async getAttempts() {
    await delay(250)
    requireSession()
    return [...state.attempts]
  },
  async submitAttempt(input) {
    await delay(450)
    requireSession()
    const task = demoCatalog.tasks.find((t) => t.id === input.task_id)
    const answer = demoCatalog.answers.get(input.task_id)
    if (!task || answer === undefined) throw new Error('Задача не найдена')

    const correct = isAnswerCorrect(answer, input.user_answer)
    const alreadySolved = state.attempts.some((a) => a.task_id === task.id && a.is_correct)
    const reward = correct && !alreadySolved ? DEMO_XP_REWARD[task.difficulty] : 0
    const attempt: Attempt = {
      id: state.attempts.length + 1,
      task_id: task.id,
      session_id: input.session_id ?? null,
      user_answer: input.user_answer,
      is_correct: correct,
      created_at: new Date().toISOString(),
    }
    state.attempts.push(attempt)
    state.xp += reward

    const key = toDateKey(new Date())
    const today = state.activity.get(key) ?? { date: key, attempts: 0, correct: 0, xp: 0, minutes: 0 }
    state.activity.set(key, {
      ...today,
      attempts: today.attempts + 1,
      correct: today.correct + (correct ? 1 : 0),
      xp: today.xp + reward,
      minutes: today.minutes + 2,
    })
    return attempt
  },
}

export const mockInsights: InsightsSource = {
  async getActivity() {
    await delay(300)
    return [...state.activity.values()].sort((a, b) => a.date.localeCompare(b.date))
  },
  async getBestStreak() {
    return DEMO_BEST_STREAK
  },
  async getMockExams() {
    await delay(250)
    return [...state.exams]
  },
  async addMockExam(input: Omit<MockExamResult, 'id'>) {
    await delay(300)
    const result = { ...input, id: `demo-${Date.now()}` }
    state.exams.push(result)
    return result
  },
}

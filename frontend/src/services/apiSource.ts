import type { Attempt, AttemptCreate, Profile, Prototype, Subject, Task, Topic, User } from '../types'
import { ApiError, http } from './http'
import type { CatalogSource } from './types'

export const apiSource: CatalogSource = {
  async getCurrentUser() {
    try {
      return await http<User>('/users/me')
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) return null
      throw error
    }
  },
  login: (code) =>
    http<User>('/auth/telegram/exchange', { method: 'POST', body: JSON.stringify({ code }) }),
  logout: () => http<void>('/auth/logout', { method: 'POST' }),
  getProfile: () => http<Profile>('/profile'),
  getSubjects: () => http<Subject[]>('/subjects'),
  getTopics: () => http<Topic[]>('/topics'),
  getPrototypes: () => http<Prototype[]>('/prototypes'),
  getTasks: () => http<Task[]>('/tasks'),
  getAttempts: () => http<Attempt[]>('/attempts'),
  submitAttempt: (input: AttemptCreate) =>
    http<Attempt>('/attempts', { method: 'POST', body: JSON.stringify(input) }),
}

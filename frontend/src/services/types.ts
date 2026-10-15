import type {
  ActivityDay,
  Attempt,
  AttemptCreate,
  MockExamResult,
  Profile,
  Prototype,
  Subject,
  Task,
  Topic,
  User,
} from '../types'

/** Контракт, который реализуют и FastAPI-адаптер, и демо-слой. */
export interface CatalogSource {
  getCurrentUser(): Promise<User | null>
  login(code: string): Promise<User>
  logout(): Promise<void>
  getProfile(): Promise<Profile>
  getSubjects(): Promise<Subject[]>
  getTopics(): Promise<Topic[]>
  getPrototypes(): Promise<Prototype[]>
  getTasks(): Promise<Task[]>
  getAttempts(): Promise<Attempt[]>
  submitAttempt(input: AttemptCreate): Promise<Attempt>
}

/**
 * Данные, для которых в backend пока нет эндпоинтов.
 * null означает «недоступно в текущем режиме» — UI показывает пустое состояние.
 */
export interface InsightsSource {
  getActivity(): Promise<ActivityDay[] | null>
  getBestStreak(): Promise<number | null>
  getMockExams(): Promise<MockExamResult[]>
  addMockExam(input: Omit<MockExamResult, 'id'>): Promise<MockExamResult>
}

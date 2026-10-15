import { IS_DEMO } from '../config'
import { mockCatalog, mockInsights } from '../mocks/mockSource'
import type { MockExamResult } from '../types'
import { apiSource } from './apiSource'
import type { CatalogSource, InsightsSource } from './types'

/**
 * В режиме api для активности и пробников эндпоинтов нет — UI получает null/пустые списки
 * и показывает пустые состояния. Результаты пробников живут только в памяти вкладки.
 */
const sessionExams: MockExamResult[] = []

const apiInsights: InsightsSource = {
  getActivity: async () => null,
  getBestStreak: async () => null,
  getMockExams: async () => [...sessionExams],
  addMockExam: async (input) => {
    const result = { ...input, id: `session-${Date.now()}` }
    sessionExams.push(result)
    return result
  },
}

export const catalog: CatalogSource = IS_DEMO ? mockCatalog : apiSource
export const insights: InsightsSource = IS_DEMO ? mockInsights : apiInsights

import { useCallback, useMemo } from 'react'
import useSWR, { useSWRConfig } from 'swr'
import { buildProgressIndex } from '../lib/progress'
import { catalog, insights } from '../services'
import type { AttemptCreate, MockExamResult, Prototype, Subject, Task, Topic } from '../types'

export interface Catalog {
  subjects: Subject[]
  topics: Topic[]
  prototypes: Prototype[]
  tasks: Task[]
}

const swrOptions = { revalidateOnFocus: false }

export function useCatalog() {
  return useSWR<Catalog>(
    'catalog',
    async () => {
      const [subjects, topics, prototypes, tasks] = await Promise.all([
        catalog.getSubjects(),
        catalog.getTopics(),
        catalog.getPrototypes(),
        catalog.getTasks(),
      ])
      return {
        subjects: subjects.filter((s) => s.is_active),
        topics: topics.filter((t) => t.is_active).sort((a, b) => a.number - b.number),
        prototypes: prototypes.filter((p) => p.is_active),
        tasks: tasks.filter((t) => t.is_active),
      }
    },
    swrOptions,
  )
}

export function useAttempts() {
  return useSWR('attempts', () => catalog.getAttempts(), swrOptions)
}

export function useProgressIndex() {
  const { data, error, isLoading, mutate } = useAttempts()
  const index = useMemo(() => buildProgressIndex(data ?? []), [data])
  return { index, attempts: data, error, isLoading, mutate }
}

export function useProfile() {
  return useSWR('profile', () => catalog.getProfile(), swrOptions)
}

export function useActivity() {
  return useSWR('activity', () => insights.getActivity(), swrOptions)
}

export function useBestStreak() {
  return useSWR('best-streak', () => insights.getBestStreak(), swrOptions)
}

export function useMockExams() {
  return useSWR('mock-exams', () => insights.getMockExams(), swrOptions)
}

export function useSubmitAttempt() {
  const { mutate } = useSWRConfig()
  return useCallback(
    async (input: AttemptCreate) => {
      const attempt = await catalog.submitAttempt(input)
      await Promise.all([mutate('attempts'), mutate('profile'), mutate('activity')])
      return attempt
    },
    [mutate],
  )
}

export function useAddMockExam() {
  const { mutate } = useSWRConfig()
  return useCallback(
    async (input: Omit<MockExamResult, 'id'>) => {
      const result = await insights.addMockExam(input)
      await mutate('mock-exams')
      return result
    },
    [mutate],
  )
}

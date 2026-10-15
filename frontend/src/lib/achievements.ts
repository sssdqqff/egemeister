import type { Achievement, AchievementIcon } from '../types'

export interface AchievementInput {
  solvedTasks: number
  activeDays: number | null
  bestStreak: number | null
  completedPrototypes: number
  masteredTopics: number
  firstTrySolved: number
  mockExams: number
}

interface Rule {
  id: string
  title: string
  description: string
  icon: AchievementIcon
  value: (input: AchievementInput) => number | null
  target: number
}

const RULES: Rule[] = [
  { id: 'first-day', title: 'Первый день', description: 'Позанимайтесь на платформе хотя бы один день.', icon: 'spark', value: (i) => i.activeDays, target: 1 },
  { id: 'first-set', title: 'Первый набор', description: 'Решите все задачи одного прототипа.', icon: 'target', value: (i) => i.completedPrototypes, target: 1 },
  { id: 'streak-7', title: 'Неделя подряд', description: 'Занимайтесь 7 дней без пропусков.', icon: 'flame', value: (i) => i.bestStreak, target: 7 },
  { id: 'clean-10', title: 'С первой попытки', description: 'Решите 10 задач без единой ошибки.', icon: 'star', value: (i) => i.firstTrySolved, target: 10 },
  { id: 'solved-100', title: 'Сотня', description: 'Решите 100 задач.', icon: 'medal', value: (i) => i.solvedTasks, target: 100 },
  { id: 'mastered-3', title: 'Три освоенных задания', description: 'Доведите три номера ЕГЭ до статуса «Освоено».', icon: 'award', value: (i) => i.masteredTopics, target: 3 },
  { id: 'streak-30', title: 'Месяц практики', description: 'Занимайтесь 30 дней подряд.', icon: 'flame', value: (i) => i.bestStreak, target: 30 },
  { id: 'mock-1', title: 'Боевое крещение', description: 'Добавьте результат первого пробного ЕГЭ.', icon: 'trophy', value: (i) => i.mockExams, target: 1 },
]

export function computeAchievements(input: AchievementInput): Achievement[] {
  return RULES.map((rule) => {
    const value = rule.value(input)
    const current = Math.min(value ?? 0, rule.target)
    return {
      id: rule.id,
      title: rule.title,
      description: rule.description,
      icon: rule.icon,
      unlocked: value !== null && value >= rule.target,
      progress: value === null ? null : { current, target: rule.target },
    }
  })
}

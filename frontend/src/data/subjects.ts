
export type SubjectSlug = 'informatics' | 'mathematics'

export type SubjectStats = {
  solvedTasks: number | null
  topicsCompleted: number | null
}

export type SubjectData = {
  slug: SubjectSlug
  name: string
  level: number
  accent: 'red' | 'gold'
  xp: {
    current: number
    required: number
  }
  stats: SubjectStats
}

export const subjects: Record<SubjectSlug, SubjectData> = {
  informatics: {
    slug: 'informatics',
    name: 'Информатика',
    level: 25,
    accent: 'red',
    xp: {
      current: 340,
      required: 500,
    },
    stats: {
      solvedTasks: null,
      topicsCompleted: null,
    },
  },
  mathematics: {
    slug: 'mathematics',
    name: 'Математика',
    level: 19,
    accent: 'gold',
    xp: {
      current: 210,
      required: 600,
    },
    stats: {
      solvedTasks: null,
      topicsCompleted: null,
    },
  },
}

const rankTiers = [
  { level: 1, name: 'Bronze', image: '/bronze.png' },
  { level: 6, name: 'Silver', image: '/silver.png' },
  { level: 12, name: 'Gold', image: '/gold.png' },
  { level: 18, name: 'Platinum', image: '/platinum.png' },
  { level: 25, name: 'Master', image: '/master.png' },
  { level: 30, name: 'Grandmaster', image: '/grandmaster.png' },
]

export function getRankForLevel(level: number) {
  const boundedLevel = Math.max(1, Math.min(30, level))
  return [...rankTiers].reverse().find((rank) => boundedLevel >= rank.level)!
}

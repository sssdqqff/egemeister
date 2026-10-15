import type { Difficulty } from '../../types'

export interface Rng {
  next(): number
  int(min: number, max: number): number
  pick<T>(items: readonly T[]): T
  chance(p: number): boolean
}

/** Детерминированный генератор: один и тот же seed даёт одинаковый каталог при каждом запуске. */
export function createRng(seed: number): Rng {
  let state = seed >>> 0
  const next = () => {
    state = (state + 0x6d2b79f5) >>> 0
    let t = state
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
  return {
    next,
    int: (min, max) => Math.floor(next() * (max - min + 1)) + min,
    pick: (items) => items[Math.floor(next() * items.length)],
    chance: (p) => next() < p,
  }
}

export interface GeneratedTask {
  condition: string
  answer: string
  difficulty: Difficulty
  solution: string
}

export interface PrototypeSpec {
  code: string
  name: string
  description: string
  hint: string
  count: number
  make(rng: Rng): GeneratedTask
}

export interface TopicSpec {
  number: number
  name: string
  slug: string
  description: string
  prototypes: PrototypeSpec[]
}

export interface SubjectSpec {
  id: number
  name: string
  slug: string
  description: string
  topics: TopicSpec[]
}

export function gcd(a: number, b: number): number {
  return b === 0 ? a : gcd(b, a % b)
}

export function lcm(a: number, b: number): number {
  return (a / gcd(a, b)) * b
}

export function countChar(value: string, char: string): number {
  let count = 0
  for (const c of value) if (c === char) count += 1
  return count
}

export const VOWELS = new Set('АЕЁИОУЫЭЮЯ')

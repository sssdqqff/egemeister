/**
 * Перевод первичных баллов в тестовые. Ориентировочные шкалы ФИПИ 2024 —
 * официальная шкала публикуется ежегодно, таблицы нужно обновлять.
 * Ключ — slug предмета.
 */
const SCALES: Record<string, number[]> = {
  informatics: [
    0, 7, 14, 20, 27, 34, 40, 43, 46, 48, 51, 54, 56, 59, 62, 64, 67, 70, 72, 75, 78, 80, 83, 85,
    88, 90, 93, 95, 98, 100,
  ],
  math: [
    0, 6, 11, 17, 22, 27, 34, 40, 46, 52, 58, 64, 66, 68, 70, 72, 74, 76, 78, 80, 82, 84, 86, 88,
    90, 92, 94, 96, 98, 99, 100, 100, 100,
  ],
}

export function maxPrimaryScore(subjectSlug: string): number | null {
  const scale = SCALES[subjectSlug]
  return scale ? scale.length - 1 : null
}

export function toTestScore(subjectSlug: string, primary: number): number | null {
  const scale = SCALES[subjectSlug]
  if (!scale || primary < 0 || primary >= scale.length || !Number.isInteger(primary)) return null
  return scale[primary]
}

/** Повторяет normalize_answer / is_answer_correct из backend/app/services/attempt_service.py. */
export function normalizeAnswer(value: string): string {
  return value.trim().toLowerCase().split(/\s+/).join(' ').replaceAll('ё', 'е').replaceAll(',', '.')
}

const DECIMAL = /^[+-]?(\d+\.?\d*|\.\d+)$/

export function isAnswerCorrect(correct: string, given: string): boolean {
  const a = normalizeAnswer(correct)
  const b = normalizeAnswer(given)
  if (a === b) return true
  if (DECIMAL.test(a) && DECIMAL.test(b)) return Number(a) === Number(b)
  return false
}

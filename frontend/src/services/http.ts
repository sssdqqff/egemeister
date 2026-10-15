export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

type UnauthorizedListener = () => void
const unauthorizedListeners = new Set<UnauthorizedListener>()

/** Подписка на 401 от любого запроса — используется AuthProvider для выхода из сессии. */
export function onUnauthorized(listener: UnauthorizedListener): () => void {
  unauthorizedListeners.add(listener)
  return () => unauthorizedListeners.delete(listener)
}

/**
 * Сессия хранится в httpOnly-cookie, которую выставляет backend (/auth/telegram/exchange),
 * поэтому токены на клиенте не читаются и не сохраняются.
 */
export async function http<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response
  try {
    response = await fetch(`/api${path}`, {
      credentials: 'same-origin',
      ...options,
      headers: { 'Content-Type': 'application/json', ...options.headers },
    })
  } catch {
    throw new ApiError(0, 'Не удалось связаться с сервером')
  }

  if (!response.ok) {
    if (response.status === 401) unauthorizedListeners.forEach((listener) => listener())
    const body = await response.json().catch(() => null)
    const detail = typeof body?.detail === 'string' ? body.detail : 'Request failed'
    throw new ApiError(response.status, detail)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export function describeError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 0) return 'Нет соединения с сервером. Проверьте подключение.'
    if (error.status === 401) return 'Сессия истекла. Войдите снова.'
    if (error.status === 403) return 'Недостаточно прав для этого действия.'
    if (error.status === 404) return 'Данные не найдены.'
    if (error.status === 429) return 'Слишком много запросов. Подождите немного.'
    if (error.status >= 500) return 'Сервер временно недоступен. Попробуйте позже.'
    return error.message
  }
  if (error instanceof Error) return error.message
  return 'Что-то пошло не так.'
}

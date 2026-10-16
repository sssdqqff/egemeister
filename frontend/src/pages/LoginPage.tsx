import { useEffect, useState, type FormEvent } from 'react'
import { ArrowRight, KeyRound, Send } from 'lucide-react'
import { ApiError } from '../api'
import { useAuth } from '../auth/authContext'

function readCodeFromUrl(): string | null {
  const fromHash = new URLSearchParams(window.location.hash.slice(1)).get('code')
  const fromQuery = new URLSearchParams(window.location.search).get('code')
  return fromHash ?? fromQuery
}

function errorText(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 429) return 'Слишком много неверных попыток. Подождите несколько минут.'
    if (error.status === 400 || error.status === 422) {
      return 'Неверный или просроченный код. Запросите новый у бота.'
    }
    return 'Не удалось войти. Попробуйте позже.'
  }
  return 'Не удалось связаться с сервером.'
}

export default function LoginPage() {
  const { login } = useAuth()
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(() => readCodeFromUrl() !== null)
  const [error, setError] = useState('')

  useEffect(() => {
    const urlCode = readCodeFromUrl()
    if (!urlCode) return
    window.history.replaceState(null, '', window.location.pathname)
    login(urlCode).catch((err) => {
      setError(errorText(err))
      setLoading(false)
    })
  }, [login])

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (code.length < 4) return
    setLoading(true)
    setError('')
    try {
      await login(code)
    } catch (err) {
      setError(errorText(err))
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center p-4">
      <form
        onSubmit={handleSubmit}
        className="max-w-md w-full bg-gray-800 rounded-2xl p-8 shadow-xl border border-gray-700 space-y-4"
      >
        <div className="flex justify-center">
          <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-indigo-600/15 border border-indigo-500/20 text-indigo-400">
            <KeyRound size={28} strokeWidth={1.7} aria-hidden="true" />
          </div>
        </div>

        <h1 className="text-2xl font-bold text-center">Вход в EgeMeister</h1>

        <p className="text-sm text-gray-400 text-center">
          Напишите боту /start и введите код, который он пришлёт.
        </p>

        <div className="relative">
          <Send
            size={18}
            strokeWidth={1.7}
            aria-hidden="true"
            className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500"
          />
          <input
            type="text"
            inputMode="numeric"
            autoComplete="one-time-code"
            maxLength={12}
            value={code}
            onChange={(event) => setCode(event.target.value.replace(/\D/g, ''))}
            placeholder="Код из Telegram"
            className="w-full px-4 py-3 pl-11 bg-gray-900 border border-gray-700 rounded-xl focus:outline-none focus:border-indigo-500 text-center text-xl tracking-widest text-white"
          />
        </div>

        {error && (
          <div className="text-red-400 text-sm text-center">{error}</div>
        )}

        <button
          type="submit"
          disabled={loading || code.length < 4}
          className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-500 transition-colors rounded-xl font-medium disabled:opacity-50 cursor-pointer flex items-center justify-center gap-2"
        >
          {loading ? (
            'Проверка...'
          ) : (
            <>
              Войти
              <ArrowRight size={18} strokeWidth={1.8} aria-hidden="true" />
            </>
          )}
        </button>
      </form>
    </div>
  )
}

import { useState, useEffect } from 'react'

export default function App() {
  const [code, setCode] = useState<string>('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState<string>('')

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const urlCode = params.get('code')
    if (urlCode) {
      setCode(urlCode)
      handleLogin(urlCode)
    }
  }, [])

  const handleLogin = async (codeToSubmit: string) => {
    if (!codeToSubmit.trim()) return
    setStatus('loading')
    setErrorMessage('')

    try {
      const response = await fetch('http://127.0.0.1:8000/auth/telegram/exchange', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        throw new Error('Неверный или просроченный код авторизации')
      }

      const data = await response.json()
      localStorage.setItem('access_token', data.access_token)
      setStatus('success')
    } catch (err: unknown) {
      setStatus('error')
      setErrorMessage(err instanceof Error ? err.message : 'Произошла непредвиденная ошибка')
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-gray-800 rounded-2xl p-8 shadow-xl border border-gray-700">
        <h1 className="text-2xl font-bold text-center mb-6">Авторизация</h1>

        {status === 'success' ? (
          <div className="text-center text-green-400 font-medium py-4">
            Успешный вход! Добро пожаловать в систему.
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Код из Telegram
              </label>
              <input
                type="text"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="Введите код"
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl focus:outline-none focus:border-indigo-500 text-center text-xl tracking-widest text-white"
              />
            </div>

            {errorMessage && (
              <div className="text-red-400 text-sm text-center">{errorMessage}</div>
            )}

            <button
              onClick={() => handleLogin(code)}
              disabled={status === 'loading'}
              className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 transition-colors rounded-xl font-medium disabled:opacity-50 cursor-pointer"
            >
              {status === 'loading' ? 'Проверка...' : 'Войти'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
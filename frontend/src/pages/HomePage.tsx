import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import { useAuth } from '../auth/authContext'
import type { Subject } from '../types'

export default function HomePage() {
  const { user, logout } = useAuth()
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadSubjects = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const data = await api<Subject[]>('/subjects')
      setSubjects(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось загрузить предметы')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadSubjects()
  }, [loadSubjects])

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="border-b border-gray-800">
        <div className="max-w-5xl mx-auto px-6 py-5 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">EG Meister</h1>
            <p className="text-sm text-gray-400 mt-1">
              Привет, {user?.first_name ?? 'ученик'}!
            </p>
          </div>

          <button
            onClick={() => void logout()}
            className="px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors"
          >
            Выйти
          </button>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-10">
        <div className="mb-8">
          <h2 className="text-3xl font-bold">Мои предметы</h2>
          <p className="text-gray-400 mt-2">
            Выбери предмет, чтобы приступить к обучению.
          </p>
        </div>

        {loading ? (
          <p className="text-gray-400">Загружаем предметы...</p>
        ) : error ? (
          <div className="rounded-xl border border-red-900 bg-red-950/30 p-5">
            <p className="text-red-300">{error}</p>
            <button
              onClick={() => void loadSubjects()}
              className="mt-4 px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700"
            >
              Попробовать снова
            </button>
          </div>
        ) : subjects.length === 0 ? (
          <p className="text-gray-400">
            Пока нет доступных предметов.
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {subjects.map((subject) => (
              <article
                key={subject.id}
                className="rounded-2xl border border-gray-700 bg-gray-800 p-6 hover:border-gray-500 transition-colors"
              >
                <h3 className="text-xl font-semibold">{subject.name}</h3>
                <p className="text-gray-400 mt-3 leading-relaxed">
                  {subject.description}
                </p>
                <p className="text-xs text-gray-500 mt-5">
                  Предмет: {subject.slug}
                </p>
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
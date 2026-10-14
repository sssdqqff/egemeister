import { useAuth } from '../auth/authContext'

export default function HomePage() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-gray-800 rounded-2xl p-8 shadow-xl border border-gray-700 space-y-4 text-center">
        <h1 className="text-2xl font-bold">Привет, {user?.first_name ?? 'ученик'}!</h1>
        <p className="text-gray-400 text-sm">Роль: {user?.role}</p>
        <button
          onClick={() => void logout()}
          className="w-full py-3 bg-gray-700 hover:bg-gray-600 transition-colors rounded-xl font-medium cursor-pointer"
        >
          Выйти
        </button>
      </div>
    </div>
  )
}
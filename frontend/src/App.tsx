import { useAuth } from './auth/authContext'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'

export default function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-gray-400 flex items-center justify-center">
        Загрузка...
      </div>
    )
  }

  return user ? <HomePage /> : <LoginPage />
}
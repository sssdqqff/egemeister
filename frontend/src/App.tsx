import { Navigate, Route, Routes } from 'react-router'
import { LogOut } from 'lucide-react'
import { useAuth } from './auth/authContext'
import { AppLayout } from './components/layout/AppLayout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import PracticePage from './pages/PracticePage'
import SubjectPage from './pages/SubjectPage'
import ProfilePage from './pages/ProfilePage'

function PlaceholderPage({
  title,
  description,
}: {
  title: string
  description: string
}) {
  return (
    <section className="section-page">
      <div className="home-accent-line" />
      <h1 className="home-title">{title}</h1>
      <p className="home-description">{description}</p>
    </section>
  )
}

function SettingsPage() {
  const { logout } = useAuth()

  return (
    <section className="section-page">
      <div className="home-accent-line" />
      <h1 className="home-title">Настройки</h1>
      <p className="home-description">
        Управление аккаунтом и настройками платформы.
      </p>

      <div className="settings-panel">
        <div>
          <h2 className="settings-panel-title">Аккаунт</h2>
          <p className="home-description">
            Завершить текущий сеанс.
          </p>
        </div>
        <button
          type="button"
          className="home-button"
          onClick={() => void logout()}
        >
          <LogOut size={16} strokeWidth={1.8} />
          Выйти из аккаунта
        </button>
      </div>
    </section>
  )
}

export default function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return <div className="app-loading">Загрузка...</div>
  }

  if (!user) {
    return <LoginPage />
  }

  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<HomePage />} />
        <Route path="tasks" element={<PracticePage />} />

        <Route
          path="tasks/:subjectSlug/topics"
          element={
            <PlaceholderPage
              title="Выбор номера ЕГЭ"
              description="Здесь появится список номеров и тем для тренировки."
            />
          }
        />

        <Route
          path="tasks/:subjectSlug/prototypes"
          element={
            <PlaceholderPage
              title="Выбор прототипа"
              description="Здесь появится список прототипов и типов задач."
            />
          }
        />

        <Route
          path="tasks/:subjectSlug/mixed"
          element={
            <PlaceholderPage
              title="Смешанная тренировка"
              description="Здесь появится тренировка на задания разных типов."
            />
          }
        />

        <Route
          path="tasks/:subjectSlug"
          element={<SubjectPage />}
        />

        <Route path="profile" element={<ProfilePage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
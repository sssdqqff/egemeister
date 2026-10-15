import { BookOpen, LayoutGrid, LogOut, UserRound } from 'lucide-react'
import { NavLink, useLocation } from 'react-router'
import { useAuth } from '../../auth/authContext'
import { useCatalog } from '../../hooks/useData'
import { cn } from '../../lib/cn'
import { Logo } from './Logo'

export function MobileHeader() {
  const { logout } = useAuth()
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-line bg-bg/90 px-4 backdrop-blur lg:hidden">
      <NavLink to="/dashboard" aria-label="EG Meister — на главную">
        <Logo />
      </NavLink>
      <button
        type="button"
        onClick={() => logout()}
        className="grid size-9 place-items-center rounded-md text-subtle hover:bg-surface-2 hover:text-fg"
        aria-label="Выйти"
      >
        <LogOut className="size-4" aria-hidden="true" />
      </button>
    </header>
  )
}

const itemClass = (active: boolean) =>
  cn('flex flex-1 flex-col items-center gap-1 py-2 text-[11px] font-medium transition-colors', active ? 'text-fg' : 'text-subtle')

export function MobileTabBar() {
  const { data: catalog } = useCatalog()
  const { pathname } = useLocation()
  const firstSubject = catalog?.subjects[0]
  const inSubjects = pathname.startsWith('/subjects')

  return (
    <nav
      aria-label="Основная навигация"
      className="fixed inset-x-0 bottom-0 z-30 flex border-t border-line bg-bg/95 pb-[env(safe-area-inset-bottom)] backdrop-blur lg:hidden"
    >
      <NavLink to="/dashboard" className={({ isActive }) => itemClass(isActive)}>
        <LayoutGrid className="size-5" aria-hidden="true" />
        Главная
      </NavLink>
      <NavLink
        to={firstSubject ? `/subjects/${firstSubject.id}/tasks` : '/dashboard'}
        className={() => itemClass(inSubjects)}
        aria-current={inSubjects ? 'page' : undefined}
      >
        <BookOpen className="size-5" aria-hidden="true" />
        Задания
      </NavLink>
      <NavLink to="/profile" className={({ isActive }) => itemClass(isActive)}>
        <UserRound className="size-5" aria-hidden="true" />
        Профиль
      </NavLink>
    </nav>
  )
}

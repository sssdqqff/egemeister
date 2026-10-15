import { LayoutGrid, LogOut, UserRound } from 'lucide-react'
import { NavLink } from 'react-router'
import { useAuth } from '../../auth/authContext'
import { IS_DEMO } from '../../config'
import { useCatalog, useProfile } from '../../hooks/useData'
import { cn } from '../../lib/cn'
import { levelProgress } from '../../lib/progression'
import { SubjectIcon } from '../subjects/SubjectIcon'
import { ProgressBar } from '../ui/Progress'
import { Avatar } from './Avatar'
import { Logo } from './Logo'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  cn(
    'flex h-9 items-center gap-3 rounded-lg px-2.5 text-[13px] font-medium transition-colors',
    isActive ? 'bg-surface-2 text-fg' : 'text-muted hover:bg-surface-2/60 hover:text-fg',
  )

export function Sidebar() {
  const { user, logout } = useAuth()
  const { data: catalog } = useCatalog()
  const { data: profile } = useProfile()
  const level = profile ? levelProgress(profile.xp, profile.level) : null

  return (
    <aside className="sticky top-0 hidden h-dvh w-60 shrink-0 flex-col border-r border-line bg-bg px-3 py-4 lg:flex">
      <NavLink to="/dashboard" className="mb-6 px-2.5" aria-label="EG Meister — на главную">
        <Logo />
      </NavLink>

      <nav aria-label="Основная навигация" className="flex flex-col gap-0.5">
        <NavLink to="/dashboard" className={linkClass}>
          <LayoutGrid className="size-4" aria-hidden="true" />
          Главная
        </NavLink>
        <NavLink to="/profile" className={linkClass}>
          <UserRound className="size-4" aria-hidden="true" />
          Профиль
        </NavLink>

        <p className="mt-6 mb-1.5 px-2.5 text-[11px] font-medium tracking-wide text-subtle uppercase">Предметы</p>
        {catalog?.subjects.map((subject) => (
          <NavLink key={subject.id} to={`/subjects/${subject.id}/tasks`} className={linkClass}>
            <SubjectIcon slug={subject.slug} className="size-5 rounded-md border-0 bg-transparent [&_svg]:size-4" />
            <span className="truncate">{subject.name}</span>
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto space-y-3">
        {IS_DEMO && (
          <p className="rounded-lg border border-line bg-surface px-3 py-2 text-[12px] leading-relaxed text-muted">
            Демо-режим: данные локальные и сбрасываются при перезагрузке.
          </p>
        )}
        <div className="rounded-lg border border-line bg-surface p-3">
          <div className="flex items-center gap-2.5">
            <Avatar name={user?.first_name ?? user?.username ?? '?'} size={32} />
            <div className="min-w-0 flex-1">
              <p className="truncate text-[13px] font-medium">{user?.first_name ?? user?.username ?? 'Ученик'}</p>
              <p className="text-[12px] text-muted tabular">
                {level ? `Уровень ${level.level} · ${profile?.xp.toLocaleString('ru-RU')} XP` : '—'}
              </p>
            </div>
            <button
              type="button"
              onClick={() => logout()}
              className="grid size-8 place-items-center rounded-md text-subtle transition-colors hover:bg-surface-2 hover:text-fg"
              aria-label="Выйти"
              title="Выйти"
            >
              <LogOut className="size-4" aria-hidden="true" />
            </button>
          </div>
          {level && <ProgressBar value={level.ratio} size="xs" className="mt-3" label="Прогресс уровня" />}
        </div>
      </div>
    </aside>
  )
}

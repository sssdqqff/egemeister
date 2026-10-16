
import { useEffect, useRef, useState } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router'

export function AppLayout() {
  const { pathname } = useLocation()
  const navRef = useRef<HTMLElement | null>(null)
  const homeRef = useRef<HTMLAnchorElement | null>(null)
  const tasksRef = useRef<HTMLAnchorElement | null>(null)
  const profileRef = useRef<HTMLAnchorElement | null>(null)
  const [indicator, setIndicator] = useState({
    left: 0,
    width: 0,
    visible: false,
  })

  useEffect(() => {
    window.scrollTo({ top: 0 })
  }, [pathname])

  useEffect(() => {
    const updateIndicator = () => {
      const activeLink =
        pathname === '/'
          ? homeRef.current
          : pathname.startsWith('/tasks')
            ? tasksRef.current
            : pathname.startsWith('/profile')
              ? profileRef.current
              : null

      const nav = navRef.current

      if (!activeLink || !nav) {
        setIndicator((current) => ({ ...current, visible: false }))
        return
      }

      const navRect = nav.getBoundingClientRect()
      const linkRect = activeLink.getBoundingClientRect()

      setIndicator({
        left: linkRect.left - navRect.left,
        width: linkRect.width,
        visible: true,
      })
    }

    updateIndicator()

    const nav = navRef.current
    if (!nav) return

    const observer = new ResizeObserver(updateIndicator)
    observer.observe(nav)
    window.addEventListener('resize', updateIndicator)

    return () => {
      observer.disconnect()
      window.removeEventListener('resize', updateIndicator)
    }
  }, [pathname])

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-inner">
          <Link to="/" className="app-brand" aria-label="Grandmaster — главная">
            <img
              src="/grandmaster-emblem.png"
              alt=""
              className="app-brand-mark"
            />
            <span className="app-brand-copy">
              <span className="app-brand-name">
                <span className="app-brand-accent">Grand</span>
                <span className="app-brand-gold">master</span>
              </span>
              <span className="app-brand-tagline">
                LEARN. PRACTICE. MASTER.
              </span>
            </span>
          </Link>

          <nav
            ref={navRef}
            className="app-nav"
            aria-label="Основная навигация"
          >
            <span
              className="app-nav-indicator"
              aria-hidden="true"
              style={{
                transform: `translateX(${indicator.left}px)`,
                width: `${indicator.width}px`,
                opacity: indicator.visible ? 1 : 0,
              }}
            />

            <NavLink
              ref={homeRef}
              to="/"
              end
              className={({ isActive }) =>
                `app-nav-link${isActive ? ' is-active' : ''}`
              }
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="m3 10 9-7 9 7" />
                <path d="M5 9v12h14V9M9 21v-7h6v7" />
              </svg>
              <span>Главная</span>
            </NavLink>

            <NavLink
              ref={tasksRef}
              to="/tasks"
              className={({ isActive }) =>
                `app-nav-link${isActive ? ' is-active' : ''}`
              }
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="4" y="4" width="16" height="16" rx="2" />
                <path d="M8 9h.01M11 9h5M8 15h.01M11 15h5" />
              </svg>
              <span>Практика</span>
            </NavLink>

            <NavLink
              ref={profileRef}
              to="/profile"
              className={({ isActive }) =>
                `app-nav-link${isActive ? ' is-active' : ''}`
              }
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <circle cx="12" cy="8" r="3.5" />
                <path d="M5 21a7 7 0 0 1 14 0" />
              </svg>
              <span>Профиль</span>
            </NavLink>
          </nav>

          <div className="app-header-right">
            <span className="app-greeting">Привет, 🇺🇸!</span>

            <div className="app-level-wrapper">
              <Link
                to="/profile"
                className="app-level-badge"
                aria-label="Уровень 12 — открыть профиль"
              >
                <span
                  className="app-level-progress"
                  style={{ width: '68%' }}
                />
                <span className="app-level-label">LVL 12</span>
              </Link>

              <div className="app-level-tooltip" role="tooltip">
                <span className="app-level-tooltip-eyebrow">
                  ТВОЙ УРОВЕНЬ
                </span>

                <div className="app-level-tooltip-heading">
                  <strong>LVL 12</strong>
                  <span>340 / 500 XP</span>
                </div>

                <div className="app-level-tooltip-track">
                  <div
                    className="app-level-tooltip-fill"
                    style={{ width: '68%' }}
                  />
                </div>

                <div className="app-level-tooltip-footer">
                  <span>До следующего уровня</span>
                  <strong>160 XP</strong>
                </div>
              </div>
            </div>

            <Link
              to="/settings"
              className="app-settings-button"
              aria-label="Настройки"
              title="Настройки"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.09a2 2 0 0 1 1 1.73v.5a2 2 0 0 1-1 1.73l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.38a2 2 0 0 0-.73-2.73l-.15-.09a2 2 0 0 1-1-1.73v-.5a2 2 0 0 1 1-1.73l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2Z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            </Link>
          </div>
        </div>
      </header>

      <main className="app-main">
        <Outlet />
      </main>
    </div>
  )
}

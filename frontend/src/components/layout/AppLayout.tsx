import { useEffect } from 'react'
import { Outlet, useLocation } from 'react-router'
import { MobileHeader, MobileTabBar } from './MobileNav'
import { Sidebar } from './Sidebar'

export function AppLayout() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo({ top: 0 })
  }, [pathname])

  return (
    <div className="flex min-h-dvh">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <MobileHeader />
        <main className="mx-auto w-full max-w-[1120px] flex-1 px-4 pt-6 pb-24 sm:px-6 lg:px-10 lg:pt-10 lg:pb-12">
          <Outlet />
        </main>
      </div>
      <MobileTabBar />
    </div>
  )
}

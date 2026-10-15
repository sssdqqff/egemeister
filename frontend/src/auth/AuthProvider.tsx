import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { useSWRConfig } from 'swr'
import { catalog } from '../services'
import { onUnauthorized } from '../services/http'
import type { User } from '../types'
import { AuthContext } from './authContext'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const { mutate } = useSWRConfig()

  useEffect(() => {
    let cancelled = false
    catalog
      .getCurrentUser()
      .then((current) => !cancelled && setUser(current))
      .catch(() => !cancelled && setUser(null))
      .finally(() => !cancelled && setLoading(false))
    return () => {
      cancelled = true
    }
  }, [])

  const clearCache = useCallback(() => mutate(() => true, undefined, { revalidate: false }), [mutate])

  useEffect(
    () =>
      onUnauthorized(() => {
        setUser(null)
        clearCache()
      }),
    [clearCache],
  )

  const login = useCallback(async (code: string) => {
    const loggedIn = await catalog.login(code)
    setUser(loggedIn)
  }, [])

  const logout = useCallback(async () => {
    await catalog.logout()
    setUser(null)
    await clearCache()
  }, [clearCache])

  const value = useMemo(() => ({ user, loading, login, logout }), [user, loading, login, logout])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { api } from '../api'
import type { User } from '../types'
import { AuthContext } from './authContext'

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        api<User>('/users/me')
        .then(setUser)
        .catch(() => setUser(null))
        .finally(() => setLoading(false))
    }, [])

    const login = useCallback(async (code: string) => {
        const loggedInUser = await api<User>('/auth/telegram/exchange', {
        method: 'POST',
        body: JSON.stringify({ code }),
        })
        setUser(loggedInUser)
    }, [])

    const logout = useCallback(async () => {
        await api<void>('/auth/logout', { method: 'POST' })
        setUser(null)
    }, [])

    const value = useMemo(() => ({ user, loading, login, logout }), [user, loading, login, logout])

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
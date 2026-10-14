import { createContext, useContext } from 'react'
import type { User } from '../types'

export interface AuthState {
    user: User | null
    loading: boolean
    login: (code: string) => Promise<void>
    logout: () => Promise<void>
    }

    export const AuthContext = createContext<AuthState | null>(null)

    export function useAuth(): AuthState {
    const context = useContext(AuthContext)
    if (!context) throw new Error('useAuth must be used inside AuthProvider')
    return context
}
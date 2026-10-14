export interface User {
  id: number
  telegram_id: number | null
  first_name: string | null
  username: string | null
  email: string | null
  is_active: boolean
  role: 'user' | 'admin'
  created_at: string
}
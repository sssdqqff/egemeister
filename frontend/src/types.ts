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

export interface Subject {
  id: number
  name: string
  slug: string
  description: string
  is_active: boolean
}
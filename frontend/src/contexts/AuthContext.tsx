import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'

interface User {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<boolean>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        setLoading(false)
        return
      }

      // Verify token by fetching user info
      const response = await api.get('/auth/me')
      setUser(response.data)
    } catch (error) {
      console.error('Auth check failed:', error)
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_info')
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setLoading(true)
      
      const response = await api.post('/auth/login/json', {
        email,
        password,
      })

      const { access_token, user_id, role, full_name } = response.data
      
      // Store token and user info
      localStorage.setItem('auth_token', access_token)
      localStorage.setItem('user_info', JSON.stringify({
        id: user_id,
        email,
        full_name,
        role,
        is_active: true
      }))

      // Set user state
      setUser({
        id: user_id,
        email,
        full_name,
        role,
        is_active: true
      })

      toast.success(`Welcome back, ${full_name}!`)
      return true
    } catch (error: any) {
      console.error('Login failed:', error)
      
      if (error.response?.status === 401) {
        toast.error('Invalid email or password')
      } else if (error.response?.status === 400) {
        toast.error('Account is inactive')
      } else {
        toast.error('Login failed. Please try again.')
      }
      
      return false
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_info')
    setUser(null)
    toast.success('Logged out successfully')
  }

  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
} 
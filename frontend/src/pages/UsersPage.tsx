import React, { useState, useEffect } from 'react'
import { Users, Plus, Mail, Calendar, Shield, AlertTriangle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

interface User {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
  updated_at: string
}

const UsersPage: React.FC = () => {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (currentUser?.role !== 'admin') {
      setError('Access denied. Admin privileges required.')
      setLoading(false)
      return
    }
    fetchUsers()
  }, [currentUser])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const response = await api.get('/users/')
      setUsers(response.data)
      setError(null)
    } catch (err: any) {
      setError('Failed to fetch users')
      console.error('Error fetching users:', err)
    } finally {
      setLoading(false)
    }
  }

  const toggleUserStatus = async (userId: string, isActive: boolean) => {
    try {
      await api.put(`/users/${userId}`, { is_active: !isActive })
      await fetchUsers() // Refresh the list
    } catch (err: any) {
      console.error('Error updating user status:', err)
    }
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-purple-100 text-purple-800'
      case 'operator': return 'bg-blue-100 text-blue-800'
      case 'logistics': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin': return <Shield className="h-4 w-4" />
      case 'operator': return <Users className="h-4 w-4" />
      case 'logistics': return <Users className="h-4 w-4" />
      default: return <Users className="h-4 w-4" />
    }
  }

  if (currentUser?.role !== 'admin') {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Users</h1>
          <p className="text-gray-600 mt-1">Manage system users and permissions</p>
        </div>
        <div className="card p-6">
          <div className="text-center py-12">
            <Shield className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Access Denied</h3>
            <p className="text-gray-500">
              You need administrator privileges to access user management.
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Users</h1>
            <p className="text-gray-600 mt-1">Manage system users and permissions</p>
          </div>
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="flex items-center space-x-4">
                <div className="h-12 w-12 bg-gray-200 rounded-full"></div>
                <div className="space-y-2 flex-1">
                  <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/3"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Users</h1>
          <p className="text-gray-600 mt-1">Manage system users and permissions</p>
        </div>
        <div className="card p-6">
          <div className="text-center py-12">
            <AlertTriangle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Users</h3>
            <p className="text-gray-500 mb-4">{error}</p>
            <button onClick={fetchUsers} className="btn-primary">Try Again</button>
          </div>
        </div>
      </div>
    )
  }

  const adminUsers = users.filter(user => user.role === 'admin')
  const operatorUsers = users.filter(user => user.role === 'operator')
  const logisticsUsers = users.filter(user => user.role === 'logistics')
  const activeUsers = users.filter(user => user.is_active)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Users</h1>
          <p className="text-gray-600 mt-1">
            Manage system users and permissions
          </p>
        </div>
        <button className="btn-primary">
          <Plus className="h-4 w-4 mr-2" />
          Add User
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-8 w-8 text-blue-500" />
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">{users.length}</div>
              <div className="text-sm text-gray-500">Total Users</div>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-8 w-8 text-green-500" />
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">{activeUsers.length}</div>
              <div className="text-sm text-gray-500">Active Users</div>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Shield className="h-8 w-8 text-purple-500" />
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">{adminUsers.length}</div>
              <div className="text-sm text-gray-500">Administrators</div>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-8 w-8 text-orange-500" />
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">{operatorUsers.length + logisticsUsers.length}</div>
              <div className="text-sm text-gray-500">Staff Users</div>
            </div>
          </div>
        </div>
      </div>

      {/* Users List */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">System Users</h3>
        </div>
        
        {users.length === 0 ? (
          <div className="p-6">
            <div className="text-center py-12">
              <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Users Found</h3>
              <p className="text-gray-500">
                No users have been created yet.
              </p>
            </div>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {users.map((user) => (
              <div key={user.id} className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="text-primary-600 font-medium text-lg">
                          {user.full_name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className="text-lg font-medium text-gray-900">{user.full_name}</h4>
                        {user.id === currentUser?.id && (
                          <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                            You
                          </span>
                        )}
                        {!user.is_active && (
                          <span className="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
                            Inactive
                          </span>
                        )}
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center">
                          <Mail className="h-4 w-4 mr-1" />
                          {user.email}
                        </div>
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          Joined {new Date(user.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <span className={`flex items-center px-3 py-1 text-sm font-medium rounded-full ${getRoleColor(user.role)}`}>
                      {getRoleIcon(user.role)}
                      <span className="ml-1 capitalize">{user.role}</span>
                    </span>
                    
                    {user.id !== currentUser?.id && (
                      <button
                        onClick={() => toggleUserStatus(user.id, user.is_active)}
                        className={`text-sm px-3 py-1 rounded-md ${
                          user.is_active
                            ? 'text-red-600 hover:bg-red-50 border border-red-200'
                            : 'text-green-600 hover:bg-green-50 border border-green-200'
                        }`}
                      >
                        {user.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default UsersPage 
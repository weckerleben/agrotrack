import React, { useState, useEffect } from 'react'
import { AlertTriangle, CheckCircle, Clock, Thermometer, Droplets, Package, Filter, X } from 'lucide-react'
import api from '../services/api'

interface Alert {
  id: string
  silo_id: number
  alert_type: string
  severity: string
  title: string
  description: string
  value: number
  threshold: number
  status: string
  created_at: string
  resolved_at?: string
  silo?: {
    name: string
    location: string
  }
}

const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState({
    status: 'all',
    severity: 'all',
    type: 'all'
  })

  useEffect(() => {
    fetchAlerts()
  }, [])

  const fetchAlerts = async () => {
    try {
      setLoading(true)
      const response = await api.get('/alerts/')
      setAlerts(response.data)
      setError(null)
    } catch (err: any) {
      setError('Failed to fetch alerts')
      console.error('Error fetching alerts:', err)
    } finally {
      setLoading(false)
    }
  }

  const resolveAlert = async (alertId: string) => {
    try {
      await api.put(`/alerts/${alertId}/resolve`)
      await fetchAlerts() // Refresh the list
    } catch (err: any) {
      console.error('Error resolving alert:', err)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200'
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-red-100 text-red-800'
      case 'resolved': return 'bg-green-100 text-green-800'
      case 'acknowledged': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'temperature': return <Thermometer className="h-5 w-5" />
      case 'humidity': return <Droplets className="h-5 w-5" />
      case 'volume': return <Package className="h-5 w-5" />
      default: return <AlertTriangle className="h-5 w-5" />
    }
  }

  const filteredAlerts = alerts.filter(alert => {
    if (filter.status !== 'all' && alert.status !== filter.status) return false
    if (filter.severity !== 'all' && alert.severity !== filter.severity) return false
    if (filter.type !== 'all' && alert.alert_type !== filter.type) return false
    return true
  })

  const activeAlerts = alerts.filter(alert => alert.status === 'active')
  const criticalAlerts = alerts.filter(alert => alert.severity === 'critical' && alert.status === 'active')

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Alerts</h1>
          <p className="text-gray-600 mt-1">Monitor and manage system alerts</p>
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
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
          <h1 className="text-2xl font-bold text-gray-900">Alerts</h1>
          <p className="text-gray-600 mt-1">Monitor and manage system alerts</p>
        </div>
        <div className="card p-6">
          <div className="text-center py-12">
            <AlertTriangle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Alerts</h3>
            <p className="text-gray-500 mb-4">{error}</p>
            <button onClick={fetchAlerts} className="btn-primary">Try Again</button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Alerts</h1>
        <p className="text-gray-600 mt-1">
          Monitor and manage system alerts
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-8 w-8 text-red-500" />
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">{activeAlerts.length}</div>
              <div className="text-sm text-gray-500">Active Alerts</div>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">{criticalAlerts.length}</div>
              <div className="text-sm text-gray-500">Critical Alerts</div>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">{alerts.length - activeAlerts.length}</div>
              <div className="text-sm text-gray-500">Resolved</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex items-center">
            <Filter className="h-4 w-4 mr-2 text-gray-400" />
            <span className="text-sm font-medium text-gray-700">Filters:</span>
          </div>
          
          <select
            value={filter.status}
            onChange={(e) => setFilter({ ...filter, status: e.target.value })}
            className="text-sm border border-gray-300 rounded-md px-3 py-1"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="resolved">Resolved</option>
            <option value="acknowledged">Acknowledged</option>
          </select>

          <select
            value={filter.severity}
            onChange={(e) => setFilter({ ...filter, severity: e.target.value })}
            className="text-sm border border-gray-300 rounded-md px-3 py-1"
          >
            <option value="all">All Severity</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select
            value={filter.type}
            onChange={(e) => setFilter({ ...filter, type: e.target.value })}
            className="text-sm border border-gray-300 rounded-md px-3 py-1"
          >
            <option value="all">All Types</option>
            <option value="temperature">Temperature</option>
            <option value="humidity">Humidity</option>
            <option value="volume">Volume</option>
          </select>

          {(filter.status !== 'all' || filter.severity !== 'all' || filter.type !== 'all') && (
            <button
              onClick={() => setFilter({ status: 'all', severity: 'all', type: 'all' })}
              className="text-sm text-gray-500 hover:text-gray-700 flex items-center"
            >
              <X className="h-4 w-4 mr-1" />
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Alerts List */}
      {filteredAlerts.length === 0 ? (
        <div className="card p-6">
          <div className="text-center py-12">
            <CheckCircle className="h-12 w-12 text-green-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Alerts Found</h3>
            <p className="text-gray-500">
              {alerts.length === 0 
                ? "No alerts have been generated yet."
                : "No alerts match the current filters."
              }
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredAlerts.map((alert) => (
            <div key={alert.id} className={`card p-6 border-l-4 ${getSeverityColor(alert.severity)}`}>
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <div className={`flex-shrink-0 ${alert.severity === 'critical' ? 'text-red-600' : 
                    alert.severity === 'high' ? 'text-orange-600' : 'text-yellow-600'}`}>
                    {getAlertIcon(alert.alert_type)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-lg font-medium text-gray-900">{alert.title}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(alert.severity)}`}>
                        {alert.severity}
                      </span>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(alert.status)}`}>
                        {alert.status}
                      </span>
                    </div>
                    <p className="text-gray-600 mb-2">{alert.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {new Date(alert.created_at).toLocaleString()}
                      </div>
                      {alert.silo && (
                        <div>
                          {alert.silo.name} - {alert.silo.location}
                        </div>
                      )}
                      <div>
                        Value: {alert.value} | Threshold: {alert.threshold}
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex-shrink-0">
                  {alert.status === 'active' && (
                    <button
                      onClick={() => resolveAlert(alert.id)}
                      className="btn btn-outline text-sm"
                    >
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Resolve
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default AlertsPage 
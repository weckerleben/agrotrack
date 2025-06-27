import React, { useState, useEffect } from 'react'
import api from '../services/api'
import WeatherWidget from '../components/WeatherWidget'
import { 
  Database, 
  AlertTriangle, 
  Truck, 
  Thermometer,
  Droplets,
  Activity
} from 'lucide-react'

interface DashboardKPIs {
  silos: {
    total: number
    active: number
    capacity_utilization: number
    total_capacity_tons: number
    current_volume_tons: number
  }
  readings: {
    average_temperature: number
    average_humidity: number
    total_readings_24h: number
  }
  alerts: {
    active: number
    critical: number
    recent_7_days: number
  }
  logistics: {
    total: number
    in_transit: number
    delivered_today: number
  }
}

const Dashboard: React.FC = () => {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/dashboard/kpis/')
      setKpis(response.data)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="card p-6">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-3/4"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!kpis) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Failed to load dashboard data</p>
      </div>
    )
  }

  const kpiCards = [
    {
      title: 'Active Silos',
      value: `${kpis.silos.active}/${kpis.silos.total}`,
      icon: Database,
      color: 'primary',
      subtitle: `${kpis.silos.capacity_utilization}% capacity utilized`
    },
    {
      title: 'Active Alerts',
      value: kpis.alerts.active,
      icon: AlertTriangle,
      color: kpis.alerts.critical > 0 ? 'red' : 'yellow',
      subtitle: `${kpis.alerts.critical} critical alerts`
    },
    {
      title: 'In Transit',
      value: kpis.logistics.in_transit,
      icon: Truck,
      color: 'blue',
      subtitle: `${kpis.logistics.delivered_today} delivered today`
    },
    {
      title: 'Avg Temperature',
      value: `${kpis.readings.average_temperature}°C`,
      icon: Thermometer,
      color: 'orange',
      subtitle: `${kpis.readings.total_readings_24h} readings (24h)`
    }
  ]

  const getColorClasses = (color: string) => {
    switch (color) {
      case 'primary':
        return 'bg-primary-50 text-primary-600'
      case 'red':
        return 'bg-red-50 text-red-600'
      case 'yellow':
        return 'bg-yellow-50 text-yellow-600'
      case 'blue':
        return 'bg-blue-50 text-blue-600'
      case 'orange':
        return 'bg-orange-50 text-orange-600'
      default:
        return 'bg-gray-50 text-gray-600'
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Real-time overview of your agricultural operations
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiCards.map((card, index) => {
          const Icon = card.icon
          return (
            <div key={index} className="card p-6">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${getColorClasses(card.color)}`}>
                  <Icon className="h-6 w-6" />
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-600">{card.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{card.value}</p>
                  {card.subtitle && (
                    <p className="text-xs text-gray-500 mt-1">{card.subtitle}</p>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Weather Overview */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Weather Conditions</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          <WeatherWidget className="h-fit" />
          <div className="lg:col-span-1 xl:col-span-2 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <p className="text-sm mb-2">📍 Live weather data for all silo locations</p>
              <p className="text-xs">Including agricultural insights like irrigation recommendations, disease risk, and growing degree days</p>
              <a href="/weather" className="text-primary-600 hover:text-primary-700 text-sm font-medium mt-2 inline-block">
                View Complete Weather Dashboard →
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Info Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Storage Overview */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Storage Overview</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Total Capacity</span>
              <span className="font-medium">{kpis.silos.total_capacity_tons.toLocaleString()} tons</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Current Volume</span>
              <span className="font-medium">{kpis.silos.current_volume_tons.toLocaleString()} tons</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-primary-600 h-2 rounded-full" 
                style={{ width: `${kpis.silos.capacity_utilization}%` }}
              ></div>
            </div>
            <div className="text-center text-sm text-gray-600">
              {kpis.silos.capacity_utilization}% Utilized
            </div>
          </div>
        </div>

        {/* Recent Activity Summary */}
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">System Health</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Thermometer className="h-5 w-5 text-orange-500 mr-2" />
                <span className="text-sm text-gray-600">Average Temperature</span>
              </div>
              <span className="font-medium">{kpis.readings.average_temperature}°C</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Droplets className="h-5 w-5 text-blue-500 mr-2" />
                <span className="text-sm text-gray-600">Average Humidity</span>
              </div>
              <span className="font-medium">{kpis.readings.average_humidity}%</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Activity className="h-5 w-5 text-green-500 mr-2" />
                <span className="text-sm text-gray-600">Readings (24h)</span>
              </div>
              <span className="font-medium">{kpis.readings.total_readings_24h}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
                <span className="text-sm text-gray-600">Recent Alerts (7d)</span>
              </div>
              <span className="font-medium">{kpis.alerts.recent_7_days}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="flex flex-wrap gap-3">
          <button className="btn-primary">
            View All Silos
          </button>
          <button className="btn-outline">
            View Active Alerts
          </button>
          <button className="btn-outline">
            Track Logistics
          </button>
          <button className="btn-outline">
            Download Report
          </button>
        </div>
      </div>
    </div>
  )
}

export default Dashboard 
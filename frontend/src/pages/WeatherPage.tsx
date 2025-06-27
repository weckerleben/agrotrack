import React, { useState, useEffect } from 'react'
import { RefreshCw, AlertTriangle, Info, TrendingUp } from 'lucide-react'
import WeatherWidget from '../components/WeatherWidget'
import api from '../services/api'

interface Silo {
  id: number
  name: string
  location: string
  latitude: number
  longitude: number
  status: string
}

interface AgricultureSummary {
  silo_id: number
  silo_name: string
  location: string
  temperature: number
  humidity: number
  weather_condition: string
  agricultural_alerts: Array<{
    type: string
    message: string
  }>
  disease_pressure_risk: string
  frost_risk: string
  irrigation_recommendation: string
  heat_index: number
  growing_degree_days: number
}

const WeatherPage: React.FC = () => {
  const [silos, setSilos] = useState<Silo[]>([])
  const [agSummary, setAgSummary] = useState<AgricultureSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [agLoading, setAgLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchSilos()
    fetchAgriculturalSummary()
  }, [])

  const fetchSilos = async () => {
    try {
      const response = await api.get('/silos/')
      setSilos(response.data.filter((s: Silo) => s.status === 'active'))
    } catch (err) {
      console.error('Error fetching silos:', err)
      setError('Failed to load silo data')
    } finally {
      setLoading(false)
    }
  }

  const fetchAgriculturalSummary = async () => {
    try {
      setAgLoading(true)
      const response = await api.get('/weather/agricultural-summary')
      setAgSummary(response.data.summary || [])
    } catch (err) {
      console.error('Error fetching agricultural summary:', err)
    } finally {
      setAgLoading(false)
    }
  }

  const refreshAll = () => {
    fetchSilos()
    fetchAgriculturalSummary()
  }

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'frost_warning':
        return '❄️'
      case 'disease_risk':
        return '🦠'
      case 'irrigation_needed':
        return '💧'
      case 'heat_stress':
        return '🌡️'
      case 'high_wind':
        return '💨'
      default:
        return '⚠️'
    }
  }

  const getRiskBadgeColor = (risk: string) => {
    switch (risk) {
      case 'high':
        return 'bg-red-100 text-red-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Weather Monitoring</h1>
          <p className="text-gray-600 mt-1">Real-time weather conditions for all silo locations</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Weather Monitoring</h1>
          <p className="text-gray-600 mt-1">
            Real-time weather conditions and agricultural insights for all silo locations
          </p>
        </div>
        <button
          onClick={refreshAll}
          className="btn-outline"
          disabled={loading || agLoading}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${(loading || agLoading) ? 'animate-spin' : ''}`} />
          Refresh All
        </button>
      </div>

      {/* Agricultural Summary */}
      {agSummary.length > 0 && (
        <div className="card p-6">
          <div className="flex items-center mb-4">
            <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900">Agricultural Conditions Summary</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agSummary.map((summary) => (
              <div key={summary.silo_id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="font-medium text-gray-900">{summary.silo_name}</h3>
                    <p className="text-sm text-gray-500">{summary.location}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-gray-900">{Math.round(summary.temperature)}°C</div>
                    <div className="text-sm text-gray-500 capitalize">{summary.weather_condition}</div>
                  </div>
                </div>

                {/* Risk Indicators */}
                <div className="space-y-2 mb-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Disease Risk:</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskBadgeColor(summary.disease_pressure_risk)}`}>
                      {summary.disease_pressure_risk}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Irrigation:</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskBadgeColor(summary.irrigation_recommendation)}`}>
                      {summary.irrigation_recommendation}
                    </span>
                  </div>
                  {summary.frost_risk === 'high' && (
                    <div className="flex items-center text-sm text-blue-600">
                      <span>❄️ Frost Risk</span>
                    </div>
                  )}
                </div>

                {/* Agricultural Metrics */}
                <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 mb-3">
                  <div>Heat Index: {summary.heat_index}°C</div>
                  <div>GDD: {summary.growing_degree_days}</div>
                </div>

                {/* Alerts */}
                {summary.agricultural_alerts.length > 0 && (
                  <div className="space-y-1">
                    {summary.agricultural_alerts.map((alert, index) => (
                      <div key={index} className="flex items-center text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded">
                        <span className="mr-1">{getAlertIcon(alert.type)}</span>
                        {alert.message}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Weather Widgets Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {silos.map((silo) => (
          <WeatherWidget
            key={silo.id}
            siloId={silo.id}
            showDetails={true}
            className="h-auto"
          />
        ))}
      </div>

      {/* Info Box */}
      <div className="card p-4 bg-blue-50 border-blue-200">
        <div className="flex items-start">
          <Info className="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
          <div className="text-sm text-blue-800">
            <h3 className="font-medium mb-1">Agricultural Weather Metrics</h3>
            <ul className="space-y-1 text-xs">
              <li><strong>Heat Index:</strong> Apparent temperature considering humidity effects</li>
              <li><strong>GDD:</strong> Growing Degree Days - accumulation of heat units for crop development</li>
              <li><strong>ET:</strong> Evapotranspiration estimate - water loss from soil and plants</li>
              <li><strong>Disease Risk:</strong> Conditions favorable for plant diseases (temp + humidity)</li>
              <li><strong>Irrigation Need:</strong> Recommendation based on ET and recent rainfall</li>
            </ul>
          </div>
        </div>
      </div>

      {error && (
        <div className="card p-4 bg-red-50 border-red-200">
          <div className="flex items-center text-red-800">
            <AlertTriangle className="h-5 w-5 mr-2" />
            {error}
          </div>
        </div>
      )}
    </div>
  )
}

export default WeatherPage 
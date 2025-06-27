import React, { useState, useEffect } from 'react'
import { Cloud, CloudRain, Sun, Wind, Eye, Gauge, AlertTriangle } from 'lucide-react'
import api from '../services/api'

interface WeatherData {
  silo_id?: number
  silo_name?: string
  location: string
  timestamp: string
  temperature: number
  feels_like: number
  humidity: number
  pressure: number
  visibility: number
  wind_speed: number
  wind_direction: number
  weather_condition: string
  weather_description: string
  weather_icon: string
  clouds: number
  precipitation: {
    rain_1h: number
    rain_3h: number
    snow_1h: number
    snow_3h: number
  }
  sunrise: string
  sunset: string
  agricultural_metrics: {
    heat_index: number
    evapotranspiration_estimate: number
    growing_degree_days: number
    disease_pressure_risk: string
    frost_risk: string
    irrigation_recommendation: string
  }
}

interface WeatherWidgetProps {
  siloId?: number
  showDetails?: boolean
  className?: string
}

const WeatherWidget: React.FC<WeatherWidgetProps> = ({ 
  siloId, 
  showDetails = false, 
  className = "" 
}) => {
  const [weather, setWeather] = useState<WeatherData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchWeather()
  }, [siloId])

  const fetchWeather = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const endpoint = siloId 
        ? `/weather/current/${siloId}`
        : '/weather/current'
      
      const response = await api.get(endpoint)
      
      if (siloId) {
        setWeather(response.data)
      } else {
        // For multiple silos, take the first one or handle accordingly
        const weatherData = response.data.weather_data?.[0]
        if (weatherData) {
          setWeather(weatherData)
        } else {
          setError('No weather data available')
        }
      }
    } catch (err: any) {
      console.error('Error fetching weather:', err)
      setError('Failed to load weather data')
    } finally {
      setLoading(false)
    }
  }

  const getWeatherIcon = (condition: string) => {
    switch (condition.toLowerCase()) {
      case 'clear':
        return <Sun className="h-8 w-8 text-yellow-500" />
      case 'clouds':
        return <Cloud className="h-8 w-8 text-gray-500" />
      case 'rain':
      case 'drizzle':
        return <CloudRain className="h-8 w-8 text-blue-500" />
      case 'snow':
        return <Cloud className="h-8 w-8 text-blue-200" />
      case 'thunderstorm':
        return <Cloud className="h-8 w-8 text-purple-500" />
      default:
        return <Cloud className="h-8 w-8 text-gray-400" />
    }
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'high': return 'text-red-600 bg-red-50'
      case 'medium': return 'text-yellow-600 bg-yellow-50'
      case 'low': return 'text-green-600 bg-green-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const formatTime = (isoString: string) => {
    return new Date(isoString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className={`card p-4 animate-pulse ${className}`}>
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
        <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-2/3"></div>
      </div>
    )
  }

  if (error || !weather) {
    return (
      <div className={`card p-4 ${className}`}>
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
          <p className="text-sm text-gray-500">{error || 'No weather data'}</p>
          <button 
            onClick={fetchWeather}
            className="text-xs text-blue-600 hover:text-blue-800 mt-1"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={`card p-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-medium text-gray-900">
            {weather.silo_name ? `${weather.silo_name} Weather` : 'Weather'}
          </h3>
          <p className="text-xs text-gray-500">{weather.location}</p>
        </div>
        <div className="text-xs text-gray-400">
          {new Date(weather.timestamp).toLocaleTimeString()}
        </div>
      </div>

      {/* Main Weather Display */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
                     {getWeatherIcon(weather.weather_condition)}
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(weather.temperature)}°C
            </div>
            <div className="text-sm text-gray-500 capitalize">
              {weather.weather_description}
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-600">
            Feels like {Math.round(weather.feels_like)}°C
          </div>
          <div className="text-xs text-gray-500">
            Humidity {weather.humidity}%
          </div>
        </div>
      </div>

      {/* Quick Metrics */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="text-center">
          <Wind className="h-4 w-4 text-gray-400 mx-auto mb-1" />
          <div className="text-xs text-gray-600">{weather.wind_speed} m/s</div>
        </div>
        <div className="text-center">
          <Gauge className="h-4 w-4 text-gray-400 mx-auto mb-1" />
          <div className="text-xs text-gray-600">{weather.pressure} hPa</div>
        </div>
        <div className="text-center">
          <Eye className="h-4 w-4 text-gray-400 mx-auto mb-1" />
          <div className="text-xs text-gray-600">{weather.visibility} km</div>
        </div>
      </div>

      {/* Precipitation */}
      {(weather.precipitation.rain_1h > 0 || weather.precipitation.rain_3h > 0) && (
        <div className="mb-4 p-2 bg-blue-50 rounded-lg">
          <div className="flex items-center text-sm text-blue-800">
            <CloudRain className="h-4 w-4 mr-2" />
            Precipitation: {weather.precipitation.rain_1h || weather.precipitation.rain_3h} mm
          </div>
        </div>
      )}

      {/* Agricultural Metrics (if details are shown) */}
      {showDetails && weather.agricultural_metrics && (
        <div className="space-y-3">
          <div className="border-t pt-3">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Agricultural Conditions</h4>
            
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-gray-500">Heat Index:</span>
                <span className="ml-1 font-medium">{weather.agricultural_metrics.heat_index}°C</span>
              </div>
              <div>
                <span className="text-gray-500">GDD:</span>
                <span className="ml-1 font-medium">{weather.agricultural_metrics.growing_degree_days}</span>
              </div>
              <div>
                <span className="text-gray-500">ET:</span>
                <span className="ml-1 font-medium">{weather.agricultural_metrics.evapotranspiration_estimate} mm</span>
              </div>
            </div>
          </div>

          {/* Risk Indicators */}
          <div className="space-y-2">
            <div className={`px-2 py-1 rounded text-xs ${getRiskColor(weather.agricultural_metrics.disease_pressure_risk)}`}>
              Disease Risk: {weather.agricultural_metrics.disease_pressure_risk}
            </div>
            
            {weather.agricultural_metrics.frost_risk === 'high' && (
              <div className="px-2 py-1 rounded text-xs text-blue-600 bg-blue-50">
                ❄️ Frost Risk
              </div>
            )}
            
            <div className={`px-2 py-1 rounded text-xs ${getRiskColor(weather.agricultural_metrics.irrigation_recommendation)}`}>
              Irrigation: {weather.agricultural_metrics.irrigation_recommendation}
            </div>
          </div>

          {/* Sun Times */}
          <div className="border-t pt-2">
            <div className="flex justify-between text-xs text-gray-500">
              <span>🌅 {formatTime(weather.sunrise)}</span>
              <span>🌇 {formatTime(weather.sunset)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Refresh Button */}
      <div className="mt-3 text-center">
        <button
          onClick={fetchWeather}
          className="text-xs text-gray-400 hover:text-gray-600"
        >
          🔄 Refresh
        </button>
      </div>
    </div>
  )
}

export default WeatherWidget 
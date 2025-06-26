import React, { useState, useEffect } from 'react'
import { Database, Plus, MapPin, Thermometer, Droplets, Package, AlertTriangle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

interface Silo {
  id: number
  name: string
  location: string
  capacity_tons: string | number
  max_temperature: string | number
  max_humidity: string | number
  status: string
  latest_reading?: {
    temperature: string | number
    humidity: string | number
    volume_percent: string | number
    volume_tons: string | number
    timestamp: string
  }
  readings_count: number
  average_temperature?: string | number
  average_humidity?: string | number
  current_volume_tons?: string | number
}

const SilosPage: React.FC = () => {
  const { user } = useAuth()
  const [silos, setSilos] = useState<Silo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchSilos()
  }, [])

  const fetchSilos = async () => {
    try {
      setLoading(true)
      const response = await api.get('/silos/')
      setSilos(response.data)
      setError(null)
    } catch (err: any) {
      setError('Failed to fetch silos')
      console.error('Error fetching silos:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'maintenance': return 'bg-yellow-100 text-yellow-800'
      case 'inactive': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getTemperatureStatus = (temp: string | number, maxTemp: string | number) => {
    const tempNum = parseFloat(temp.toString())
    const maxTempNum = parseFloat(maxTemp.toString())
    if (tempNum > maxTempNum) return 'text-red-600'
    if (tempNum > maxTempNum * 0.9) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getHumidityStatus = (humidity: string | number, maxHumidity: string | number) => {
    const humidityNum = parseFloat(humidity.toString())
    const maxHumidityNum = parseFloat(maxHumidity.toString())
    if (humidityNum > maxHumidityNum) return 'text-red-600'
    if (humidityNum > maxHumidityNum * 0.9) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getVolumeStatus = (volume: string | number) => {
    const volumeNum = parseFloat(volume.toString())
    if (volumeNum < 10) return 'text-red-600'
    if (volumeNum < 25) return 'text-yellow-600'
    return 'text-green-600'
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Silos</h1>
            <p className="text-gray-600 mt-1">Manage and monitor all storage facilities</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2 mb-6"></div>
              <div className="space-y-3">
                <div className="h-3 bg-gray-200 rounded"></div>
                <div className="h-3 bg-gray-200 rounded w-5/6"></div>
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
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Silos</h1>
            <p className="text-gray-600 mt-1">Manage and monitor all storage facilities</p>
          </div>
        </div>
        <div className="card p-6">
          <div className="text-center py-12">
            <AlertTriangle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Silos</h3>
            <p className="text-gray-500 mb-4">{error}</p>
            <button onClick={fetchSilos} className="btn-primary">Try Again</button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Silos</h1>
          <p className="text-gray-600 mt-1">
            Manage and monitor all storage facilities
          </p>
        </div>
        {(user?.role === 'admin' || user?.role === 'operator') && (
          <button className="btn-primary">
            <Plus className="h-4 w-4 mr-2" />
            Add Silo
          </button>
        )}
      </div>

      {silos.length === 0 ? (
        <div className="card p-6">
          <div className="text-center py-12">
            <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Silos Found</h3>
            <p className="text-gray-500">
              No storage facilities have been configured yet.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {silos.map((silo) => (
            <div key={silo.id} className="card p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{silo.name}</h3>
                  <div className="flex items-center text-sm text-gray-500 mt-1">
                    <MapPin className="h-4 w-4 mr-1" />
                    {silo.location}
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(silo.status)}`}>
                  {silo.status}
                </span>
              </div>

              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">Capacity</span>
                  <span className="text-sm font-medium">{parseFloat(silo.capacity_tons.toString()).toLocaleString()} tons</span>
                </div>

                {silo.latest_reading && (
                  <>
                    <div className="border-t pt-4">
                      <h4 className="text-sm font-medium text-gray-900 mb-3">Latest Reading</h4>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div className="flex items-center">
                          <Thermometer className={`h-4 w-4 mr-2 ${getTemperatureStatus(silo.latest_reading.temperature, silo.max_temperature)}`} />
                          <div>
                            <div className={`text-sm font-medium ${getTemperatureStatus(silo.latest_reading.temperature, silo.max_temperature)}`}>
                              {parseFloat(silo.latest_reading.temperature.toString()).toFixed(1)}°C
                            </div>
                            <div className="text-xs text-gray-500">Temperature</div>
                          </div>
                        </div>

                        <div className="flex items-center">
                          <Droplets className={`h-4 w-4 mr-2 ${getHumidityStatus(silo.latest_reading.humidity, silo.max_humidity)}`} />
                          <div>
                            <div className={`text-sm font-medium ${getHumidityStatus(silo.latest_reading.humidity, silo.max_humidity)}`}>
                              {parseFloat(silo.latest_reading.humidity.toString()).toFixed(1)}%
                            </div>
                            <div className="text-xs text-gray-500">Humidity</div>
                          </div>
                        </div>

                        <div className="flex items-center col-span-2">
                          <Package className={`h-4 w-4 mr-2 ${getVolumeStatus(silo.latest_reading.volume_percent)}`} />
                          <div className="flex-1">
                            <div className="flex justify-between items-center mb-1">
                              <span className={`text-sm font-medium ${getVolumeStatus(silo.latest_reading.volume_percent)}`}>
                                {parseFloat(silo.latest_reading.volume_percent.toString()).toFixed(1)}%
                              </span>
                              <span className="text-xs text-gray-500">
                                {parseFloat(silo.latest_reading.volume_tons.toString()).toFixed(0)} tons
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${
                                  parseFloat(silo.latest_reading.volume_percent.toString()) < 10 ? 'bg-red-500' :
                                  parseFloat(silo.latest_reading.volume_percent.toString()) < 25 ? 'bg-yellow-500' : 'bg-green-500'
                                }`}
                                style={{ width: `${Math.min(parseFloat(silo.latest_reading.volume_percent.toString()), 100)}%` }}
                              ></div>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="mt-3 text-xs text-gray-500">
                        Last updated: {new Date(silo.latest_reading.timestamp).toLocaleString()}
                      </div>
                    </div>

                    <div className="border-t pt-3">
                      <div className="text-xs text-gray-500">
                        {silo.readings_count} readings in last 24h
                      </div>
                    </div>
                  </>
                )}

                {!silo.latest_reading && (
                  <div className="border-t pt-4">
                    <div className="text-center py-4">
                      <div className="text-sm text-gray-500">No recent readings</div>
                      <div className="text-xs text-gray-400">Waiting for sensor data...</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SilosPage 
import React, { useState } from 'react'
import { X, MapPin, Package, Thermometer, Droplets } from 'lucide-react'
import api from '../services/api'

interface AddSiloModalProps {
  isOpen: boolean
  onClose: () => void
  onSiloAdded: () => void
}

interface SiloFormData {
  name: string
  location: string
  latitude: string
  longitude: string
  capacity_tons: string
  max_temperature: string
  max_humidity: string
  status: string
}

const AddSiloModal: React.FC<AddSiloModalProps> = ({ isOpen, onClose, onSiloAdded }) => {
  const [formData, setFormData] = useState<SiloFormData>({
    name: '',
    location: '',
    latitude: '',
    longitude: '',
    capacity_tons: '',
    max_temperature: '30.0',
    max_humidity: '75.0',
    status: 'active'
  })
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      // Prepare data for API
      const apiData = {
        name: formData.name.trim(),
        location: formData.location.trim(),
        capacity_tons: parseInt(formData.capacity_tons),
        max_temperature: parseFloat(formData.max_temperature),
        max_humidity: parseFloat(formData.max_humidity),
        status: formData.status,
        // Only include coordinates if they're provided
        ...(formData.latitude && formData.longitude && {
          latitude: parseFloat(formData.latitude),
          longitude: parseFloat(formData.longitude)
        })
      }

      await api.post('/silos/', apiData)
      
      // Reset form
      setFormData({
        name: '',
        location: '',
        latitude: '',
        longitude: '',
        capacity_tons: '',
        max_temperature: '30.0',
        max_humidity: '75.0',
        status: 'active'
      })
      
      onSiloAdded()
      onClose()
    } catch (err: any) {
      console.error('Error creating silo:', err)
      setError(err.response?.data?.detail || 'Failed to create silo')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    if (!loading) {
      setFormData({
        name: '',
        location: '',
        latitude: '',
        longitude: '',
        capacity_tons: '',
        max_temperature: '30.0',
        max_humidity: '75.0',
        status: 'active'
      })
      setError(null)
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Add New Silo</h2>
          <button
            onClick={handleClose}
            disabled={loading}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="text-red-800 text-sm">{error}</div>
            </div>
          )}

          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Basic Information</h3>
            
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                Silo Name *
              </label>
              <input
                type="text"
                id="name"
                name="name"
                required
                value={formData.name}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Silo Central A"
              />
            </div>

            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
                Location *
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  id="location"
                  name="location"
                  required
                  value={formData.location}
                  onChange={handleInputChange}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Asunción, Paraguay"
                />
              </div>
            </div>

            <div>
              <label htmlFor="capacity_tons" className="block text-sm font-medium text-gray-700 mb-1">
                Capacity (tons) *
              </label>
              <div className="relative">
                <Package className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="number"
                  id="capacity_tons"
                  name="capacity_tons"
                  required
                  min="1"
                  value={formData.capacity_tons}
                  onChange={handleInputChange}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 1000"
                />
              </div>
            </div>

            <div>
              <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="active">Active</option>
                <option value="maintenance">Maintenance</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>

          {/* Location Coordinates */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">GPS Coordinates (Optional)</h3>
            <p className="text-sm text-gray-600">
              If coordinates are not provided, weather data will be retrieved using the location name.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="latitude" className="block text-sm font-medium text-gray-700 mb-1">
                  Latitude
                </label>
                <input
                  type="number"
                  id="latitude"
                  name="latitude"
                  step="any"
                  value={formData.latitude}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., -25.2637"
                />
              </div>

              <div>
                <label htmlFor="longitude" className="block text-sm font-medium text-gray-700 mb-1">
                  Longitude
                </label>
                <input
                  type="number"
                  id="longitude"
                  name="longitude"
                  step="any"
                  value={formData.longitude}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., -57.5759"
                />
              </div>
            </div>
          </div>

          {/* Monitoring Thresholds */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Monitoring Thresholds</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="max_temperature" className="block text-sm font-medium text-gray-700 mb-1">
                  Max Temperature (°C)
                </label>
                <div className="relative">
                  <Thermometer className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="number"
                    id="max_temperature"
                    name="max_temperature"
                    step="0.1"
                    value={formData.max_temperature}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="30.0"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="max_humidity" className="block text-sm font-medium text-gray-700 mb-1">
                  Max Humidity (%)
                </label>
                <div className="relative">
                  <Droplets className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="number"
                    id="max_humidity"
                    name="max_humidity"
                    step="0.1"
                    value={formData.max_humidity}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="75.0"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-3 pt-4 border-t">
            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Create Silo'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default AddSiloModal 
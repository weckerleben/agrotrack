import React, { useState, useEffect } from 'react'
import { Truck, Plus, MapPin, Package, AlertTriangle, Clock, CheckCircle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

interface LogisticsEntry {
  id: string
  shipment_id: string
  origin: string
  destination: string
  product_type: string
  quantity_tons: number
  status: string
  departure_date: string
  estimated_arrival: string
  actual_arrival?: string
  driver_name: string
  truck_plate: string
  created_at: string
  updated_at: string
}

const LogisticsPage: React.FC = () => {
  const { user } = useAuth()
  const [logistics, setLogistics] = useState<LogisticsEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchLogistics()
  }, [])

  const fetchLogistics = async () => {
    try {
      setLoading(true)
      const response = await api.get('/logistics/')
      setLogistics(response.data)
      setError(null)
    } catch (err: any) {
      setError('Failed to fetch logistics data')
      console.error('Error fetching logistics:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      case 'in_transit': return 'bg-blue-100 text-blue-800'
      case 'delivered': return 'bg-green-100 text-green-800'
      case 'delayed': return 'bg-red-100 text-red-800'
      case 'cancelled': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="h-4 w-4" />
      case 'in_transit': return <Truck className="h-4 w-4" />
      case 'delivered': return <CheckCircle className="h-4 w-4" />
      case 'delayed': return <AlertTriangle className="h-4 w-4" />
      case 'cancelled': return <AlertTriangle className="h-4 w-4" />
      default: return <Package className="h-4 w-4" />
    }
  }

  const filteredLogistics = logistics.filter(entry => {
    if (filter === 'all') return true
    return entry.status === filter
  })

  const pendingShipments = logistics.filter(entry => entry.status === 'pending')
  const inTransitShipments = logistics.filter(entry => entry.status === 'in_transit')
  const deliveredShipments = logistics.filter(entry => entry.status === 'delivered')
  const delayedShipments = logistics.filter(entry => entry.status === 'delayed')

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Logistics</h1>
            <p className="text-gray-600 mt-1">Track shipments and transportation</p>
          </div>
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
          <h1 className="text-2xl font-bold text-gray-900">Logistics</h1>
          <p className="text-gray-600 mt-1">Track shipments and transportation</p>
        </div>
        <div className="card p-6">
          <div className="text-center py-12">
            <AlertTriangle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Logistics</h3>
            <p className="text-gray-500 mb-4">{error}</p>
            <button onClick={fetchLogistics} className="btn-primary">Try Again</button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Logistics</h1>
          <p className="text-gray-600 mt-1">
            Track shipments and transportation
          </p>
        </div>
        {(user?.role === 'admin' || user?.role === 'logistics') && (
          <button className="btn-primary">
            <Plus className="h-4 w-4 mr-2" />
            New Shipment
          </button>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Clock className="h-8 w-8 text-yellow-500" />
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">{pendingShipments.length}</div>
              <div className="text-sm text-gray-500">Pending</div>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Truck className="h-8 w-8 text-blue-500" />
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">{inTransitShipments.length}</div>
              <div className="text-sm text-gray-500">In Transit</div>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">{deliveredShipments.length}</div>
              <div className="text-sm text-gray-500">Delivered</div>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-8 w-8 text-red-500" />
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">{delayedShipments.length}</div>
              <div className="text-sm text-gray-500">Delayed</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filter */}
      <div className="card p-4">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">Filter by status:</span>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="text-sm border border-gray-300 rounded-md px-3 py-1"
          >
            <option value="all">All Shipments</option>
            <option value="pending">Pending</option>
            <option value="in_transit">In Transit</option>
            <option value="delivered">Delivered</option>
            <option value="delayed">Delayed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Shipments List */}
      {filteredLogistics.length === 0 ? (
        <div className="card p-6">
          <div className="text-center py-12">
            <Truck className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Shipments Found</h3>
            <p className="text-gray-500">
              {logistics.length === 0 
                ? "No shipments have been created yet."
                : "No shipments match the current filter."
              }
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredLogistics.map((entry) => (
            <div key={entry.id} className="card p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-1">
                    <div className={`p-2 rounded-full ${
                      entry.status === 'delivered' ? 'bg-green-100' :
                      entry.status === 'in_transit' ? 'bg-blue-100' :
                      entry.status === 'delayed' ? 'bg-red-100' : 'bg-yellow-100'
                    }`}>
                      {getStatusIcon(entry.status)}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        Shipment #{entry.shipment_id}
                      </h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(entry.status)}`}>
                        {entry.status.replace('_', ' ')}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <div className="flex items-center text-sm text-gray-600 mb-1">
                          <MapPin className="h-4 w-4 mr-1" />
                          <span className="font-medium">Route:</span>
                        </div>
                        <div className="text-sm text-gray-900 ml-5">
                          {entry.origin} → {entry.destination}
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex items-center text-sm text-gray-600 mb-1">
                          <Package className="h-4 w-4 mr-1" />
                          <span className="font-medium">Cargo:</span>
                        </div>
                        <div className="text-sm text-gray-900 ml-5">
                          {entry.quantity_tons} tons of {entry.product_type}
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Driver:</span>
                        <div className="font-medium">{entry.driver_name}</div>
                      </div>
                      <div>
                        <span className="text-gray-500">Truck:</span>
                        <div className="font-medium">{entry.truck_plate}</div>
                      </div>
                      <div>
                        <span className="text-gray-500">Departure:</span>
                        <div className="font-medium">{new Date(entry.departure_date).toLocaleDateString()}</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm mt-2">
                      <div>
                        <span className="text-gray-500">Est. Arrival:</span>
                        <div className="font-medium">{new Date(entry.estimated_arrival).toLocaleDateString()}</div>
                      </div>
                      {entry.actual_arrival && (
                        <div>
                          <span className="text-gray-500">Actual Arrival:</span>
                          <div className="font-medium">{new Date(entry.actual_arrival).toLocaleDateString()}</div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex-shrink-0">
                  {(user?.role === 'admin' || user?.role === 'logistics') && entry.status !== 'delivered' && entry.status !== 'cancelled' && (
                    <button className="btn btn-outline text-sm">
                      Update Status
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

export default LogisticsPage 
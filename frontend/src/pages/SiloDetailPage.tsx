import React from 'react'
import { useParams } from 'react-router-dom'
import { Database } from 'lucide-react'

const SiloDetailPage: React.FC = () => {
  const { id } = useParams()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Silo Details</h1>
        <p className="text-gray-600 mt-1">
          Detailed information for Silo ID: {id}
        </p>
      </div>

      <div className="card p-6">
        <div className="text-center py-12">
          <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Silo Detail View</h3>
          <p className="text-gray-500">
            This page will show detailed silo information, real-time readings, charts, and alerts.
          </p>
        </div>
      </div>
    </div>
  )
}

export default SiloDetailPage 
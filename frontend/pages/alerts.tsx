import { useState, useEffect } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import Header from '@/components/Header'
import {
  BellIcon,
  PlusIcon,
  XMarkIcon,
  TrashIcon,
  PauseIcon,
  PlayIcon,
  ExclamationTriangleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'
import { API_BASE_URL } from '@/utils/api'

interface Alert {
  id: string
  name: string
  keywords?: string
  category?: string
  remote_type?: string
  location?: string
  salary_min?: number
  is_active: boolean
  frequency: string
}

const categories = [
  'Software Development', 'Data Science', 'Design', 'Marketing', 'Sales',
  'Customer Support', 'Product Management', 'DevOps',
]

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [newAlert, setNewAlert] = useState({
    name: '', keywords: '', category: '', remote_type: 'full_remote',
    location: '', salary_min: '', frequency: 'daily'
  })

  useEffect(() => {
    loadAlerts()
  }, [])

  const loadAlerts = async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      setError('Please login to manage alerts')
      setLoading(false)
      return
    }
    try {
      const response = await fetch(`${API_BASE_URL}/alerts/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!response.ok) throw new Error('Failed to load alerts')
      setAlerts(await response.json())
    } catch (err) {
      setError('Failed to load alerts')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    const token = localStorage.getItem('token')
    if (!token) return
    try {
      const response = await fetch(`${API_BASE_URL}/alerts/`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newAlert.name,
          keywords: newAlert.keywords,
          category: newAlert.category || null,
          remote_type: newAlert.remote_type || null,
          location: newAlert.location || null,
          salary_min: newAlert.salary_min ? parseInt(newAlert.salary_min) : null,
          frequency: newAlert.frequency
        })
      })
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create alert')
      }
      setShowForm(false)
      setNewAlert({ name: '', keywords: '', category: '', remote_type: 'full_remote', location: '', salary_min: '', frequency: 'daily' })
      loadAlerts()
    } catch (err: any) {
      setError(err.message || 'Failed to create alert')
    }
  }

  const toggleAlert = async (alert: Alert) => {
    const token = localStorage.getItem('token')
    if (!token) return
    try {
      await fetch(`${API_BASE_URL}/alerts/${alert.id}`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !alert.is_active })
      })
      loadAlerts()
    } catch (err) {
      console.error('Failed to toggle alert')
    }
  }

  const deleteAlert = async (alertId: string) => {
    const token = localStorage.getItem('token')
    if (!token) return
    setAlerts(alerts.filter(a => a.id !== alertId))
    try {
      await fetch(`${API_BASE_URL}/alerts/${alertId}`, {
        method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` }
      })
    } catch (err) {
      console.error('Failed to delete alert')
    }
  }

  const inputCls = "input-app !py-2.5"

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Job Alerts - RemoteJobHub</title>
        <meta name="description" content="Set up alerts to be notified when new remote jobs are posted" />
      </Head>

      <Header />

      <main className="container-app pb-16 pt-10">
        <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">
              Job <span className="text-gradient">Alerts</span>
            </h1>
            <p className="mt-2 text-gray-600">
              Get notified when new jobs matching your criteria are posted
            </p>
          </div>
          <button onClick={() => setShowForm(!showForm)} className="btn-primary">
            <PlusIcon className="h-4 w-4" />
            New Alert
          </button>
        </div>

        {error && (
          <div className="mb-8 flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-5">
            <ExclamationTriangleIcon className="h-5 w-5 shrink-0 text-red-500" />
            <div>
              <p className="text-red-700">{error}</p>
              <Link href="/login" className="mt-1 inline-block text-sm font-semibold text-brand-600 hover:underline">
                Login here
              </Link>
            </div>
          </div>
        )}

        {/* Create form */}
        {showForm && (
          <form onSubmit={handleCreate} className="mb-8 animate-fade-in-up rounded-2xl border border-brand-100 bg-white p-6 shadow-card sm:p-8">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="font-display text-xl font-bold text-gray-900">Create New Alert</h2>
              <button type="button" onClick={() => setShowForm(false)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
            <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700">Alert Name *</label>
                <input type="text" required value={newAlert.name}
                  onChange={(e) => setNewAlert({...newAlert, name: e.target.value})}
                  placeholder="e.g., Senior React Jobs" className={inputCls} />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700">Keywords</label>
                <input type="text" value={newAlert.keywords}
                  onChange={(e) => setNewAlert({...newAlert, keywords: e.target.value})}
                  placeholder="React, TypeScript, Remote" className={inputCls} />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700">Category</label>
                <select value={newAlert.category}
                  onChange={(e) => setNewAlert({...newAlert, category: e.target.value})}
                  className={inputCls}>
                  <option value="">All Categories</option>
                  {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
                </select>
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700">Remote Type</label>
                <select value={newAlert.remote_type}
                  onChange={(e) => setNewAlert({...newAlert, remote_type: e.target.value})}
                  className={inputCls}>
                  <option value="full_remote">Full Remote</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="onsite">On-site</option>
                </select>
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700">Location</label>
                <input type="text" value={newAlert.location}
                  onChange={(e) => setNewAlert({...newAlert, location: e.target.value})}
                  placeholder="Europe, USA, Global" className={inputCls} />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700">Min Salary (USD)</label>
                <input type="number" value={newAlert.salary_min}
                  onChange={(e) => setNewAlert({...newAlert, salary_min: e.target.value})}
                  placeholder="75000" className={inputCls} />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-gray-700">Frequency</label>
                <select value={newAlert.frequency}
                  onChange={(e) => setNewAlert({...newAlert, frequency: e.target.value})}
                  className={inputCls}>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="instant">Instant</option>
                </select>
              </div>
            </div>
            <div className="mt-6 flex gap-3">
              <button type="submit" className="btn-primary">Create Alert</button>
              <button type="button" onClick={() => setShowForm(false)} className="btn-ghost">Cancel</button>
            </div>
          </form>
        )}

        {loading ? (
          <div className="flex flex-col items-center justify-center py-24">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-brand-600" />
            <p className="mt-4 text-sm text-gray-500">Loading alerts...</p>
          </div>
        ) : alerts.length === 0 && !error ? (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white py-24 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-100">
              <BellIcon className="h-8 w-8 text-gray-400" />
            </div>
            <p className="mt-4 font-display text-lg font-semibold text-gray-900">No alerts yet</p>
            <p className="mt-1 text-sm text-gray-500">Create an alert to get notified about new matching jobs.</p>
            <button onClick={() => setShowForm(true)} className="btn-primary mt-6">
              <PlusIcon className="h-4 w-4" />
              Create your first alert
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div key={alert.id} className="rounded-2xl border border-gray-100 bg-white p-6 shadow-card transition-all hover:border-brand-200 hover:shadow-lift">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-display text-lg font-bold text-gray-900">{alert.name}</h3>
                      <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium capitalize text-gray-600">
                        <ClockIcon className="h-3.5 w-3.5" />
                        {alert.frequency}
                      </span>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {alert.keywords && (
                        <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-600">{alert.keywords}</span>
                      )}
                      {alert.category && (
                        <span className="rounded-full bg-brand-50 px-2.5 py-1 text-xs font-semibold text-brand-700">{alert.category}</span>
                      )}
                      {alert.remote_type && (
                        <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 capitalize">{alert.remote_type.replace('_', ' ')}</span>
                      )}
                      {alert.location && (
                        <span className="rounded-full bg-purple-50 px-2.5 py-1 text-xs font-semibold text-purple-700">{alert.location}</span>
                      )}
                      {alert.salary_min && (
                        <span className="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700">${alert.salary_min.toLocaleString()}+</span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${alert.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-100 text-gray-500'}`}>
                      <span className={`h-1.5 w-1.5 rounded-full ${alert.is_active ? 'bg-emerald-500' : 'bg-gray-400'}`} />
                      {alert.is_active ? 'Active' : 'Paused'}
                    </span>
                    <button onClick={() => toggleAlert(alert)} className="btn-ghost !px-3 !py-2"
                      title={alert.is_active ? 'Pause' : 'Resume'}>
                      {alert.is_active ? <PauseIcon className="h-4 w-4" /> : <PlayIcon className="h-4 w-4" />}
                      <span className="hidden sm:inline">{alert.is_active ? 'Pause' : 'Resume'}</span>
                    </button>
                    <button onClick={() => deleteAlert(alert.id)} className="btn-ghost !px-3 !py-2 text-red-600 hover:border-red-300 hover:text-red-700">
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

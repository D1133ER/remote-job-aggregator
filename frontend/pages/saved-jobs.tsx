import { useState, useEffect } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import Header from '@/components/Header'
import JobCard from '@/components/JobCard'
import { BookmarkIcon, TrashIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import { API_BASE_URL } from '@/utils/api'

interface SavedJob {
  id: string
  job_id: string
  notes?: string
  created_at: string
  job: {
    id: string
    title: string
    company_name: string
    location: string
    remote_type: string
    skills: string[]
    posted_at: string
    category: string
    company_logo_url?: string
    salary_display?: string
    summary?: string
  }
}

export default function SavedJobs() {
  const [savedJobs, setSavedJobs] = useState<SavedJob[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadSavedJobs()
  }, [])

  const loadSavedJobs = async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      setError('Please login to view saved jobs')
      setLoading(false)
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/saved-jobs/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (!response.ok) throw new Error('Failed to load saved jobs')

      const data = await response.json()
      setSavedJobs(data)
    } catch (err) {
      setError('Failed to load saved jobs')
    } finally {
      setLoading(false)
    }
  }

  const removeSavedJob = async (savedJobId: string) => {
    const token = localStorage.getItem('token')
    if (!token) return
    setSavedJobs(savedJobs.filter(j => j.id !== savedJobId))
    try {
      await fetch(`${API_BASE_URL}/saved-jobs/${savedJobId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
    } catch (err) {
      console.error('Failed to remove saved job')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Saved Jobs - RemoteJobHub</title>
        <meta name="description" content="Your saved jobs and applications" />
      </Head>

      <Header />

      <main className="container-app pb-16 pt-10">
        <div className="mb-8">
          <h1 className="font-display text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">
            Saved <span className="text-gradient">Jobs</span>
          </h1>
          <p className="mt-2 text-gray-600">Jobs you've saved for later review</p>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-24">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-brand-600" />
            <p className="mt-4 text-sm text-gray-500">Loading saved jobs...</p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white py-24 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-amber-50">
              <ExclamationTriangleIcon className="h-8 w-8 text-amber-500" />
            </div>
            <p className="mt-4 font-semibold text-gray-900">{error}</p>
            <Link href="/login" className="btn-primary mt-6">
              Login here
            </Link>
          </div>
        ) : savedJobs.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white py-24 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-100">
              <BookmarkIcon className="h-8 w-8 text-gray-400" />
            </div>
            <p className="mt-4 font-display text-lg font-semibold text-gray-900">
              You haven't saved any jobs yet
            </p>
            <p className="mt-1 text-sm text-gray-500">Save jobs you like to review them later.</p>
            <Link href="/" className="btn-primary mt-6">
              Browse Jobs
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {savedJobs.map((savedJob) => (
              <div key={savedJob.id} className="group relative">
                <JobCard job={savedJob.job} />
                {savedJob.notes && (
                  <div className="mt-2 ml-6 rounded-xl border-l-2 border-brand-300 bg-brand-50 px-4 py-2 text-sm text-brand-700">
                    Note: {savedJob.notes}
                  </div>
                )}
                <button
                  onClick={() => removeSavedJob(savedJob.id)}
                  className="absolute right-4 top-4 inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-gray-400 opacity-100 transition-all hover:bg-red-50 hover:text-red-600 sm:opacity-0 sm:group-hover:opacity-100"
                >
                  <TrashIcon className="h-4 w-4" />
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

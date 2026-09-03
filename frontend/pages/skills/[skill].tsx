import { useRouter } from 'next/router'
import Head from 'next/head'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import Header from '@/components/Header'
import JobCard from '@/components/JobCard'
import { CodeBracketIcon, ArrowLeftIcon } from '@heroicons/react/24/outline'
import { API_BASE_URL } from '@/utils/api'

interface Job {
  id: string
  title: string
  company_name: string
  company_logo_url?: string
  location: string
  remote_type: string
  salary_display?: string
  summary?: string
  skills: string[]
  posted_at: string
  category: string
}

export default function SkillJobsPage() {
  const router = useRouter()
  const { skill } = router.query
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!skill) return
    loadJobs()
  }, [skill])

  const loadJobs = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/search/?q=${skill}`)
      const data = await response.json()
      setJobs(data.jobs || [])
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const skillName = Array.isArray(skill) ? skill[0] : skill || ''

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Remote {skillName} Jobs - RemoteJobHub</title>
        <meta name="description" content={`Find the best remote ${skillName} jobs from top companies worldwide.`} />
      </Head>

      <Header />

      <main className="container-app pb-16 pt-10">
        <Link href="/" className="inline-flex items-center gap-1.5 text-sm font-medium text-gray-500 transition-colors hover:text-brand-600">
          <ArrowLeftIcon className="h-4 w-4" />
          Browse all jobs
        </Link>

        <div className="mt-6 mb-8">
          <span className="bg-gradient-brand inline-flex h-14 w-14 items-center justify-center rounded-2xl text-white shadow-lift">
            <CodeBracketIcon className="h-7 w-7" />
          </span>
          <h1 className="font-display mt-4 text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">
            Remote <span className="text-gradient">{skillName}</span> Jobs
          </h1>
          <p className="mt-2 text-gray-600">
            {loading ? 'Loading...' : `${jobs.length} remote ${skillName} jobs available`}
          </p>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-24">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-brand-600" />
            <p className="mt-4 text-sm text-gray-500">Loading {skillName} jobs...</p>
          </div>
        ) : jobs.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white py-24 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-100">
              <CodeBracketIcon className="h-8 w-8 text-gray-400" />
            </div>
            <p className="mt-4 font-display text-lg font-semibold text-gray-900">
              No remote {skillName} jobs found
            </p>
            <Link href="/" className="btn-primary mt-6">Browse all jobs</Link>
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

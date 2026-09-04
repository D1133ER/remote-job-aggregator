import { useRouter } from 'next/router'
import Head from 'next/head'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import Header from '@/components/Header'
import {
  ArrowLeftIcon,
  BriefcaseIcon,
  MapPinIcon,
  ClockIcon,
  ArrowUpRightIcon,
  CheckBadgeIcon,
  ArrowTopRightOnSquareIcon,
} from '@heroicons/react/24/outline'
import { getJob } from '@/utils/api'
import { formatDistanceToNow } from 'date-fns'

interface Job {
  id: string
  title: string
  company_name: string
  company_logo_url?: string
  company_website?: string
  description?: string
  location?: string
  remote_type?: string
  salary_display?: string
  salary_min?: number
  salary_max?: number
  salary_currency?: string
  summary?: string
  skills: string[]
  posted_at?: string
  category?: string
  job_type?: string
  experience_level?: string
  source_url?: string
  apply_url?: string
  source_name?: string
  is_verified?: boolean
}

export default function JobDetail() {
  const router = useRouter()
  const { id } = router.query
  const [job, setJob] = useState<Job | null>(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    if (!id) return
    loadJob()
  }, [id])

  const loadJob = async () => {
    setLoading(true)
    try {
      const data = await getJob(id as string)
      setJob(data)
    } catch (err: any) {
      if (err.response?.status === 404) setNotFound(true)
      else console.error('Failed to load job:', err)
    } finally {
      setLoading(false)
    }
  }

  const openApplication = () => {
    const target = job?.apply_url || job?.source_url
    if (!target) return
    const w = window.open(target, '_blank', 'noopener,noreferrer')
    if (w) w.opener = null
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex min-h-[60vh] items-center justify-center">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-brand-600" />
        </div>
      </div>
    )
  }

  if (notFound || !job) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="container-app flex flex-col items-center justify-center pb-16 pt-24 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-100">
            <BriefcaseIcon className="h-8 w-8 text-gray-400" />
          </div>
          <h1 className="mt-4 font-display text-2xl font-bold text-gray-900">Job not found</h1>
          <p className="mt-2 text-gray-500">
            This job may have been removed or is no longer active.
          </p>
          <Link href="/" className="btn-primary mt-6">
            <ArrowLeftIcon className="mr-1 h-4 w-4" /> Back to jobs
          </Link>
        </div>
      </div>
    )
  }

  const applyTarget = job.apply_url || job.source_url
  const hasSalary = job.salary_min != null || job.salary_max != null

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>{job.title} at {job.company_name} | RemoteJobHub</title>
        <meta
          name="description"
          content={job.summary || `Apply for ${job.title} at ${job.company_name} — a remote job.`}
        />
      </Head>

      <Header />

      <main className="container-app pb-16 pt-8">
        <Link href="/" className="inline-flex items-center gap-1 text-sm font-medium text-gray-500 transition-colors hover:text-brand-600">
          <ArrowLeftIcon className="h-4 w-4" /> Back to all jobs
        </Link>

        <div className="mt-6 rounded-2xl border border-gray-100 bg-white p-6 shadow-card sm:p-8">
          {/* Header */}
          <div className="flex flex-col gap-4 border-b border-gray-100 pb-6 sm:flex-row sm:items-start sm:justify-between">
            <div className="flex items-start gap-4">
              {job.company_logo_url ? (
                <img
                  src={job.company_logo_url}
                  alt={`${job.company_name} logo`}
                  className="h-14 w-14 shrink-0 rounded-xl object-contain"
                />
              ) : (
                <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-gradient-brand text-xl font-bold text-white">
                  {job.company_name.charAt(0).toUpperCase()}
                </div>
              )}
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="font-display text-2xl font-extrabold tracking-tight text-gray-900">
                    {job.title}
                  </h1>
                  {job.is_verified && (
                    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-semibold text-emerald-700">
                      <CheckBadgeIcon className="h-3.5 w-3.5" /> Legitimate
                    </span>
                  )}
                </div>
                <p className="mt-1 text-sm font-medium text-gray-500">{job.company_name}</p>

                <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-gray-500">
                  <div className="flex items-center">
                    <MapPinIcon className="mr-1.5 h-4 w-4 text-gray-400" />
                    <span className="font-medium text-gray-700">{job.location || 'Remote'}</span>
                  </div>
                  <div className="flex items-center">
                    <BriefcaseIcon className="mr-1.5 h-4 w-4 text-gray-400" />
                    <span className="capitalize">{(job.remote_type || 'Full Remote').replace('_', ' ')}</span>
                  </div>
                  {job.posted_at && (
                    <div className="flex items-center">
                      <ClockIcon className="mr-1.5 h-4 w-4 text-gray-400" />
                      <span>{formatDistanceToNow(new Date(job.posted_at), { addSuffix: true })}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Apply CTA */}
            {applyTarget && (
              <div className="shrink-0 sm:text-right">
                <button
                  type="button"
                  onClick={openApplication}
                  className="btn-primary inline-flex w-full items-center justify-center gap-2 !px-6 !py-3 text-base sm:w-auto"
                >
                  Apply Now
                  <ArrowTopRightOnSquareIcon className="h-4 w-4" />
                </button>
                <p className="mt-2 flex items-center justify-center gap-1 text-xs text-gray-400 sm:justify-end">
                  <CheckBadgeIcon className="h-3.5 w-3.5 text-emerald-500" />
                  Opens the official application page
                </p>
              </div>
            )}
          </div>

          {/* Details grid */}
          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {hasSalary && (
              <div className="rounded-xl bg-emerald-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-emerald-600">Salary</p>
                <p className="mt-1 text-lg font-bold text-emerald-800">
                  {job.salary_display ||
                    (() => {
                      const parts: string[] = []
                      if (job.salary_min != null) parts.push(`$${job.salary_min.toLocaleString()}`)
                      if (job.salary_max != null) parts.push(`$${job.salary_max.toLocaleString()}`)
                      return parts.join(' – ') + (job.salary_currency ? ` ${job.salary_currency}` : '')
                    })()}
                </p>
              </div>
            )}
            {job.category && (
              <div className="rounded-xl bg-gray-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Category</p>
                <p className="mt-1 text-lg font-bold capitalize text-gray-800">{job.category}</p>
              </div>
            )}
            {job.job_type && (
              <div className="rounded-xl bg-gray-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Job Type</p>
                <p className="mt-1 text-lg font-bold capitalize text-gray-800">{job.job_type}</p>
              </div>
            )}
            {job.experience_level && (
              <div className="rounded-xl bg-gray-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Experience</p>
                <p className="mt-1 text-lg font-bold capitalize text-gray-800">{job.experience_level}</p>
              </div>
            )}
          </div>

          {/* Description */}
          {job.description && (
            <div className="mt-8">
              <h2 className="font-display text-lg font-bold text-gray-900">Job Description</h2>
              <div
                className="prose prose-gray mt-4 max-w-none whitespace-pre-line text-sm leading-relaxed text-gray-700"
              >
                {job.description}
              </div>
            </div>
          )}

          {/* Skills */}
          {job.skills && job.skills.length > 0 && (
            <div className="mt-8">
              <h2 className="font-display text-lg font-bold text-gray-900">Skills</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {job.skills.map((skill) => (
                  <Link
                    key={skill}
                    href={`/skills/${encodeURIComponent(skill)}`}
                    className="rounded-md bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-600 transition-colors hover:bg-brand-50 hover:text-brand-700"
                  >
                    {skill}
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Footer actions */}
          <div className="mt-8 flex flex-col items-start justify-between gap-4 border-t border-gray-100 pt-6 sm:flex-row sm:items-center">
            {applyTarget ? (
              <div>
                <p className="text-sm font-semibold text-gray-700">Ready to apply?</p>
                <p className="mt-0.5 text-xs text-gray-400">
                  You will be redirected to the official application page hosted by{' '}
                  {job.source_name ? (
                    <span className="capitalize">{job.source_name}</span>
                  ) : (
                    job.company_name
                  )}
                </p>
              </div>
            ) : (
              <p className="text-sm text-gray-500">
                No direct application link is available for this posting.
              </p>
            )}

            <div className="flex shrink-0 items-center gap-3">
              {job.company_website && (
                <a
                  href={job.company_website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 transition-colors hover:border-brand-200 hover:text-brand-700"
                >
                  Company website
                  <ArrowUpRightIcon className="h-4 w-4" />
                </a>
              )}
              {applyTarget && (
                <button
                  type="button"
                  onClick={openApplication}
                  className="btn-primary inline-flex items-center gap-2 !px-6 !py-2.5"
                >
                  Apply Now
                  <ArrowTopRightOnSquareIcon className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

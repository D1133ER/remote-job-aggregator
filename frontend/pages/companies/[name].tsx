import { useRouter } from 'next/router'
import Head from 'next/head'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import Header from '@/components/Header'
import JobCard from '@/components/JobCard'
import { ArrowLeftIcon, GlobeAltIcon, ChartBarIcon, BriefcaseIcon, SparklesIcon } from '@heroicons/react/24/outline'
import { getCompany, getCompanyStats, getCompanyJobs } from '@/utils/api'

interface Company {
  id: string
  name: string
  logo_url?: string
  website?: string
  description?: string
  industry?: string
  remote_policy?: string
  average_response_time?: string
  total_jobs_posted: number
  total_jobs_remote: number
}

interface CompanyStats {
  total_jobs: number
  remote_jobs: number
  average_salary_min: number | null
  average_salary_max: number | null
  top_skills: string[]
  categories: string[]
}

interface Job {
  id: string
  title: string
  company_name: string
  location?: string
  remote_type?: string
  salary_display?: string
  skills?: string[]
  posted_at?: string
  category?: string
}

export default function CompanyDetail() {
  const router = useRouter()
  const { name } = router.query
  const [company, setCompany] = useState<Company | null>(null)
  const [stats, setStats] = useState<CompanyStats | null>(null)
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!name) return
    loadCompany()
  }, [name])

  const loadCompany = async () => {
    const decodedName = decodeURIComponent(name as string)
    try {
      const [companyRes, statsRes, jobsRes] = await Promise.allSettled([
        getCompany(decodedName),
        getCompanyStats(decodedName),
        getCompanyJobs(decodedName),
      ])

      if (companyRes.status === 'fulfilled') {
        setCompany(companyRes.value)
      }
      if (statsRes.status === 'fulfilled') {
        setStats(statsRes.value)
      }
      if (jobsRes.status === 'fulfilled') {
        setJobs(jobsRes.value.jobs || jobsRes.value || [])
      }
    } catch (error) {
      console.error('Failed to load company:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-brand-600" />
      </div>
    )
  }

  if (!company) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="font-display text-2xl font-bold text-gray-900">Company not found</h1>
          <Link href="/companies" className="btn-primary mt-6">
            Back to companies
          </Link>
        </div>
      </div>
    )
  }

  const statsCards = [
    { label: 'Total Jobs', value: stats?.total_jobs ?? company.total_jobs_posted, icon: ChartBarIcon, color: 'text-brand-600 bg-brand-50' },
    { label: 'Remote Jobs', value: stats?.remote_jobs ?? company.total_jobs_remote, icon: BriefcaseIcon, color: 'text-emerald-600 bg-emerald-50' },
    {
      label: 'Avg Salary',
      value: stats?.average_salary_min
        ? `$${Math.round(stats.average_salary_min / 1000)}k-$${Math.round((stats.average_salary_max || 0) / 1000)}k`
        : 'N/A',
      icon: SparklesIcon,
      color: 'text-amber-600 bg-amber-50',
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>{company.name} - RemoteJobHub</title>
        <meta name="description" content={`Remote jobs at ${company.name}. View company profile and open positions.`} />
      </Head>

      <Header />

      <main className="container-app pb-16 pt-6">
        <Link href="/companies" className="inline-flex items-center gap-1.5 text-sm font-medium text-gray-500 transition-colors hover:text-brand-600">
          <ArrowLeftIcon className="h-4 w-4" />
          Back to companies
        </Link>

        {/* Company header card */}
        <div className="mt-6 overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-card">
          <div className="bg-gradient-brand relative h-28">
            <div className="pointer-events-none absolute -top-10 right-10 h-40 w-40 rounded-full bg-white/10 blur-2xl" />
          </div>
          <div className="px-6 pb-6 sm:px-8">
            <div className="-mt-12 flex items-end gap-5">
              {company.logo_url ? (
                <img
                  src={company.logo_url}
                  alt={`${company.name} logo`}
                  className="h-24 w-24 rounded-2xl border-4 border-white bg-white object-contain shadow-card"
                />
              ) : (
                <div className="bg-gradient-brand flex h-24 w-24 items-center justify-center rounded-2xl border-4 border-white text-4xl font-bold text-white shadow-card">
                  {company.name.charAt(0)}
                </div>
              )}
              <div className="flex-1 pb-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="font-display text-2xl font-extrabold tracking-tight text-gray-900 sm:text-3xl">
                    {company.name}
                  </h1>
                  {company.industry && (
                    <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-600">
                      {company.industry}
                    </span>
                  )}
                </div>
                <div className="mt-1.5 flex flex-wrap gap-2">
                  {company.remote_policy && (
                    <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700">
                      {company.remote_policy === 'full_remote' ? 'Fully Remote' : company.remote_policy}
                    </span>
                  )}
                  {company.website && (
                    <a
                      href={company.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-semibold text-brand-700 transition-colors hover:bg-brand-100"
                    >
                      <GlobeAltIcon className="h-3.5 w-3.5" />
                      Website
                    </a>
                  )}
                </div>
              </div>
            </div>

            {company.description && (
              <p className="mt-6 text-gray-600">{company.description}</p>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          {statsCards.map((card) => (
            <div key={card.label} className="flex items-center gap-4 rounded-2xl border border-gray-100 bg-white p-5 shadow-card">
              <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${card.color}`}>
                <card.icon className="h-6 w-6" />
              </div>
              <div>
                <div className="font-display text-2xl font-bold text-gray-900">{card.value}</div>
                <div className="text-sm text-gray-500">{card.label}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Top skills */}
        {stats && stats.top_skills.length > 0 && (
          <div className="mt-6 rounded-2xl border border-gray-100 bg-white p-6 shadow-card">
            <h2 className="mb-4 font-display text-lg font-bold text-gray-900">Top Skills</h2>
            <div className="flex flex-wrap gap-2">
              {stats.top_skills.map((skill) => (
                <span
                  key={skill}
                  className="rounded-lg bg-brand-50 px-3 py-1.5 text-sm font-medium text-brand-700 transition-colors hover:bg-brand-100"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Open positions */}
        <div className="mt-8">
          <h2 className="mb-4 font-display text-xl font-bold text-gray-900">
            Open Positions{' '}
            <span className="ml-1 rounded-full bg-brand-100 px-2.5 py-0.5 text-sm font-semibold text-brand-700">
              {jobs.length}
            </span>
          </h2>

          {jobs.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white py-20 text-center">
              <BriefcaseIcon className="h-12 w-12 text-gray-300" />
              <p className="mt-4 font-semibold text-gray-900">No open positions at this time</p>
              <p className="mt-1 text-sm text-gray-500">
                Check back soon or set up a job alert for {company.name}.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {jobs.map((job) => (
                <JobCard
                  key={job.id}
                  job={{
                    id: job.id,
                    title: job.title,
                    company_name: company.name,
                    location: job.location || 'Remote',
                    remote_type: job.remote_type || 'full_remote',
                    salary_display: job.salary_display,
                    skills: job.skills || [],
                    posted_at: job.posted_at || new Date().toISOString(),
                    category: job.category || '',
                    summary: undefined,
                    company_logo_url: company.logo_url,
                  }}
                />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

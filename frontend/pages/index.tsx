import { useState, useEffect } from 'react'
import Head from 'next/head'
import Header from '@/components/Header'
import Hero from '@/components/Hero'
import JobCard from '@/components/JobCard'
import SearchBar from '@/components/SearchBar'
import FilterSidebar from '@/components/FilterSidebar'
import { ChevronLeftIcon, ChevronRightIcon, BriefcaseIcon } from '@heroicons/react/24/outline'
import { API_BASE_URL } from '@/utils/api'

interface Job {
  id: string
  title: string
  company_name: string
  location: string
  remote_type: string
  salary_display?: string
  skills: string[]
  posted_at: string
  category: string
  summary?: string
  company_logo_url?: string
}

const EMPTY_FILTERS = {
  query: '',
  category: '',
  remoteType: '',
  experienceLevel: '',
  salaryMin: null as number | null,
  skills: [] as string[],
}

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [companiesCount, setCompaniesCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState(EMPTY_FILTERS)
  const [page, setPage] = useState(1)
  const [totalJobs, setTotalJobs] = useState(0)
  const [sort, setSort] = useState('recent')

  useEffect(() => {
    loadJobs()
  }, [filters, page, sort])

  const loadJobs = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (filters.query) params.append('q', filters.query)
      if (filters.category) params.append('category', filters.category)
      if (filters.remoteType) params.append('remote_type', filters.remoteType)
      if (filters.experienceLevel) params.append('experience_level', filters.experienceLevel)
      if (filters.salaryMin) params.append('salary_min', filters.salaryMin.toString())
      if (filters.skills.length > 0) {
        filters.skills.forEach(skill => params.append('skills', skill))
      }
      params.append('page', page.toString())
      if (sort !== 'recent') params.append('sort', sort)

      const [jobsRes, companiesRes] = await Promise.all([
        fetch(`${API_BASE_URL}/jobs/?${params}`),
        fetch(`${API_BASE_URL}/companies/`),
      ])
      const jobsData = await jobsRes.json()
      const companiesData = await companiesRes.json()
      setJobs(jobsData.jobs || [])
      setTotalJobs(jobsData.total || 0)
      setCompaniesCount(Array.isArray(companiesData) ? companiesData.length : 0)
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const allFiltersEmpty =
    !filters.query && !filters.category && !filters.remoteType &&
    !filters.experienceLevel && !filters.salaryMin

  const pageSize = 20
  const totalPages = Math.max(1, Math.ceil(totalJobs / pageSize))

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>RemoteJobHub - Find Your Perfect Remote Job</title>
        <meta name="description" content="Aggregated remote jobs from top companies" />
      </Head>

      <Header />
      <Hero totalJobs={totalJobs} totalCompanies={companiesCount} />

      <main className="container-app -mt-6 pb-16">
        <div className="mb-8 rounded-2xl bg-white p-4 shadow-card sm:p-6">
          <SearchBar onSearch={(query) => {
            setFilters({ ...EMPTY_FILTERS, query })
            setPage(1)
          }} />
        </div>

        <div className="grid grid-cols-12 gap-6">
          <aside className="col-span-12 md:col-span-3">
            <FilterSidebar
              filters={filters}
              onFilterChange={(next) => {
                setFilters(next)
                setPage(1)
              }}
            />
          </aside>

          <section className="col-span-12 md:col-span-9">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <h2 className="font-display text-lg font-bold text-gray-900">
                {totalJobs} Remote Jobs Available
                {!allFiltersEmpty && (
                  <span className="ml-2 rounded-full bg-brand-100 px-2 py-0.5 text-xs font-semibold text-brand-700">
                    filtered
                  </span>
                )}
              </h2>

              <select
                value={sort}
                onChange={(e) => { setSort(e.target.value); setPage(1) }}
                className="input-app !w-auto !py-2 text-sm"
              >
                <option value="recent">Most Recent</option>
                <option value="salary">Highest Salary</option>
                <option value="relevance">Most Relevant</option>
              </select>
            </div>

            {loading ? (
              <div className="flex flex-col items-center justify-center py-24">
                <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-brand-600" />
                <p className="mt-4 text-sm text-gray-500">Loading best remote jobs...</p>
              </div>
            ) : jobs.length === 0 ? (
              <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white py-24 text-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-100">
                  <BriefcaseIcon className="h-8 w-8 text-gray-400" />
                </div>
                <p className="mt-4 font-display text-lg font-semibold text-gray-900">
                  No jobs found
                </p>
                <p className="mt-1 max-w-sm text-sm text-gray-500">
                  Try adjusting your filters or search for a different skill.
                </p>
                <button
                  onClick={() => { setFilters(EMPTY_FILTERS); setPage(1) }}
                  className="btn-primary mt-6"
                >
                  Clear all filters
                </button>
              </div>
            ) : (
              <>
                <div className="space-y-4">
                  {jobs.map((job) => (
                    <JobCard
                      key={job.id}
                      job={job}
                      onHide={() => setJobs((current) => current.filter((i) => i.id !== job.id))}
                    />
                  ))}
                </div>

                {/* Pagination */}
                <div className="mt-8 flex items-center justify-between border-t border-gray-200 pt-6">
                  <p className="text-sm text-gray-500">
                    Page <span className="font-semibold text-gray-900">{page}</span> of {totalPages}
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setPage(Math.max(1, page - 1))}
                      disabled={page === 1}
                      className="btn-ghost !px-3 !py-2 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      <ChevronLeftIcon className="h-4 w-4" />
                      <span className="hidden sm:inline">Previous</span>
                    </button>
                    <button
                      onClick={() => setPage(Math.min(totalPages, page + 1))}
                      disabled={page >= totalPages}
                      className="btn-primary !px-3 !py-2 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      <span className="hidden sm:inline">Next</span>
                      <ChevronRightIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </>
            )}
          </section>
        </div>
      </main>
    </div>
  )
}

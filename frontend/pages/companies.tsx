import { useState, useEffect } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import Header from '@/components/Header'
import { BuildingOfficeIcon, MagnifyingGlassIcon, ArrowRightIcon } from '@heroicons/react/24/outline'
import { getCompanies } from '@/utils/api'

interface Company {
  id: string
  name: string
  logo_url?: string
  website?: string
  industry?: string
  remote_policy?: string
  total_jobs_posted: number
  total_jobs_remote: number
}

export default function Companies() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    loadCompanies()
  }, [])

  const loadCompanies = async () => {
    try {
      const data = await getCompanies()
      setCompanies(data)
    } catch (error) {
      console.error('Failed to load companies:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredCompanies = companies.filter(company =>
    company.name.toLowerCase().includes(filter.toLowerCase()) ||
    (company.industry && company.industry.toLowerCase().includes(filter.toLowerCase()))
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Companies - RemoteJobHub</title>
        <meta name="description" content="Browse top remote-first companies" />
      </Head>

      <Header />

      <main className="container-app pb-16 pt-10">
        <div className="mb-8">
          <h1 className="font-display text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">
            Remote-First <span className="text-gradient">Companies</span>
          </h1>
          <p className="mt-2 max-w-2xl text-gray-600">
            Browse companies that are committed to remote work. View their hiring history and open opportunities.
          </p>
        </div>

        {/* Search */}
        <div className="mb-8 max-w-md">
          <div className="relative">
            <MagnifyingGlassIcon className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search companies by name or industry..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="input-app !pl-11"
            />
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-24">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-brand-600" />
            <p className="mt-4 text-sm text-gray-500">Loading companies...</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {filteredCompanies.map((company) => (
                <Link
                  key={company.id}
                  href={`/companies/${encodeURIComponent(company.name)}`}
                  className="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white p-6 shadow-card transition-all hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-lift"
                >
                  <div className="flex items-start space-x-4">
                    {company.logo_url ? (
                      <img
                        src={company.logo_url}
                        alt={`${company.name} logo`}
                        className="h-14 w-14 shrink-0 rounded-xl object-contain"
                      />
                    ) : (
                      <div className="bg-gradient-brand flex h-14 w-14 shrink-0 items-center justify-center rounded-xl text-xl font-bold text-white">
                        {company.name.charAt(0)}
                      </div>
                    )}

                    <div className="min-w-0 flex-1">
                      <h3 className="flex items-center gap-1.5 font-display text-lg font-bold text-gray-900 transition-colors group-hover:text-brand-600">
                        {company.name}
                        <ArrowRightIcon className="h-4 w-4 -translate-x-1 text-brand-500 opacity-0 transition-all group-hover:translate-x-0 group-hover:opacity-100" />
                      </h3>
                      {company.industry && (
                        <p className="text-sm text-gray-500">{company.industry}</p>
                      )}

                      <div className="mt-3 flex flex-wrap gap-2">
                        {company.remote_policy && (
                          <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                            {company.remote_policy === 'full_remote' ? 'Fully Remote' : company.remote_policy}
                          </span>
                        )}
                        <span className="rounded-full bg-brand-50 px-2.5 py-1 text-xs font-semibold text-brand-700">
                          {company.total_jobs_remote} remote jobs
                        </span>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {!loading && filteredCompanies.length === 0 && (
              <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white py-24 text-center">
                <BuildingOfficeIcon className="h-12 w-12 text-gray-300" />
                <p className="mt-4 font-semibold text-gray-900">No companies found</p>
                <p className="mt-1 text-sm text-gray-500">Try a different search.</p>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}

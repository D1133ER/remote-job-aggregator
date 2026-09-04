import { formatDistanceToNow } from 'date-fns'
import Link from 'next/link'
import { BriefcaseIcon, MapPinIcon, ClockIcon, BookmarkIcon, CheckBadgeIcon, ArrowUpRightIcon, ArrowTopRightOnSquareIcon } from '@heroicons/react/24/outline'
import { hideJob as hideJobApi } from '@/utils/api'

interface JobCardProps {
  onHide?: () => void
  onApply?: (applyUrl: string) => void
  job: {
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
    source_url?: string
    apply_url?: string
  }
}

export default function JobCard({ job, onHide, onApply }: JobCardProps) {
  const hideJob = async () => {
    if (!onHide) return

    const token = localStorage.getItem('token')
    if (!token) {
      window.location.href = '/login'
      return
    }

    try {
      await hideJobApi(job.id)
      onHide()
    } catch (err: any) {
      // 409 means already hidden — still remove from the list
      if (err.response?.status === 409) onHide()
    }
  }

  const openApplication = () => {
    // Prefer a dedicated apply URL; fall back to the source posting.
    const target = job.apply_url || job.source_url
    if (!target) return

    if (onApply) {
      onApply(target)
    } else {
      window.open(target, '_blank', 'noopener,noreferrer')
    }
  }

  return (
    <article className="group rounded-2xl border border-gray-100 bg-white p-6 shadow-card transition-all hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-lift">
      <div className="flex items-start space-x-4">
        {/* Logo / fallback */}
        {job.company_logo_url ? (
          <img
            src={job.company_logo_url}
            alt={`${job.company_name} logo`}
            className="h-12 w-12 shrink-0 rounded-xl object-contain"
          />
        ) : (
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-brand text-lg font-bold text-white">
            {job.company_name.charAt(0).toUpperCase()}
          </div>
        )}

        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-3">
            <div>
              <Link href={`/jobs/${job.id}`}>
                <h3 className="font-display text-lg font-bold text-gray-900 transition-colors group-hover:text-brand-600">
                  {job.title}
                </h3>
              </Link>
              <Link href={`/jobs/${job.id}`}>
                <p className="mt-0.5 text-sm font-medium text-gray-500 transition-colors hover:text-brand-600">{job.company_name}</p>
              </Link>
            </div>

            <div className="flex shrink-0 flex-col items-end gap-1">
              {job.salary_display && (
                <span className="rounded-lg bg-emerald-50 px-2.5 py-1 text-sm font-semibold text-emerald-700">
                  {job.salary_display}
                </span>
              )}
              <span className="inline-flex items-center gap-1 rounded-full bg-brand-50 px-2 py-0.5 text-xs font-semibold text-brand-700">
                <CheckBadgeIcon className="h-3.5 w-3.5" />
                Verified
              </span>
            </div>
          </div>

          {job.summary && (
            <p className="mt-2 line-clamp-2 text-sm text-gray-600">{job.summary}</p>
          )}

          <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-gray-500">
            <div className="flex items-center">
              <MapPinIcon className="mr-1.5 h-4 w-4 text-gray-400" />
              <span className="font-medium text-gray-700">{job.location}</span>
            </div>

            <div className="flex items-center">
              <BriefcaseIcon className="mr-1.5 h-4 w-4 text-gray-400" />
              <span className="capitalize">{job.remote_type.replace('_', ' ')}</span>
            </div>

            <div className="flex items-center">
              <ClockIcon className="mr-1.5 h-4 w-4 text-gray-400" />
              <span>{formatDistanceToNow(new Date(job.posted_at), { addSuffix: true })}</span>
            </div>
          </div>

          {job.skills && job.skills.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {job.skills.slice(0, 5).map((skill) => (
                <span
                  key={skill}
                  className="rounded-md bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-600 transition-colors hover:bg-brand-50 hover:text-brand-700"
                >
                  {skill}
                </span>
              ))}
              {job.skills.length > 5 && (
                <span className="text-xs text-gray-400">
                  +{job.skills.length - 5} more
                </span>
              )}
            </div>
          )}

          {(job.apply_url || job.source_url || onHide) && (
            <div className="mt-4 flex items-center justify-between gap-3 border-t border-gray-100 pt-3">
              <div className="flex items-center gap-2">
                {(job.apply_url || job.source_url) && (
                  <button
                    type="button"
                    onClick={openApplication}
                    className="btn-primary inline-flex items-center gap-1.5 !px-3.5 !py-2 text-sm font-semibold"
                  >
                    <ArrowUpRightIcon className="h-4 w-4" />
                    Apply
                    <ArrowTopRightOnSquareIcon className="h-3.5 w-3.5 opacity-70" />
                  </button>
                )}
                {onHide && (
                  <button
                    type="button"
                    onClick={hideJob}
                    className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-2 text-xs font-medium text-gray-400 transition-colors hover:bg-red-50 hover:text-red-600"
                  >
                    <BookmarkIcon className="h-4 w-4" />
                    Hide
                  </button>
                )}
              </div>
              <span className="rounded-md bg-gray-50 px-2.5 py-1 text-xs font-semibold uppercase tracking-wide text-gray-500">
                {job.category}
              </span>
            </div>
          )}
        </div>
      </div>
    </article>
  )
}

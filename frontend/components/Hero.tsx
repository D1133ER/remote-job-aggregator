import { SparklesIcon, ShieldCheckIcon, ChartBarIcon, GlobeAltIcon } from '@heroicons/react/24/outline'

interface HeroProps {
  totalJobs: number
  totalCompanies: number
}

export default function Hero({ totalJobs, totalCompanies }: HeroProps) {
  const stats = [
    { label: 'Remote Jobs', value: totalJobs || '0', icon: SparklesIcon },
    { label: 'Companies', value: totalCompanies || '0', icon: GlobeAltIcon },
    { label: '100% Remote', value: '100%', icon: ShieldCheckIcon },
  ]

  return (
    <section className="relative overflow-hidden bg-gradient-brand py-16 sm:py-20">
      {/* Decorative blobs */}
      <div className="pointer-events-none absolute -top-24 -right-24 h-72 w-72 rounded-full bg-white/10 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-32 -left-24 h-80 w-80 rounded-full bg-cyan-300/20 blur-3xl" />
      <div className="pointer-events-none absolute top-10 left-1/3 h-40 w-40 rounded-full bg-indigo-300/20 blur-2xl animate-float" />

      <div className="relative container-app">
        <div className="mx-auto max-w-3xl text-center animate-fade-in-up">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-white/15 px-4 py-1.5 text-xs font-semibold text-white ring-1 ring-white/20">
            <SparklesIcon className="h-3.5 w-3.5" />
            The smartest remote job aggregator
          </span>

          <h1 className="font-display mt-6 text-4xl font-extrabold leading-tight tracking-tight text-white sm:text-5xl lg:text-6xl">
            Find your perfect{' '}
            <span className="bg-gradient-to-r from-cyan-200 to-white bg-clip-text text-transparent">
              remote job
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg text-indigo-100">
            Aggregated, deduplicated, and AI-enriched opportunities from the world's best
            remote-first companies. No hybrid. No on-site. Just truly remote roles.
          </p>
        </div>

        {/* Stats */}
        <div className="mx-auto mt-12 grid max-w-2xl grid-cols-3 gap-4 sm:gap-6">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="rounded-2xl bg-white/10 px-4 py-5 text-center ring-1 ring-white/15 backdrop-blur-sm"
            >
              <stat.icon className="mx-auto h-6 w-6 text-cyan-200" />
              <div className="mt-2 font-display text-2xl font-bold text-white sm:text-3xl">
                {stat.value}
              </div>
              <div className="mt-1 text-xs font-medium text-indigo-100">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Wave */}
      <svg
        className="absolute bottom-0 left-0 w-full text-gray-50"
        viewBox="0 0 1440 48"
        fill="currentColor"
        preserveAspectRatio="none"
      >
        <path d="M0,48 C240,16 480,0 720,0 C960,0 1200,16 1440,48 L1440,48 L0,48 Z" />
      </svg>
    </section>
  )
}

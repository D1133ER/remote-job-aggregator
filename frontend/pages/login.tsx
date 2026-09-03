import { useState } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { BriefcaseIcon, EnvelopeIcon, LockClosedIcon, SparklesIcon } from '@heroicons/react/24/outline'
import { loginUser } from '@/utils/api'

export default function Login() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const data = await loginUser(email, password)
      localStorage.setItem('token', data.access_token)
      router.push('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      <Head>
        <title>Login - RemoteJobHub</title>
        <meta name="description" content="Login to RemoteJobHub" />
      </Head>

      {/* Left branding panel */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-brand flex-col justify-between overflow-hidden p-12">
        <div className="pointer-events-none absolute -top-20 -right-20 h-72 w-72 rounded-full bg-white/10 blur-3xl" />
        <div className="pointer-events-none absolute bottom-0 -left-24 h-80 w-80 rounded-full bg-cyan-300/20 blur-3xl" />

        <div className="relative flex items-center gap-3">
          <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-white/15 text-white ring-1 ring-white/20">
            <BriefcaseIcon className="h-6 w-6" />
          </span>
          <span className="font-display text-2xl font-extrabold tracking-tight text-white">
            Remote<span className="text-cyan-200">JobHub</span>
          </span>
        </div>

        <div className="relative">
          <h2 className="font-display text-4xl font-extrabold leading-tight text-white">
            Welcome back to your
            <span className="block bg-gradient-to-r from-cyan-200 to-white bg-clip-text text-transparent">
              remote career hub
            </span>
          </h2>
          <p className="mt-4 max-w-md text-lg text-indigo-100">
            Sign in to manage your saved jobs, set up alerts, and discover truly remote opportunities.
          </p>

          <div className="mt-8 flex items-center gap-2 text-sm text-indigo-100">
            <SparklesIcon className="h-5 w-5 text-cyan-200" />
            Salary insights · AI summaries · Instant alerts
          </div>
        </div>

        <p className="relative text-sm text-indigo-200">© {new Date().getFullYear()} RemoteJobHub</p>
      </div>

      {/* Form panel */}
      <div className="flex flex-1 items-center justify-center bg-gray-50 px-6 py-12 sm:px-12">
        <div className="w-full max-w-md animate-fade-in-up">
          <div className="mb-8 lg:hidden">
            <span className="bg-gradient-brand inline-flex h-11 w-11 items-center justify-center rounded-2xl text-white shadow-lift">
              <BriefcaseIcon className="h-6 w-6" />
            </span>
          </div>

          <h1 className="font-display text-3xl font-extrabold tracking-tight text-gray-900">
            Sign in to your account
          </h1>
          <p className="mt-2 text-gray-500">
            Don't have an account?{' '}
            <Link href="/register" className="font-semibold text-brand-600 hover:text-brand-700">
              Create one free
            </Link>
          </p>

          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-gray-700">
                Email or Username
              </label>
              <div className="relative">
                <EnvelopeIcon className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  id="email"
                  type="text"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="input-app !pl-11"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="relative">
                <LockClosedIcon className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="input-app !pl-11"
                />
              </div>
            </div>

            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                {error}
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary w-full !py-3">
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <div className="mt-8 rounded-2xl border border-brand-100 bg-brand-50 p-4 text-sm text-brand-700">
            <span className="font-semibold">Demo account:</span> demo@remotejobhub.com / Demo1234
          </div>
        </div>
      </div>
    </div>
  )
}

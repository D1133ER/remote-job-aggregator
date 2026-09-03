import { useState } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { BriefcaseIcon, UserIcon, EnvelopeIcon, LockClosedIcon, ChatBubbleOvalLeftIcon, CheckBadgeIcon } from '@heroicons/react/24/outline'
import { API_BASE_URL } from '@/utils/api'

export default function Register() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    full_name: '',
    password: '',
    confirmPassword: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          username: formData.username,
          full_name: formData.full_name,
          password: formData.password
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Registration failed')
      }

      router.push('/login')
    } catch (err: any) {
      setError(err.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      <Head>
        <title>Register - RemoteJobHub</title>
        <meta name="description" content="Create your RemoteJobHub account" />
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
            Your next remote role
            <span className="block bg-gradient-to-r from-cyan-200 to-white bg-clip-text text-transparent">
              is one search away
            </span>
          </h2>
          <p className="mt-4 max-w-md text-lg text-indigo-100">
            Join thousands of professionals finding verified, 100% remote opportunities from the world's best companies.
          </p>

          <ul className="mt-8 space-y-3 text-indigo-100">
            {[
              'Deduplicated, truly remote jobs only',
              'AI-powered salary & skills insights',
              'Personalized job alerts straight to your inbox',
            ].map((item) => (
              <li key={item} className="flex items-center gap-2.5 text-sm">
                <CheckBadgeIcon className="h-5 w-5 text-cyan-200" />
                {item}
              </li>
            ))}
          </ul>
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
            Create your account
          </h1>
          <p className="mt-2 text-gray-500">
            Already have an account?{' '}
            <Link href="/login" className="font-semibold text-brand-600 hover:text-brand-700">
              Sign in
            </Link>
          </p>

          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-gray-700">
                Email
              </label>
              <div className="relative">
                <EnvelopeIcon className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input id="email" name="email" type="email" autoComplete="email" required
                  value={formData.email} onChange={handleChange} placeholder="you@example.com"
                  className="input-app !pl-11" />
              </div>
            </div>

            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <div>
                <label htmlFor="username" className="mb-1.5 block text-sm font-medium text-gray-700">
                  Username
                </label>
                <div className="relative">
                  <UserIcon className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                  <input id="username" name="username" type="text" required
                    value={formData.username} onChange={handleChange} placeholder="johndoe"
                    className="input-app !pl-11" />
                </div>
              </div>

              <div>
                <label htmlFor="full_name" className="mb-1.5 block text-sm font-medium text-gray-700">
                  Full Name
                </label>
                <div className="relative">
                  <ChatBubbleOvalLeftIcon className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                  <input id="full_name" name="full_name" type="text"
                    value={formData.full_name} onChange={handleChange} placeholder="John Doe"
                    className="input-app !pl-11" />
                </div>
              </div>
            </div>

            <div>
              <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="relative">
                <LockClosedIcon className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input id="password" name="password" type="password" autoComplete="new-password" required
                  value={formData.password} onChange={handleChange} placeholder="••••••••"
                  className="input-app !pl-11" />
              </div>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="mb-1.5 block text-sm font-medium text-gray-700">
                Confirm Password
              </label>
              <div className="relative">
                <LockClosedIcon className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input id="confirmPassword" name="confirmPassword" type="password" autoComplete="new-password" required
                  value={formData.confirmPassword} onChange={handleChange} placeholder="••••••••"
                  className="input-app !pl-11" />
              </div>
            </div>

            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                {error}
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary w-full !py-3">
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

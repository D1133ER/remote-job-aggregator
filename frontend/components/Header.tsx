import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { MagnifyingGlassIcon, ArrowRightOnRectangleIcon, UserCircleIcon, BriefcaseIcon } from '@heroicons/react/24/outline'

const NAV_LINKS = [
  { href: '/', label: 'Jobs' },
  { href: '/companies', label: 'Companies' },
  { href: '/alerts', label: 'Job Alerts' },
]

export default function Header() {
  const router = useRouter()
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    setToken(localStorage.getItem('token'))
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    setToken(null)
    router.push('/')
  }

  return (
    <header className="sticky top-0 z-50 border-b border-gray-100 bg-white/80 backdrop-blur-xl">
      <div className="container-app flex h-16 items-center justify-between">
        {/* Logo */}
        <Link href="/" className="group flex items-center gap-2.5">
          <span className="bg-gradient-brand inline-flex h-9 w-9 items-center justify-center rounded-xl text-white shadow-lift transition-transform group-hover:scale-105">
            <BriefcaseIcon className="h-5 w-5" />
          </span>
          <span className="font-display text-xl font-extrabold tracking-tight text-gray-900">
            Remote<span className="text-gradient">JobHub</span>
          </span>
        </Link>

        {/* Nav */}
        <nav className="hidden items-center gap-1 md:flex">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                router.pathname === link.href
                  ? 'bg-brand-50 text-brand-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Auth actions */}
        <div className="flex items-center gap-2">
          {token ? (
            <div className="flex items-center gap-2">
              <Link href="/saved-jobs" className="btn-ghost !px-3 !py-2">
                <MagnifyingGlassIcon className="h-4 w-4" />
                <span className="hidden sm:inline">Saved</span>
              </Link>
              <button onClick={handleLogout} className="btn-ghost !px-3 !py-2 text-red-600 hover:border-red-300 hover:text-red-700">
                <ArrowRightOnRectangleIcon className="h-4 w-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link href="/login" className="btn-ghost !px-3 !py-2">
                <UserCircleIcon className="h-4 w-4" />
                <span className="hidden sm:inline">Log in</span>
              </Link>
              <Link href="/register" className="btn-primary !px-4 !py-2">
                Sign up
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Mobile nav */}
      <nav className="container-app flex gap-1 border-t border-gray-100 py-2 md:hidden">
        {NAV_LINKS.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
              router.pathname === link.href
                ? 'bg-brand-50 text-brand-700'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </header>
  )
}

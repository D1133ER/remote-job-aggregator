import { useState } from 'react'
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'

interface SearchBarProps {
  onSearch: (query: string) => void
}

const SUGGESTIONS = ['React', 'DevOps', 'Customer Support', 'Python', 'Design']

export default function SearchBar({ onSearch }: SearchBarProps) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSearch(query)
  }

  return (
    <div className="mx-auto max-w-3xl">
      <form onSubmit={handleSubmit}>
        <div className="group relative">
          <div className="absolute inset-y-0 left-0 flex items-center pl-4">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search remote jobs by title, skill, or company..."
            className="block w-full rounded-2xl border border-gray-200 bg-white py-4 pl-12 pr-40 text-gray-900 shadow-card transition-all placeholder-gray-400 focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/10 focus:shadow-lift"
          />
          <div className="absolute inset-y-0 right-0 flex items-center pr-3">
            <button
              type="submit"
              className="btn-primary !rounded-xl"
            >
              Search
            </button>
          </div>
        </div>
      </form>

      <div className="mt-3 flex flex-wrap items-center justify-center gap-2 text-sm">
        <span className="text-gray-400">Popular:</span>
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => onSearch(s)}
            className="rounded-full border border-gray-200 bg-white px-3 py-1 text-gray-600 transition-colors hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  )
}

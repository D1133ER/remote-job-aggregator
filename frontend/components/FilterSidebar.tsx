import { AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline'

interface FilterSidebarProps {
  filters: {
    query: string
    category: string
    remoteType: string
    experienceLevel: string
    salaryMin: number | null
    skills: string[]
  }
  onFilterChange: (filters: any) => void
}

interface Option {
  value: string
  label: string
}

function FilterGroup({
  title,
  options,
  selected,
  onChange,
}: {
  title: string
  options: Option[]
  selected: string
  onChange: (value: string) => void
}) {
  return (
    <div>
      <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
        {title}
      </h4>
      <div className="space-y-1.5">
        {options.map((option) => {
          const active = selected === option.value
          return (
            <button
              key={option.value}
              onClick={() => onChange(option.value)}
              className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                active
                  ? 'bg-brand-50 text-brand-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <span>{option.label}</span>
              {active && (
                <span className="h-1.5 w-1.5 rounded-full bg-brand-600" />
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default function FilterSidebar({ filters, onFilterChange }: FilterSidebarProps) {
  const categories = [
    'Software Development',
    'Data Science',
    'Design',
    'Marketing',
    'Sales',
    'Customer Support',
    'Product Management',
    'DevOps',
  ].map((c) => ({ value: c, label: c }))

  const remoteTypes: Option[] = [
    { value: 'full_remote', label: 'Full Remote' },
    { value: 'hybrid', label: 'Hybrid' },
    { value: 'onsite', label: 'On-site' },
  ]

  const experienceLevels: Option[] = [
    { value: 'junior', label: 'Junior' },
    { value: 'mid', label: 'Mid-Level' },
    { value: 'senior', label: 'Senior' },
    { value: 'lead', label: 'Lead' },
  ]

  const salaryRanges: Option[] = [
    { value: '50000', label: '$50k+' },
    { value: '75000', label: '$75k+' },
    { value: '100000', label: '$100k+' },
    { value: '150000', label: '$150k+' },
    { value: '200000', label: '$200k+' },
  ]

  const hasActiveFilters =
    filters.category ||
    filters.remoteType ||
    filters.experienceLevel ||
    filters.salaryMin

  return (
    <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-card">
      <div className="mb-5 flex items-center justify-between">
        <h3 className="flex items-center gap-2 font-display text-base font-bold text-gray-900">
          <AdjustmentsHorizontalIcon className="h-5 w-5 text-brand-600" />
          Filters
        </h3>
        {hasActiveFilters && (
          <button
            onClick={() =>
              onFilterChange({
                ...filters,
                category: '',
                remoteType: '',
                experienceLevel: '',
                salaryMin: null,
                skills: [],
              })
            }
            className="text-xs font-semibold text-brand-600 hover:text-brand-700"
          >
            Reset all
          </button>
        )}
      </div>

      <div className="space-y-6">
        <FilterGroup
          title="Category"
          options={categories}
          selected={filters.category}
          onChange={(value) => onFilterChange({ ...filters, category: value === filters.category ? '' : value })}
        />

        <FilterGroup
          title="Remote Type"
          options={remoteTypes}
          selected={filters.remoteType}
          onChange={(value) => onFilterChange({ ...filters, remoteType: value === filters.remoteType ? '' : value })}
        />

        <FilterGroup
          title="Experience Level"
          options={experienceLevels}
          selected={filters.experienceLevel}
          onChange={(value) => onFilterChange({ ...filters, experienceLevel: value === filters.experienceLevel ? '' : value })}
        />

        <FilterGroup
          title="Minimum Salary"
          options={salaryRanges}
          selected={filters.salaryMin ? filters.salaryMin.toString() : ''}
          onChange={(value) => onFilterChange({ ...filters, salaryMin: Number(value) })}
        />
      </div>
    </div>
  )
}

type MetricCardProps = {
  title: string
  value: string
  icon: string
  highlight?: boolean
}

export function MetricCard({
  title,
  value,
  icon,
  highlight = false,
}: MetricCardProps) {
  return (
    <div
      className={`rounded-2xl border p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md ${
        highlight
          ? 'border-blue-200 bg-blue-900'
          : 'border-slate-200 bg-white'
      }`}
    >
      <div className="flex items-start justify-between">

        <div
          className={`flex h-10 w-10 items-center justify-center rounded-xl text-lg ${
            highlight
              ? 'bg-white/10'
              : 'bg-slate-100'
          }`}
        >
          {icon}
        </div>

        {highlight && (
          <span className="rounded-full bg-white/10 px-2.5 py-1 text-xs font-medium text-blue-100">
            Total
          </span>
        )}

      </div>

      <div className="mt-5">

        <p
          className={`text-sm font-medium ${
            highlight
              ? 'text-blue-100'
              : 'text-slate-500'
          }`}
        >
          {title}
        </p>

        <p
          className={`mt-1 text-2xl font-bold tracking-tight ${
            highlight
              ? 'text-white'
              : 'text-slate-900'
          }`}
        >
          {value}
        </p>

      </div>

    </div>
  )
}
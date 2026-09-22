export function AppHeader() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            🏥 Faturamento Médico
          </h1>

          <p className="mt-1 text-sm text-slate-500">
            Gestão de faturamento, notas fiscais e impostos
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2">
          <span className="text-sm font-medium text-slate-600">
            Sistema
          </span>

          <span className="ml-2 text-sm font-semibold text-emerald-600">
            ● Online
          </span>
        </div>
      </div>
    </header>
  )
}
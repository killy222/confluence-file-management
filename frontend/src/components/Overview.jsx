export default function Overview({ runs = [], loading }) {
  const total = runs.length;
  const success = runs.filter((r) => r.status === 'success').length;
  const successRate = total > 0 ? ((success / total) * 100).toFixed(1) : '0';
  const running = runs.filter((r) => r.status === 'running').length;

  return (
    <section className="mb-8" aria-label="Overview">
      <h2 className="text-2xl font-semibold text-white mb-1">Overview</h2>
      <p className="text-slate-400 mb-6">Welcome back. Check run status and exported files.</p>
      {loading ? (
        <div className="text-slate-400">Loading…</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-xl bg-slate-800 border border-slate-700 p-5">
            <p className="text-slate-400 text-sm uppercase tracking-wide mb-1">Total runs</p>
            <p className="text-2xl font-semibold text-white">{total}</p>
            <p className="text-slate-500 text-sm mt-1">recorded in history</p>
          </div>
          <div className="rounded-xl bg-slate-800 border border-slate-700 p-5">
            <p className="text-slate-400 text-sm uppercase tracking-wide mb-1">Success rate</p>
            <p className="text-2xl font-semibold text-white">{successRate}%</p>
            <div className="mt-2 h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-violet-500 rounded-full transition-all"
                style={{ width: `${successRate}%` }}
              />
            </div>
          </div>
          <div className="rounded-xl bg-slate-800 border border-slate-700 p-5">
            <p className="text-slate-400 text-sm uppercase tracking-wide mb-1">Running now</p>
            <p className="text-2xl font-semibold text-white">{running}</p>
            <p className="text-slate-500 text-sm mt-1">active jobs</p>
          </div>
        </div>
      )}
    </section>
  );
}

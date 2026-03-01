function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  const now = new Date();
  const sec = Math.floor((now - d) / 1000);
  if (sec < 60) return 'Just now';
  if (sec < 3600) return `${Math.floor(sec / 60)}m ago`;
  if (sec < 86400) return `${Math.floor(sec / 3600)}h ago`;
  return d.toLocaleDateString();
}

export default function FileList({ files = [], loading }) {
  return (
    <section className="flex-1 min-w-0 lg:max-w-md" id="files" aria-label="Exported files">
      <h2 className="text-xl font-semibold text-white mb-4">Cloud files</h2>
      {loading ? (
        <div className="text-slate-400">Loading files…</div>
      ) : files.length === 0 ? (
        <p className="text-slate-500">No exported files yet. Run Confluence export first.</p>
      ) : (
        <ul className="space-y-2">
          {files.map((f) => (
            <li
              key={f.id}
              className="flex items-center gap-3 rounded-lg bg-slate-800 border border-slate-700 px-4 py-3"
            >
              <span className="text-slate-500" aria-hidden="true">📄</span>
              <div className="flex-1 min-w-0">
                <p className="text-white truncate" title={f.title || f.path}>
                  {f.title || f.path || 'Untitled'}
                </p>
                <p className="text-slate-500 text-sm">{formatDate(f.created_at)}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

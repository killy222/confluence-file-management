import { useState } from 'react';
import { getRun } from '../api';

function StatusDot({ status }) {
  const colors = {
    running: 'bg-emerald-500',
    success: 'bg-emerald-500',
    failure: 'bg-red-500',
  };
  return (
    <span
      className={`inline-block w-2 h-2 rounded-full ${colors[status] || 'bg-slate-500'}`}
      aria-hidden="true"
    />
  );
}

function formatAgo(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  const now = new Date();
  const sec = Math.floor((now - d) / 1000);
  if (sec < 60) return 'Just now';
  if (sec < 3600) return `${Math.floor(sec / 60)}m ago`;
  if (sec < 86400) return `${Math.floor(sec / 3600)}h ago`;
  return `${Math.floor(sec / 86400)}d ago`;
}

export default function RunHistory({ runs = [], loading, onRefresh }) {
  const [detail, setDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  async function showDetails(id) {
    setLoadingDetail(true);
    setDetail(null);
    try {
      const run = await getRun(id);
      setDetail(run);
    } catch (e) {
      setDetail({ error: e.message });
    } finally {
      setLoadingDetail(false);
    }
  }

  function closeDetail() {
    setDetail(null);
  }

  return (
    <section className="flex-1 min-w-0" id="dashboard" aria-label="Run history">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white">Active pipelines</h2>
        <button
          type="button"
          onClick={onRefresh}
          className="text-sm text-violet-400 hover:text-violet-300 transition"
        >
          View all →
        </button>
      </div>
      {loading ? (
        <div className="text-slate-400">Loading runs…</div>
      ) : runs.length === 0 ? (
        <p className="text-slate-500">No runs yet. Trigger an export or push above.</p>
      ) : (
        <ul className="space-y-3">
          {runs.slice(0, 8).map((run) => (
            <li
              key={run.id}
              className="rounded-xl bg-slate-800 border border-slate-700 p-4 flex flex-wrap items-center gap-3"
            >
              <StatusDot status={run.status} />
              <div className="flex-1 min-w-0">
                <p className="font-medium text-white capitalize">
                  {run.script.replace(/_/g, ' ')}
                </p>
                <p className="text-slate-500 text-sm">
                  {formatAgo(run.started_at)} · {run.status}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => showDetails(run.id)}
                  className="px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-sm transition min-h-[44px] min-w-[44px]"
                >
                  Details
                </button>
                <button
                  type="button"
                  onClick={() => showDetails(run.id)}
                  className="px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm transition min-h-[44px]"
                >
                  Logs
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {loadingDetail && <p className="mt-2 text-slate-400 text-sm">Loading details…</p>}
      {detail && !detail.error && (
        <div
          className="mt-4 p-4 rounded-xl bg-slate-800 border border-slate-700"
          role="dialog"
          aria-label="Run details"
        >
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-medium text-white">Run details</h3>
            <button
              type="button"
              onClick={closeDetail}
              className="text-slate-400 hover:text-white"
              aria-label="Close"
            >
              ×
            </button>
          </div>
          <pre className="text-sm text-slate-300 whitespace-pre-wrap overflow-auto max-h-48">
            {detail.log_output || detail.error_message || 'No log'}
          </pre>
        </div>
      )}
      {detail && detail.error && (
        <div className="mt-4 p-4 rounded-xl bg-red-900/30 border border-red-700 text-red-200 text-sm">
          {detail.error}
          <button type="button" onClick={closeDetail} className="ml-2 underline">Dismiss</button>
        </div>
      )}
    </section>
  );
}

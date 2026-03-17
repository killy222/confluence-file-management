import { useEffect, useMemo, useState } from 'react';
import { triggerRuns } from '../api';

const buttonClass =
  'px-4 py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-medium transition min-h-[44px]';

export default function TriggerRuns({
  onTriggered,
  runs = [],
  spaces = [],
  notebooks = [],
}) {
  const [loading, setLoading] = useState(null);
  const [message, setMessage] = useState(null);
  const [selectedSpaceId, setSelectedSpaceId] = useState('');
  const [selectedNotebookId, setSelectedNotebookId] = useState('');

  const lastSpaceKeyFromRuns = useMemo(() => {
    const exportRun = runs.find((r) => r.script === 'confluence_export' && r.space_key);
    return exportRun?.space_key || null;
  }, [runs]);

  const lastNotebookNameFromRuns = useMemo(() => {
    const pushRun = runs.find(
      (r) => r.script === 'notebooklm_push' && r.notebook_name,
    );
    return pushRun?.notebook_name || null;
  }, [runs]);

  useEffect(() => {
    if (!spaces.length) {
      setSelectedSpaceId('');
      return;
    }
    if (selectedSpaceId) return;
    if (lastSpaceKeyFromRuns) {
      const match = spaces.find((s) => s.key === lastSpaceKeyFromRuns);
      if (match) {
        setSelectedSpaceId(match.id);
        return;
      }
    }
    // default to first space if nothing else selected
    setSelectedSpaceId(spaces[0]?.id || '');
  }, [spaces, selectedSpaceId, lastSpaceKeyFromRuns]);

  useEffect(() => {
    if (!notebooks.length) {
      setSelectedNotebookId('');
      return;
    }
    if (selectedNotebookId) return;
    if (lastNotebookNameFromRuns) {
      const match = notebooks.find((n) => n.name === lastNotebookNameFromRuns);
      if (match) {
        setSelectedNotebookId(match.id);
        return;
      }
    }
    setSelectedNotebookId(notebooks[0]?.id || '');
  }, [notebooks, selectedNotebookId, lastNotebookNameFromRuns]);

  async function handleTrigger(scripts) {
    setMessage(null);
    setLoading(scripts.join('+'));
    try {
      const payload = { scripts };
      if (selectedSpaceId && scripts.includes('confluence_export')) {
        payload.space_id = selectedSpaceId;
      }
      if (selectedNotebookId && scripts.includes('notebooklm_push')) {
        payload.notebook_id = selectedNotebookId;
      }
      const res = await triggerRuns(payload);
      setMessage(`Started: ${res.run_ids?.length || 0} run(s). ${res.message || ''}`);
      onTriggered?.();
    } catch (e) {
      setMessage(`Error: ${e.message || e.status || 'Request failed'}`);
    } finally {
      setLoading(null);
    }
  }

  const isLoading = loading !== null;
  const disableExportButtons = !selectedSpaceId && !isLoading;
  const disablePushButtons = !selectedNotebookId && !isLoading;

  return (
    <section className="mb-6" aria-label="Trigger runs">
      <div className="flex flex-wrap items-center gap-4 mb-3">
        <div className="flex flex-col">
          <label htmlFor="space-select" className="text-xs text-slate-400 mb-1">
            Confluence space
          </label>
          <select
            id="space-select"
            value={selectedSpaceId}
            onChange={(e) => setSelectedSpaceId(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100 min-w-[200px]"
          >
            {spaces.length === 0 ? (
              <option value="">No spaces configured</option>
            ) : (
              spaces.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label} ({s.key})
                </option>
              ))
            )}
          </select>
        </div>
        <div className="flex flex-col">
          <label htmlFor="notebook-select" className="text-xs text-slate-400 mb-1">
            NotebookLM notebook
          </label>
          <select
            id="notebook-select"
            value={selectedNotebookId}
            onChange={(e) => setSelectedNotebookId(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100 min-w-[220px]"
          >
            {notebooks.length === 0 ? (
              <option value="">No notebooks configured</option>
            ) : (
              notebooks.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.name}
                </option>
              ))
            )}
          </select>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-4">
        <button
          type="button"
          onClick={() => handleTrigger(['confluence_export'])}
          disabled={isLoading || disableExportButtons}
          className={buttonClass}
        >
          {loading === 'confluence_export' ? 'Starting…' : 'Run Confluence Export'}
        </button>
        <button
          type="button"
          onClick={() => handleTrigger(['notebooklm_push'])}
          disabled={isLoading || disablePushButtons}
          className={buttonClass}
        >
          {loading === 'notebooklm_push' ? 'Starting…' : 'Run push files to notebook'}
        </button>
        <button
          type="button"
          onClick={() => handleTrigger(['confluence_export', 'notebooklm_push'])}
          disabled={isLoading || disableExportButtons || disablePushButtons}
          className={buttonClass}
        >
          {loading === 'confluence_export+notebooklm_push' ? 'Starting…' : 'Run all'}
        </button>
      </div>
      {message && (
        <p className={`mt-2 text-sm ${message.startsWith('Error') ? 'text-red-400' : 'text-emerald-400'}`}>
          {message}
        </p>
      )}
    </section>
  );
}

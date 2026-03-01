import { useState } from 'react';
import { triggerRuns } from '../api';

const buttonClass =
  'px-4 py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-medium transition min-h-[44px]';

export default function TriggerRuns({ onTriggered }) {
  const [loading, setLoading] = useState(null);
  const [message, setMessage] = useState(null);

  async function handleTrigger(scripts) {
    setMessage(null);
    setLoading(scripts.join('+'));
    try {
      const res = await triggerRuns(scripts);
      setMessage(`Started: ${res.run_ids?.length || 0} run(s). ${res.message || ''}`);
      onTriggered?.();
    } catch (e) {
      setMessage(`Error: ${e.message || e.status || 'Request failed'}`);
    } finally {
      setLoading(null);
    }
  }

  const isLoading = loading !== null;

  return (
    <section className="mb-6" aria-label="Trigger runs">
      <div className="flex flex-wrap items-center gap-4">
        <button
          type="button"
          onClick={() => handleTrigger(['confluence_export'])}
          disabled={isLoading}
          className={buttonClass}
        >
          {loading === 'confluence_export' ? 'Starting…' : 'Run Confluence Export'}
        </button>
        <button
          type="button"
          onClick={() => handleTrigger(['notebooklm_push'])}
          disabled={isLoading}
          className={buttonClass}
        >
          {loading === 'notebooklm_push' ? 'Starting…' : 'Run push files to notebook'}
        </button>
        <button
          type="button"
          onClick={() => handleTrigger(['confluence_export', 'notebooklm_push'])}
          disabled={isLoading}
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

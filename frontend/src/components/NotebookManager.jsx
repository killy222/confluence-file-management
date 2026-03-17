import { useState } from 'react';
import { createNotebook, updateNotebook, deleteNotebook } from '../api';

export default function NotebookManager({ notebooks = [], onReload }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [name, setName] = useState('');

  async function handleCreate(e) {
    e.preventDefault();
    if (!name.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await createNotebook({ name: name.trim() });
      setName('');
      await onReload?.();
    } catch (e) {
      setError(e.message || e.status || 'Failed to create notebook');
    } finally {
      setLoading(false);
    }
  }

  async function handleUpdate(id, nextName) {
    if (!nextName.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await updateNotebook(id, { name: nextName.trim() });
      await onReload?.();
    } catch (e) {
      setError(e.message || e.status || 'Failed to update notebook');
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Delete this notebook target?')) return;
    setLoading(true);
    setError(null);
    try {
      await deleteNotebook(id);
      await onReload?.();
    } catch (e) {
      setError(e.message || e.status || 'Failed to delete notebook');
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="mt-6" aria-label="NotebookLM notebooks">
      <h2 className="text-lg font-semibold text-white mb-3">NotebookLM notebooks</h2>
      <p className="text-xs text-slate-400 mb-3">
        Manage the NotebookLM notebooks available for push. Each push run uses the selected notebook.
      </p>

      <form
        onSubmit={handleCreate}
        className="mb-4 flex flex-wrap gap-2 items-end"
      >
        <div className="flex flex-col">
          <label className="text-xs text-slate-400 mb-1" htmlFor="notebook-name">
            Notebook name
          </label>
          <input
            id="notebook-name"
            name="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100 placeholder:text-slate-500 min-w-[220px]"
            placeholder="Phonix Sales"
          />
        </div>
        <button
          type="submit"
          className="px-4 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium transition min-h-[40px]"
        >
          Add notebook
        </button>
      </form>

      {error && (
        <p className="mb-2 text-xs text-red-400">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-slate-400 text-sm">Loading notebooks…</p>
      ) : notebooks.length === 0 ? (
        <p className="text-slate-500 text-sm">No notebooks configured yet.</p>
      ) : (
        <ul className="space-y-2">
          {notebooks.map((nb) => (
            <li
              key={nb.id}
              className="flex items-center justify-between gap-3 rounded-lg bg-slate-800 border border-slate-700 px-3 py-2"
            >
              <div className="min-w-0">
                <p className="text-sm text-slate-100 truncate">{nb.name}</p>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => {
                    const nextName = window.prompt('New notebook name', nb.name) ?? '';
                    if (!nextName.trim()) return;
                    handleUpdate(nb.id, nextName);
                  }}
                  className="px-2 py-1 rounded-md bg-slate-700 hover:bg-slate-600 text-xs text-slate-100"
                >
                  Edit
                </button>
                <button
                  type="button"
                  onClick={() => handleDelete(nb.id)}
                  className="px-2 py-1 rounded-md bg-red-700 hover:bg-red-600 text-xs text-red-50"
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}


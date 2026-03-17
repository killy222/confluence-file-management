import { useState } from 'react';
import { createSpace, updateSpace, deleteSpace } from '../api';

export default function SpacesManager({ spaces = [], onReload }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({ key: '', label: '' });

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleCreate(e) {
    e.preventDefault();
    if (!form.key.trim() || !form.label.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await createSpace({ key: form.key.trim(), label: form.label.trim() });
      setForm({ key: '', label: '' });
      await onReload?.();
    } catch (e) {
      setError(e.message || e.status || 'Failed to create space');
    } finally {
      setLoading(false);
    }
  }

  async function handleUpdate(id, patch) {
    setLoading(true);
    setError(null);
    try {
      await updateSpace(id, patch);
      await onReload?.();
    } catch (e) {
      setError(e.message || e.status || 'Failed to update space');
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Delete this space?')) return;
    setLoading(true);
    setError(null);
    try {
      await deleteSpace(id);
      await onReload?.();
    } catch (e) {
      setError(e.message || e.status || 'Failed to delete space');
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="mt-8" aria-label="Confluence spaces">
      <h2 className="text-lg font-semibold text-white mb-3">Confluence spaces</h2>
      <p className="text-xs text-slate-400 mb-3">
        Manage the Confluence spaces available for export. Each run uses the selected space key.
      </p>

      <form
        onSubmit={handleCreate}
        className="mb-4 flex flex-wrap gap-2 items-end"
      >
        <div className="flex flex-col">
          <label className="text-xs text-slate-400 mb-1" htmlFor="space-label">
            Label
          </label>
          <input
            id="space-label"
            name="label"
            value={form.label}
            onChange={handleChange}
            className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100 placeholder:text-slate-500 min-w-[180px]"
            placeholder="Phonix Sales"
          />
        </div>
        <div className="flex flex-col">
          <label className="text-xs text-slate-400 mb-1" htmlFor="space-key">
            Space key
          </label>
          <input
            id="space-key"
            name="key"
            value={form.key}
            onChange={handleChange}
            className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-100 placeholder:text-slate-500 min-w-[120px]"
            placeholder="PHS"
          />
        </div>
        <button
          type="submit"
          className="px-4 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium transition min-h-[40px]"
        >
          Add space
        </button>
      </form>

      {error && (
        <p className="mb-2 text-xs text-red-400">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-slate-400 text-sm">Loading spaces…</p>
      ) : spaces.length === 0 ? (
        <p className="text-slate-500 text-sm">No spaces configured yet.</p>
      ) : (
        <ul className="space-y-2">
          {spaces.map((space) => (
            <li
              key={space.id}
              className="flex items-center justify-between gap-3 rounded-lg bg-slate-800 border border-slate-700 px-3 py-2"
            >
              <div className="min-w-0">
                <p className="text-sm text-slate-100 truncate">{space.label}</p>
                <p className="text-xs text-slate-400">Key: {space.key}</p>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => {
                    const nextLabel = window.prompt('New label', space.label) ?? '';
                    if (!nextLabel.trim()) return;
                    handleUpdate(space.id, { label: nextLabel.trim() });
                  }}
                  className="px-2 py-1 rounded-md bg-slate-700 hover:bg-slate-600 text-xs text-slate-100"
                >
                  Edit
                </button>
                <button
                  type="button"
                  onClick={() => handleDelete(space.id)}
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


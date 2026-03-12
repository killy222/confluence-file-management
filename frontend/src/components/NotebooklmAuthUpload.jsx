import { useRef, useState } from 'react';
import { uploadNotebooklmAuth } from '../api';

export default function NotebooklmAuthUpload() {
  const inputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);
  const [isError, setIsError] = useState(false);

  function handleClick() {
    setMessage(null);
    if (inputRef.current) {
      inputRef.current.click();
    }
  }

  async function handleChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setMessage(null);
    setIsError(false);

    try {
      await uploadNotebooklmAuth(file);
      setMessage('NotebookLM auth updated successfully.');
    } catch (e) {
      setIsError(true);
      setMessage(e.message || 'Upload failed.');
    } finally {
      setUploading(false);
      // Reset input so the same file can be selected again if needed.
      event.target.value = '';
    }
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <button
        type="button"
        onClick={handleClick}
        disabled={uploading}
        className="px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-sm text-slate-100 transition"
      >
        {uploading ? 'Uploading…' : 'Upload NotebookLM auth'}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept=".json,application/json"
        className="hidden"
        onChange={handleChange}
      />
      {message && (
        <p className={`text-xs ${isError ? 'text-red-400' : 'text-emerald-400'}`}>{message}</p>
      )}
    </div>
  );
}


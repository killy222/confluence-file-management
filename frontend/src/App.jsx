import { useState, useEffect, useCallback } from 'react';
import Nav from './components/Nav';
import Overview from './components/Overview';
import RunHistory from './components/RunHistory';
import FileList from './components/FileList';
import TriggerRuns from './components/TriggerRuns';
import NotebooklmAuthUpload from './components/NotebooklmAuthUpload';
import SpacesManager from './components/SpacesManager';
import NotebookManager from './components/NotebookManager';
import { getRuns, getFiles, getSpaces, getNotebooks } from './api';
import './App.css';

function App() {
  const [runs, setRuns] = useState([]);
  const [files, setFiles] = useState([]);
  const [loadingRuns, setLoadingRuns] = useState(true);
  const [loadingFiles, setLoadingFiles] = useState(true);
  const [error, setError] = useState(null);
  const [spaces, setSpaces] = useState([]);
  const [notebooks, setNotebooks] = useState([]);

  const loadRuns = useCallback(async (silent = false) => {
    if (!silent) {
      setLoadingRuns(true);
      setError(null);
    }
    try {
      const data = await getRuns({ limit: 50 });
      setRuns(data.runs || []);
    } catch (e) {
      if (!silent) setError(e.message || 'Failed to load runs');
      setRuns([]);
    } finally {
      if (!silent) setLoadingRuns(false);
    }
  }, []);

  const loadFiles = useCallback(async (silent = false) => {
    if (!silent) setLoadingFiles(true);
    try {
      const data = await getFiles();
      setFiles(data.files || []);
    } catch (_) {
      setFiles([]);
    } finally {
      if (!silent) setLoadingFiles(false);
    }
  }, []);

  const loadSpaces = useCallback(async () => {
    try {
      const data = await getSpaces();
      setSpaces(data || []);
    } catch (_) {
      setSpaces([]);
    }
  }, []);

  const loadNotebooks = useCallback(async () => {
    try {
      const data = await getNotebooks();
      setNotebooks(data || []);
    } catch (_) {
      setNotebooks([]);
    }
  }, []);

  useEffect(() => {
    loadRuns();
    loadFiles();
    loadSpaces();
    loadNotebooks();
  }, [loadRuns, loadFiles, loadSpaces, loadNotebooks]);

  const hasRunning = runs.some((r) => r.status === 'running');
  useEffect(() => {
    if (!hasRunning) return;
    const intervalId = setInterval(() => {
      loadRuns(true);
      loadFiles(true);
    }, 5_000);
    return () => clearInterval(intervalId);
  }, [hasRunning, loadRuns, loadFiles]);

  function handleTriggered() {
    loadRuns();
    loadFiles();
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200">
      <Nav />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-900/30 border border-red-700 text-red-200">
            {error} — is the backend running at {import.meta.env.VITE_API_URL || 'http://localhost:8000'}?
          </div>
        )}
        <TriggerRuns
          onTriggered={handleTriggered}
          runs={runs}
          spaces={spaces}
          notebooks={notebooks}
        />
        <Overview runs={runs} loading={loadingRuns} />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
          <div className="lg:col-span-2">
            <RunHistory runs={runs} loading={loadingRuns} onRefresh={loadRuns} />
            <SpacesManager spaces={spaces} onReload={loadSpaces} />
            <NotebookManager notebooks={notebooks} onReload={loadNotebooks} />
          </div>
          <div>
            <FileList
              files={files}
              loading={loadingFiles}
              authUploader={<NotebooklmAuthUpload />}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

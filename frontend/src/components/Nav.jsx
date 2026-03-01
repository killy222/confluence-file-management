export default function Nav() {
  return (
    <nav className="flex items-center justify-between px-6 py-4 bg-slate-900 border-b border-slate-700">
      <div className="flex items-center gap-6">
        <h1 className="text-xl font-semibold text-white">Agents Dashboard</h1>
        <a href="#dashboard" className="text-slate-300 hover:text-white transition">Dashboard</a>
        <a href="#files" className="text-slate-300 hover:text-white transition">Files</a>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-slate-400 text-sm" aria-hidden="true">Workflow status</span>
      </div>
    </nav>
  );
}

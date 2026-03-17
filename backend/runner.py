"""Run extract_confluence and push_to_notebooklm scripts; persist run state and file list."""

import asyncio
import json
import os
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.db import async_session_maker
from backend.models import ExportedFile, Run


def _env_for_scripts() -> dict[str, str]:
    """Build env for subprocess: inherit current env, ensure PYTHONPATH and script defaults.
    Confluence and NotebookLM vars from settings (loaded from .env) are passed through so
    the subprocess always gets them when the backend is configured."""
    env = os.environ.copy()
    root = settings.project_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env["PYTHONPATH"] = root
    env.setdefault("CONFLUENCE_EXPORT_DIR", settings.get_export_dir())
    env.setdefault("NOTEBOOKLM_NOTEBOOK_NAME", settings.notebooklm_notebook_name)
    if settings.confluence_url:
        env["CONFLUENCE_URL"] = settings.confluence_url
    if settings.confluence_user:
        env["CONFLUENCE_USER"] = settings.confluence_user
    if settings.confluence_password:
        env["CONFLUENCE_PASSWORD"] = settings.confluence_password
    return env


async def _run_subprocess(cmd: list[str], cwd: str, env: dict[str, str]) -> tuple[int, str, str]:
    """Run command in subprocess; return (returncode, stdout, stderr)."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode or 0, (stdout or b"").decode("utf-8", errors="replace"), (stderr or b"").decode("utf-8", errors="replace")


async def run_confluence_export(run_id: str, db: AsyncSession) -> None:
    """Execute extract_confluence.py; update Run and insert ExportedFile rows from manifest."""
    run = await db.get(Run, run_id)
    if not run or run.script != "confluence_export":
        return
    root = settings.project_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    export_dir = settings.get_export_dir()
    python = "python3"
    if not os.path.isfile(settings.get_extract_path()):
        run.status = "failure"
        run.finished_at = datetime.now(timezone.utc)
        run.error_message = f"Script not found: {settings.get_extract_path()}"
        await db.commit()
        return
    cmd = [
        python,
        settings.get_extract_path(),
        "--space", settings.confluence_space,
        "--label", settings.confluence_label,
        "--output", export_dir,
        "--manifest",
    ]
    env = _env_for_scripts()
    returncode, stdout, stderr = await _run_subprocess(cmd, root, env)
    run.finished_at = datetime.now(timezone.utc)
    run.log_output = (stdout + "\n" + stderr).strip() or None
    if returncode != 0:
        run.status = "failure"
        run.error_message = stderr.strip() or f"Exit code {returncode}"
    else:
        run.status = "success"
        manifest_path = os.path.join(export_dir, "manifest.json")
        if os.path.isfile(manifest_path):
            try:
                with open(manifest_path, encoding="utf-8") as f:
                    entries = json.load(f)
                for entry in entries:
                    path = entry.get("output_path") or ""
                    if os.path.isabs(path):
                        path = os.path.basename(path)
                    ef = ExportedFile(
                        run_id=run_id,
                        path=path,
                        title=entry.get("title"),
                        page_id=str(entry.get("page_id", "")),
                    )
                    db.add(ef)
            except Exception as e:
                run.log_output = (run.log_output or "") + f"\nManifest read error: {e}"
    await db.commit()


async def run_notebooklm_push(run_id: str, db: AsyncSession) -> None:
    """Execute push_to_notebooklm.py; update Run."""
    run = await db.get(Run, run_id)
    if not run or run.script != "notebooklm_push":
        return
    root = settings.project_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    export_dir = settings.get_export_dir()
    python = "python3"
    if not os.path.isfile(settings.get_push_path()):
        run.status = "failure"
        run.finished_at = datetime.now(timezone.utc)
        run.error_message = f"Script not found: {settings.get_push_path()}"
        await db.commit()
        return
    notebook_arg = run.notebook_name or settings.notebooklm_notebook_name
    cmd = [
        python,
        settings.get_push_path(),
        "--export-dir",
        export_dir,
        "--notebook",
        notebook_arg,
        "--truncate-first",
    ]
    env = _env_for_scripts()
    returncode, stdout, stderr = await _run_subprocess(cmd, root, env)
    run.finished_at = datetime.now(timezone.utc)
    run.log_output = (stdout + "\n" + stderr).strip() or None
    if returncode != 0:
        run.status = "failure"
        run.error_message = stderr.strip() or f"Exit code {returncode}"
    else:
        run.status = "success"
    await db.commit()


async def execute_runs(run_ids: list[str]) -> None:
    """
    Execute scripts in order (confluence_export then notebooklm_push if both).
    Only start push after export succeeds. Uses its own DB session.
    """
    async with async_session_maker() as db:
        for run_id in run_ids:
            run = await db.get(Run, run_id)
            if not run:
                continue
            if run.script == "confluence_export":
                await run_confluence_export(run_id, db)
            elif run.script == "notebooklm_push":
                await run_notebooklm_push(run_id, db)
            # Chained: only run push after export succeeds
            if len(run_ids) > 1 and run_id == run_ids[0]:
                await db.refresh(run)
                if run.status != "success":
                    push_run = await db.get(Run, run_ids[1])
                    if push_run:
                        push_run.status = "failure"
                        push_run.finished_at = datetime.now(timezone.utc)
                        push_run.error_message = "Skipped: previous step (confluence_export) did not succeed"
                        await db.commit()
                    return

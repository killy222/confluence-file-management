# Windows: Full installation and run guide (Path A — Docker)

This guide gets you from zero to a running project on Windows using **only Git and Docker Desktop**. No Python or Node.js is required on your machine to run the full stack. The only exception: if you want to use **NotebookLM push** (“Run push files to notebook”), you must run a one-time login that needs Python on the host (or you can skip push and use only Confluence export).

---

## 1. Prerequisites

### 1.1 Git

**Check if installed**

Press **Win + R**, type `powershell`, press **Enter**. Then run:

```powershell
git --version
```

If you see a version (e.g. `git version 2.43.0`), Git is installed. Otherwise install it.

**Install on Windows**

1. Download: [https://git-scm.com/download/win](https://git-scm.com/download/win)
2. Run the installer.
3. When asked, choose **"Git from the command line and also from 3rd-party software"** so `git` is available in the terminal.
4. Press **Win + R**, type `powershell`, press **Enter**, then run `git --version` again to confirm.

---

### 1.2 Docker Desktop

**Check if installed**

Press **Win + R**, type `powershell`, press **Enter**. Then run:

```powershell
docker --version
docker compose version
```

If both commands show a version, Docker and Docker Compose are installed. Otherwise install Docker Desktop.

**Install on Windows**

1. Download: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
2. Run the installer. If prompted, use the **WSL 2** backend (recommended).
3. Restart the computer if asked.
4. Start **Docker Desktop** from the Start menu and wait until it shows “Docker Desktop is running” (whale icon in the system tray).
5. Press **Win + R**, type `powershell`, press **Enter**, then run again: `docker --version` and `docker compose version` to confirm.

---

## 2. Clone the repository

1. Press **Win + R**, type `powershell`, press **Enter**.
2. Go to a folder where you want the project (e.g. your user folder or `C:\Projects`):

   ```powershell
   cd C:\Projects
   ```

   (Create the folder first if needed: `mkdir C:\Projects`.)

3. Clone the repo (use HTTPS if you don’t use SSH keys):

   ```powershell
   git clone https://github.com/killy222/confluence-file-management.git
   ```

   Or with SSH (after [setting up GitHub SSH](GITHUB_SETUP.md)):

   ```powershell
   git clone git@github.com:killy222/confluence-file-management.git
   ```

4. Go into the project folder:

   ```powershell
   cd confluence-file-management
   ```

---

## 3. Configuration

1. Copy the example env file (in the same PowerShell window from step 2):

   ```powershell
   copy .env.example .env
   ```

2. Edit `.env` with Notepad or another editor:

   ```powershell
   notepad .env
   ```

   Set at least:

   - `POSTGRES_PASSWORD` — choose a password (e.g. keep `postgres` for local use).

   Optional (for Confluence export and NotebookLM push from the dashboard):

   - `CONFLUENCE_URL` — your Confluence base URL.
   - `CONFLUENCE_USER` — Confluence username.
   - `CONFLUENCE_PASSWORD` — Confluence password.
   - `NOTEBOOKLM_NOTEBOOK_NAME` — target NotebookLM notebook name (e.g. `Phonix Sales`).
   - `NOTEBOOKLM_AUTH_DIR` — on Windows set to your user profile folder so the container can use your NotebookLM login:

   ```env
   NOTEBOOKLM_AUTH_DIR=%USERPROFILE%\.notebooklm
   ```

   Save and close the file.

3. **NotebookLM push (optional)**  
   Only needed if you want to use “Run push files to notebook” in the dashboard. The one-time login opens a browser for Google sign-in and **requires Python on your Windows machine** (Path A does not install Python by default).

   - **Option A — Install Python only for this step:**

     1. **Check if Python is already installed**  
        Press **Win + R**, type `powershell`, press **Enter**. Then run:

        ```powershell
        python --version
        ```

        If you see a version (e.g. `Python 3.12.0`), Python is installed. If the command is not found, try:

        ```powershell
        py -3 --version
        ```

        If that works, use `py -3` instead of `python` in the commands below. If both fail, install Python (step 2).

     2. **Install Python (if not installed)**  
        - Download the Windows installer: [https://www.python.org/downloads/](https://www.python.org/downloads/) — click the yellow **“Download Python 3.x.x”** button.
        - Run the installer. On the first screen, **check the box “Add python.exe to PATH”** at the bottom, then click **“Install Now”**.
        - When the install finishes, close any open PowerShell windows, then open a new one (Press **Win + R**, type `powershell`, press **Enter**) and run `python --version` again to confirm.
        - **If you forgot “Add to PATH”:** Uninstall Python from Settings → Apps, run the installer again and check “Add python.exe to PATH”. Or add it manually: **Settings → System → About → Advanced system settings → Environment Variables** → under “User variables” select **Path** → **Edit** → **New** → add `C:\Users\YourName\AppData\Local\Programs\Python\Python312` and `C:\Users\YourName\AppData\Local\Programs\Python\Python312\Scripts` (replace `YourName` and `Python312` with your username and the actual Python folder name).

     3. **Run the one-time NotebookLM login**  
        Press **Win + R**, type `powershell`, press **Enter**. Then run:

        ```powershell
        pip install "notebooklm-py[browser]"
        notebooklm login
        ```

        A browser opens; sign in with your Google account. Auth is saved under `%USERPROFILE%\.notebooklm`. Set `NOTEBOOKLM_AUTH_DIR=%USERPROFILE%\.notebooklm` in `.env` so the Docker backend can use it.

   - **Option B — Skip NotebookLM push:**  
     If you only need Confluence export and the dashboard (runs, files list), you do not need Python or NotebookLM login. Leave the push-related `.env` vars unset and do not use “Run push files to notebook.”

---

## 4. Run the project (Docker)

1. Make sure **Docker Desktop** is running (whale icon in the system tray).

2. In the project folder (e.g. `C:\Projects\confluence-file-management`) run:

   ```powershell
   docker compose up -d --build
   ```

   The first run can take a few minutes (downloading images and building). When it finishes, postgres, backend, and frontend containers are running.

3. Apply database migrations (one-off):

   ```powershell
   docker compose run --rm -w /app/backend backend python -m alembic upgrade head
   ```

4. Open in your browser:

   - **Dashboard:** [http://localhost:80](http://localhost:80)
   - **API docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 5. Verify

- The dashboard loads and shows “Overview” and “Active pipelines.”
- In API docs ([http://localhost:8000/docs](http://localhost:8000/docs)), try **GET /api/v1/health** — it should return `{"status":"ok","database":"connected"}`.
- If you set Confluence credentials in `.env`, use the dashboard to trigger “Run Confluence Export” and check that a run appears.
- If you set NotebookLM auth (and `NOTEBOOKLM_AUTH_DIR`), you can run “Run push files to notebook” after an export.

---

## 6. Optional: run scripts or tests in containers

To run the Confluence extract or NotebookLM push script manually, or to run tests:

```powershell
docker compose --profile tools run --rm app python extract_confluence.py --space PHS --label notebook --output /app/confluence_export --manifest
```

```powershell
docker compose --profile tools run --rm app python push_to_notebooklm.py --export-dir ./confluence_export --notebook "Phonix Sales"
```

```powershell
docker compose --profile tools run --rm app pytest tests/ -v
```

---

## 7. Stop the project

```powershell
docker compose down
```

Data in the database is kept in a Docker volume. To remove it as well:

```powershell
docker compose down -v
```

---

## 8. Troubleshooting (Windows)

| Problem | What to do |
|--------|------------|
| **“Docker daemon not running”** or `docker` not found | Start **Docker Desktop** from the Start menu and wait until it is fully running. |
| **Port 80 or 8000 already in use** | Stop the other app using that port, or change the port in `docker-compose.yml` (e.g. frontend `ports: "8080:80"`). |
| **`.env` seems ignored** | Ensure the file is named `.env` (no `.txt`) and is in the same folder as `docker-compose.yml`. Edit with “Save as” and choose “All files” so it doesn’t become `.env.txt`. |
| **NotebookLM: “auth not found”** | Run `notebooklm login` once (see step 3). Set `NOTEBOOKLM_AUTH_DIR=%USERPROFILE%\.notebooklm` in `.env` and restart: `docker compose up -d --force-recreate backend`. |
| **Git clone asks for GitHub login** | Use a [Personal Access Token](https://github.com/settings/tokens) as the password when using HTTPS, or set up SSH: see [docs/GITHUB_SETUP.md](GITHUB_SETUP.md). |
| **“Cannot connect to the Docker daemon”** | Start Docker Desktop; if it still fails, in Docker Desktop go to Settings → Resources and ensure enough memory/disk is allocated. |

---

## Summary (Path A)

- **Install:** Git + Docker Desktop (check with `git --version`, `docker --version`, `docker compose version`).
- **Clone:** `git clone https://github.com/killy222/confluence-file-management.git` then `cd confluence-file-management`.
- **Configure:** `copy .env.example .env`, edit `.env` (at least `POSTGRES_PASSWORD`; optional Confluence/NotebookLM and `NOTEBOOKLM_AUTH_DIR=%USERPROFILE%\.notebooklm`).
- **Run:** `docker compose up -d --build`, then `docker compose run --rm -w /app/backend backend python -m alembic upgrade head`.
- **Open:** [http://localhost:80](http://localhost:80) (dashboard), [http://localhost:8000/docs](http://localhost:8000/docs) (API).

For more details on the project and running without Docker, see the main [README.md](../README.md).

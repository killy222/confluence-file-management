"""Application configuration from environment."""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env from project root (parent of backend/) so it's found regardless of CWD (e.g. in Docker)
_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CONFIG_DIR)
_ENV_FILE = os.path.join(_PROJECT_ROOT, ".env")


class Settings(BaseSettings):
    """Backend settings. Env vars pass through for scripts (CONFLUENCE_*, NOTEBOOKLM_*)."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/agents"

    # Paths (project root = parent of backend/)
    project_root: str = ""
    export_dir: str = "confluence_export_pdf"
    script_extract: str = "extract_confluence.py"
    script_push: str = "push_to_notebooklm.py"

    # Confluence (required for extract script; set in .env or environment)
    confluence_url: str = ""
    confluence_user: str = ""
    confluence_password: str = ""
    # Confluence extract defaults (env can override)
    confluence_space: str = "PHS"
    confluence_label: str = "notebook"

    # NotebookLM push: notebook name or ID (env NOTEBOOKLM_NOTEBOOK_NAME overrides)
    notebooklm_notebook_name: str = "Phonix Sales"
    # NotebookLM auth home directory (env NOTEBOOKLM_HOME overrides). The storage_state.json
    # file used by notebooklm-py will be written/read from this directory.
    notebooklm_home: str = ""
    # If true, clear the target NotebookLM notebook before each push_to_notebooklm run.
    notebooklm_truncate_before_push: bool = False

    def get_extract_path(self) -> str:
        import os
        root = self.project_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(root, self.script_extract)

    def get_push_path(self) -> str:
        import os
        root = self.project_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(root, self.script_push)

    def get_export_dir(self) -> str:
        import os
        root = self.project_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(root, self.export_dir)

    def get_notebooklm_home(self) -> str:
        """Return NotebookLM auth home directory."""
        import os

        # If explicitly set (or via env), use it.
        if self.notebooklm_home:
            return self.notebooklm_home
        # Prefer NOTEBOOKLM_HOME env if present.
        env_home = os.environ.get("NOTEBOOKLM_HOME")
        if env_home:
            return env_home
        # Fallback: project-root .notebooklm directory
        root = self.project_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(root, ".notebooklm")


settings = Settings()

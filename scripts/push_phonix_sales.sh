#!/usr/bin/env bash
# Push Confluence export to NotebookLM notebook "Phonix Sales".
# Prerequisite: run `notebooklm login` once and sign in with your Google account.
set -e
cd "$(dirname "$0")/.."
python3 push_to_notebooklm.py --export-dir ./confluence_export --notebook "Phonix Sales" "$@"

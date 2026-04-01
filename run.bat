@echo off
REM ─── Islamic Finance Course — Quick Commands ───────────────────────────────
REM
REM Usage:
REM   run expand      — Query NotebookLM and populate all module content
REM   run quizzes     — Inject/refresh knowledge check quizzes
REM   run reading     — Rebuild the Essential Reading List page
REM   run build       — Build the MkDocs site to /site
REM   run serve       — Live-reload dev server at http://localhost:8000
REM   run full        — Full pipeline: expand + quizzes + reading + build
REM ────────────────────────────────────────────────────────────────────────────

set CMD=%1

if "%CMD%"=="expand" (
    .venv\Scripts\python scripts\expand_sections.py
    goto :eof
)
if "%CMD%"=="quizzes" (
    .venv\Scripts\python scripts\generate_quizzes.py
    goto :eof
)
if "%CMD%"=="reading" (
    .venv\Scripts\python scripts\build_reading_list.py
    goto :eof
)
if "%CMD%"=="build" (
    .venv\Scripts\mkdocs build
    goto :eof
)
if "%CMD%"=="serve" (
    .venv\Scripts\mkdocs serve
    goto :eof
)
if "%CMD%"=="full" (
    echo [1/4] Expanding sections via NotebookLM...
    .venv\Scripts\python scripts\expand_sections.py
    echo [2/4] Injecting quizzes...
    .venv\Scripts\python scripts\generate_quizzes.py
    echo [3/4] Building reading list...
    .venv\Scripts\python scripts\build_reading_list.py
    echo [4/4] Building site...
    .venv\Scripts\mkdocs build
    echo Done. Site is in /site
    goto :eof
)

echo Usage: run [expand^|quizzes^|reading^|build^|serve^|full]

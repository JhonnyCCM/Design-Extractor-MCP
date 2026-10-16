"""
Auto-Update Engine for Design Extractor MCP.
Checks for updates against GitHub repository and provides one-click / one-command self-updating.
"""

import os
import sys
import json
import time
import shutil
import urllib.request
import subprocess
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

from storage import atomic_write

PROJECT_ROOT = Path(__file__).parent.resolve()
PYTHON_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe" if sys.platform == "win32" else PROJECT_ROOT / ".venv" / "bin" / "python"
if not PYTHON_EXE.exists():
    PYTHON_EXE = Path(sys.executable)

GITHUB_REPO = "JhonnyCCM/Design-Extractor-MCP"
CURRENT_VERSION = "1.3.0"
UPDATE_CACHE_FILE = PROJECT_ROOT / ".cache" / "update_status.json"


def get_current_commit() -> Optional[str]:
    """Gets the short commit hash of current local HEAD if inside a git repository."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=3
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return None


def check_for_updates(force: bool = False) -> Tuple[bool, str, Optional[str]]:
    """
    Checks if an update is available on GitHub main branch.
    Returns:
        (has_update: bool, status_message: str, remote_identifier: Optional[str])
    """
    # Check cache if not forced (cache valid for 10 minutes)
    if not force and UPDATE_CACHE_FILE.exists():
        try:
            cached = json.loads(UPDATE_CACHE_FILE.read_text(encoding="utf-8"))
            if time.time() - cached.get("checked_at", 0) < 600:
                return cached.get("has_update", False), cached.get("message", ""), cached.get("remote_id")
        except Exception:
            pass

    local_commit = get_current_commit()
    remote_commit = None

    # 1. Try git ls-remote (fast, no heavy clone)
    if shutil.which("git"):
        try:
            res = subprocess.run(
                ["git", "ls-remote", "origin", "refs/heads/main"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=5
            )
            if res.returncode == 0 and res.stdout.strip():
                parts = res.stdout.strip().split()
                if parts:
                    remote_commit = parts[0][:7]
        except Exception:
            pass

    # 2. Fallback to GitHub REST API if git ls-remote fails
    if not remote_commit:
        try:
            req = urllib.request.Request(
                f"https://api.github.com/repos/{GITHUB_REPO}/commits/main",
                headers={"User-Agent": "Design-Extractor-MCP-Updater"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    sha = data.get("sha", "")
                    if sha:
                        remote_commit = sha[:7]
        except Exception:
            pass

    if not remote_commit:
        msg = "No se pudo comprobar la conexión con GitHub para actualizaciones."
        return False, msg, None

    if local_commit and local_commit != remote_commit:
        msg = f"Nueva actualización disponible en GitHub (Local: {local_commit} → Remoto: {remote_commit})."
        has_update = True
    else:
        msg = f"Design Extractor está al día (Versión v{CURRENT_VERSION} · {local_commit or 'main'})."
        has_update = False

    # Save check to cache
    try:
        UPDATE_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(UPDATE_CACHE_FILE, json.dumps({
            "has_update": has_update,
            "message": msg,
            "remote_id": remote_commit,
            "checked_at": time.time()
        }))
    except Exception:
        pass

    return has_update, msg, remote_commit


def apply_update() -> Tuple[bool, str]:
    """
    Applies the latest update from GitHub repository:
    1. Runs git pull origin main.
    2. Updates dependencies via pip.
    3. Re-registers global PATH shims.
    """
    if not shutil.which("git"):
        return False, "Git no está instalado o no se encuentra en el PATH para actualizar automáticamente."

    if not (PROJECT_ROOT / ".git").exists():
        return False, "La carpeta actual no es un repositorio Git clonado."

    # Step 1: Git pull
    try:
        pull_res = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30
        )
        if pull_res.returncode != 0:
            err = pull_res.stderr or pull_res.stdout
            return False, f"Fallo al ejecutar 'git pull': {err.strip()}"
    except Exception as e:
        return False, f"Excepción durante 'git pull': {str(e)}"

    # Step 2: Refresh dependencies
    req_file = PROJECT_ROOT / "requirements.txt"
    if req_file.exists():
        try:
            subprocess.run(
                [str(PYTHON_EXE), "-m", "pip", "install", "-r", str(req_file), "--quiet"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                timeout=60
            )
        except Exception:
            pass

    # Step 3: Refresh global PATH shims
    try:
        from path_installer import install_global_command
        install_global_command()
    except Exception:
        pass

    # Clear update cache so next check is fresh
    if UPDATE_CACHE_FILE.exists():
        try:
            UPDATE_CACHE_FILE.unlink()
        except Exception:
            pass

    new_commit = get_current_commit() or "main"
    return True, f"¡Actualización completada con éxito! Design Extractor actualizado al commit {new_commit}."

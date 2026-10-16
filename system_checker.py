"""
System Diagnostics and Auto-Repair for Playwright Chromium Engine.
Verifies and installs required browser binaries in the background without manual intervention.
"""

import sys
import subprocess
from pathlib import Path
from typing import Tuple, Optional

PROJECT_ROOT = Path(__file__).parent.resolve()
PYTHON_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe" if sys.platform == "win32" else PROJECT_ROOT / ".venv" / "bin" / "python"
if not PYTHON_EXE.exists():
    PYTHON_EXE = Path(sys.executable)


def is_browser_ready() -> bool:
    """Quick check to verify if Playwright Chromium can be launched."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
            return True
    except Exception:
        return False


def ensure_browser_ready(console=None) -> Tuple[bool, str]:
    """
    Checks if Chromium is installed. If not, automatically runs
    'playwright install chromium' with progress feedback.
    """
    if is_browser_ready():
        return True, "Playwright Chromium está listo y operativo."

    msg = "Preparando navegador Chromium headless en segundo plano..."
    if console:
        with console.status(f"[bold #38bdf8]{msg}[/bold #38bdf8]", spinner="dots"):
            return _install_chromium()
    else:
        print(f"[*] {msg}")
        return _install_chromium()


def _install_chromium() -> Tuple[bool, str]:
    """Executes playwright install chromium."""
    try:
        cmd = [str(PYTHON_EXE), "-m", "playwright", "install", "chromium"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180
        )
        if result.returncode == 0:
            return True, "Chromium instalado y verificado exitosamente."
        else:
            err = result.stderr or result.stdout or "Error desconocido durante la instalación."
            return False, f"Fallo al instalar Chromium: {err.strip()}"
    except Exception as e:
        return False, f"Excepción durante instalación de navegador: {str(e)}"

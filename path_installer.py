"""
PATH Command Integration for Design Extractor MCP.
Allows executing 'design-extractor' from any directory or terminal globally
without needing to navigate to the project directory or specify full Python paths.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Tuple

PROJECT_ROOT = Path(__file__).parent.resolve()
CLI_SCRIPT = PROJECT_ROOT / "cli.py"

# Resolve python interpreter
PYTHON_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe" if sys.platform == "win32" else PROJECT_ROOT / ".venv" / "bin" / "python"
if not PYTHON_EXE.exists():
    PYTHON_EXE = Path(sys.executable)


def get_windows_apps_dir() -> Path:
    """Returns the WindowsApps user directory which is in PATH by default."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        p = Path(local_app_data) / "Microsoft" / "WindowsApps"
        if p.exists():
            return p
    return Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps"


def get_unix_bin_dir() -> Path:
    """Returns ~/.local/bin or /usr/local/bin for Linux/macOS."""
    local_bin = Path.home() / ".local" / "bin"
    if local_bin.exists():
        return local_bin
    local_bin.mkdir(parents=True, exist_ok=True)
    return local_bin


def is_path_installed() -> bool:
    """Checks if the 'design-extractor' executable or command is reachable in PATH."""
    return shutil.which("design-extractor") is not None


def install_global_command() -> Tuple[bool, str]:
    """
    Installs the global 'design-extractor' command into the user's PATH.
    On Windows: creates 'design-extractor.cmd' and 'design-extractor.ps1' in WindowsApps.
    On Linux/macOS: creates 'design-extractor' script in ~/.local/bin with chmod +x.
    """
    py_path = str(PYTHON_EXE.resolve())
    cli_path = str(CLI_SCRIPT.resolve())

    if sys.platform == "win32":
        target_dir = get_windows_apps_dir()
        target_dir.mkdir(parents=True, exist_ok=True)

        cmd_path = target_dir / "design-extractor.cmd"
        ps1_path = target_dir / "design-extractor.ps1"

        cmd_content = f'@echo off\n"{py_path}" "{cli_path}" %*\n'
        ps1_content = f'& "{py_path}" "{cli_path}" $args\n'

        try:
            cmd_path.write_text(cmd_content, encoding="utf-8")
            ps1_path.write_text(ps1_content, encoding="utf-8")
            return True, f"Comando global instalado exitosamente en: {cmd_path}"
        except Exception as e:
            return False, f"No se pudo escribir el ejecutable en WindowsApps: {str(e)}"

    else:
        target_dir = get_unix_bin_dir()
        sh_path = target_dir / "design-extractor"
        sh_content = f'#!/usr/bin/env bash\nexec "{py_path}" "{cli_path}" "$@"\n'

        try:
            sh_path.write_text(sh_content, encoding="utf-8")
            sh_path.chmod(0o755)
            return True, f"Comando global instalado exitosamente en: {sh_path}"
        except Exception as e:
            return False, f"No se pudo escribir el ejecutable en ~/.local/bin: {str(e)}"


def uninstall_global_command() -> Tuple[bool, str]:
    """Removes the global 'design-extractor' command shims."""
    if sys.platform == "win32":
        target_dir = get_windows_apps_dir()
        cmd_path = target_dir / "design-extractor.cmd"
        ps1_path = target_dir / "design-extractor.ps1"

        removed = []
        if cmd_path.exists():
            cmd_path.unlink()
            removed.append(str(cmd_path))
        if ps1_path.exists():
            ps1_path.unlink()
            removed.append(str(ps1_path))

        if removed:
            return True, f"Comando desinstalado: {', '.join(removed)}"
        return False, "No se encontró el comando instalado para desinstalar."
    else:
        target_dir = get_unix_bin_dir()
        sh_path = target_dir / "design-extractor"
        if sh_path.exists():
            sh_path.unlink()
            return True, f"Comando desinstalado: {sh_path}"
        return False, "No se encontró el comando instalado para desinstalar."

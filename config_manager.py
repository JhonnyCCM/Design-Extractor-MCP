"""
Configuration Manager for Web Design Extractor MCP
Handles user-configurable output directory for generated Markdown specifications
and screenshots via environment variables, CLI arguments, or persistent config.json.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional

from storage import atomic_write

CONFIG_FILE = Path(__file__).parent / "config.json"
DEFAULT_OUTPUT_DIR = Path.home() / "DesignSpecs"



def get_configured_output_dir() -> Path:
    """
    Resolves the target output directory in order of precedence:
    1. CLI argument '--output-dir <path>'
    2. Environment variable 'DESIGN_SPECS_DIR' or 'OUTPUT_DIR'
    3. Persistent config.json file
    4. Default: ~/DesignSpecs (e.g. C:\\Users\\jonni\\DesignSpecs)
    """
    # 1. Check CLI args
    for i, arg in enumerate(sys.argv):
        if arg in ["--output-dir", "-o"] and i + 1 < len(sys.argv):
            path = Path(sys.argv[i + 1]).resolve()
            path.mkdir(parents=True, exist_ok=True)
            return path

    # 2. Check Environment Variable
    env_dir = os.environ.get("DESIGN_SPECS_DIR") or os.environ.get("OUTPUT_DIR")
    if env_dir:
        path = Path(env_dir).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    # 3. Check persistent config.json
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if "output_dir" in data and data["output_dir"]:
                path = Path(data["output_dir"]).resolve()
                path.mkdir(parents=True, exist_ok=True)
                return path
        except Exception:
            pass

    # 4. Default directory
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_OUTPUT_DIR


def set_configured_output_dir(new_path: str) -> str:
    """Persists a new output directory in config.json and creates the folder."""
    target_path = Path(new_path).resolve()
    target_path.mkdir(parents=True, exist_ok=True)

    data = {}
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    data["output_dir"] = str(target_path)
    atomic_write(CONFIG_FILE, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return str(target_path)


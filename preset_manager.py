"""
Custom Commands and Workflow Presets Manager for Design Extractor MCP.
Allows users to create, manage, and execute reusable custom extraction workflows
with predefined directories, screenshot settings, wait times, and parameters.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from storage import atomic_write

CONFIG_FILE = Path(__file__).parent / "config.json"


DEFAULT_PRESETS = {
    "quick": {
        "description": "Extracción rápida sin captura de pantalla",
        "output_dir": None,
        "screenshot": False,
        "wait_seconds": 1
    },
    "full": {
        "description": "Extracción completa en alta fidelidad con captura de pantalla y espera de hidratación",
        "output_dir": None,
        "screenshot": True,
        "wait_seconds": 4
    }
}


def _load_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_config(data: Dict[str, Any]) -> None:
    atomic_write(CONFIG_FILE, json.dumps(data, indent=2, ensure_ascii=False) + "\n")



def get_all_presets() -> Dict[str, Dict[str, Any]]:
    """Returns all custom commands (built-in defaults + user-defined)."""
    cfg = _load_config()
    user_presets = cfg.get("custom_commands", {})
    all_presets = dict(DEFAULT_PRESETS)
    all_presets.update(user_presets)
    return all_presets


def get_preset(name: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single preset by name."""
    presets = get_all_presets()
    return presets.get(name)


def create_or_update_preset(
    name: str,
    description: str = "",
    output_dir: Optional[str] = None,
    screenshot: bool = True,
    wait_seconds: int = 2
) -> Dict[str, Any]:
    """Creates or updates a custom workflow preset."""
    cfg = _load_config()
    if "custom_commands" not in cfg or not isinstance(cfg["custom_commands"], dict):
        cfg["custom_commands"] = {}

    preset_data = {
        "description": description or f"Flujo de trabajo personalizado '{name}'",
        "output_dir": str(Path(output_dir).resolve()) if output_dir else None,
        "screenshot": screenshot,
        "wait_seconds": max(1, min(15, wait_seconds))
    }

    cfg["custom_commands"][name] = preset_data
    _save_config(cfg)
    return preset_data


def delete_preset(name: str) -> bool:
    """Deletes a user-defined custom command."""
    cfg = _load_config()
    custom_cmds = cfg.get("custom_commands", {})
    if name in custom_cmds:
        del custom_cmds[name]
        cfg["custom_commands"] = custom_cmds
        _save_config(cfg)
        return True
    return False


def run_preset(
    name: str,
    url: str,
    custom_output: Optional[str] = None,
    storage_state: Optional[str] = None,
    cookies: Optional[Any] = None
) -> Dict[str, Any]:
    """Executes an extraction workflow configured by the specified preset."""
    preset = get_preset(name)
    if not preset:
        raise ValueError(f"Preset o comando personalizado '{name}' no existe.")

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    from config_manager import get_configured_output_dir
    from core_extractor import (
        extract_page_design_data,
        generate_agent_design_spec,
        generate_w3c_design_tokens,
        generate_shadcn_theme,
        generate_tailwind_v4_theme,
        take_screenshot
    )
    from server import _url_to_slug
    from storage import atomic_write

    out_dir = Path(custom_output).resolve() if custom_output else (
        Path(preset["output_dir"]).resolve() if preset.get("output_dir") else get_configured_output_dir()
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    slug = _url_to_slug(url)
    target_md = out_dir / f"{slug}_design_spec.md"
    target_tokens = out_dir / f"{slug}_design_tokens.json"
    target_shadcn = out_dir / f"{slug}_shadcn_globals.css"
    target_tw4 = out_dir / f"{slug}_tailwind_v4.css"
    target_png = out_dir / f"{slug}_preview.png" if preset.get("screenshot", True) else None

    wait_sec = preset.get("wait_seconds", 2)
    data = extract_page_design_data(
        url,
        wait_seconds=wait_sec,
        storage_state=storage_state,
        cookies=cookies
    )
    spec_md = generate_agent_design_spec(data, url)
    tokens_data = generate_w3c_design_tokens(data)
    shadcn_css = generate_shadcn_theme(data)
    tw4_css = generate_tailwind_v4_theme(data)

    atomic_write(target_md, spec_md)
    atomic_write(target_tokens, json.dumps(tokens_data, indent=2, ensure_ascii=False) + "\n")
    atomic_write(target_shadcn, shadcn_css)
    atomic_write(target_tw4, tw4_css)

    if target_png:
        take_screenshot(
            url,
            str(target_png),
            full_page=True,
            storage_state=storage_state,
            cookies=cookies
        )

    return {
        "preset": name,
        "url": url,
        "data": data,
        "spec_file": target_md,
        "tokens_file": target_tokens,
        "shadcn_file": target_shadcn,
        "tailwind_v4_file": target_tw4,
        "preview_file": target_png,
        "wait_seconds": wait_sec,
        "screenshot": bool(target_png),
        "output_dir": out_dir
    }


"""
Automatic Agent and CLI Integrator for Web Design Extractor MCP.
Detects installed AI CLIs, IDEs and agents (Antigravity, Codex, Claude, Cursor, Windsurf, VS Code)
and automatically registers/configures the MCP server in their respective configurations.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import tomlkit
from config_manager import get_configured_output_dir

PROJECT_ROOT = Path(__file__).parent.resolve()
CLI_SCRIPT = PROJECT_ROOT / "cli.py"
PYTHON_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe" if sys.platform == "win32" else PROJECT_ROOT / ".venv" / "bin" / "python"
if not PYTHON_EXE.exists():
    PYTHON_EXE = Path(sys.executable)


@dataclass
class AgentInfo:
    id: str
    name: str
    config_path: Path
    commands: Tuple[str, ...]
    is_installed: bool
    is_configured: bool
    status_detail: str


def get_agent_config_path(agent_id: str) -> Path:
    """Returns the expected configuration file path for each agent."""
    home = Path.home()
    appdata = Path(os.environ.get("APPDATA", home / "AppData/Roaming"))

    if agent_id == "antigravity":
        return home / ".gemini" / "config" / "mcp_config.json"
    elif agent_id == "codex":
        return Path(os.environ.get("CODEX_HOME", home / ".codex")) / "config.toml"
    elif agent_id == "claude_desktop":
        if sys.platform == "win32":
            return appdata / "Claude" / "claude_desktop_config.json"
        elif sys.platform == "darwin":
            return home / "Library/Application Support/Claude/claude_desktop_config.json"
        return Path(os.environ.get("XDG_CONFIG_HOME", home / ".config")) / "Claude" / "claude_desktop_config.json"
    elif agent_id == "claude_code":
        return home / ".claude.json"
    elif agent_id == "cursor":
        return home / ".cursor" / "mcp.json"
    elif agent_id == "windsurf":
        return home / ".codeium" / "windsurf" / "mcp_config.json"
    elif agent_id == "vscode":
        if sys.platform == "win32":
            return appdata / "Code" / "User" / "mcp.json"
        elif sys.platform == "darwin":
            return home / "Library/Application Support/Code/User/mcp.json"
        return Path(os.environ.get("XDG_CONFIG_HOME", home / ".config")) / "Code/User/mcp.json"

    raise ValueError(f"Agente desconocido: {agent_id}")


AGENT_DEFINITIONS = [
    {
        "id": "antigravity",
        "name": "Google Antigravity / Gemini CLI",
        "commands": ("agy", "antigravity", "gemini"),
    },
    {
        "id": "codex",
        "name": "OpenAI Codex CLI & App",
        "commands": ("codex",),
    },
    {
        "id": "claude_desktop",
        "name": "Claude Desktop",
        "commands": ("claude-desktop",),
    },
    {
        "id": "claude_code",
        "name": "Claude Code CLI",
        "commands": ("claude",),
    },
    {
        "id": "cursor",
        "name": "Cursor IDE",
        "commands": ("cursor", "cursor-agent", "agent"),
    },
    {
        "id": "windsurf",
        "name": "Windsurf IDE",
        "commands": ("windsurf",),
    },
    {
        "id": "vscode",
        "name": "VS Code (Copilot / Cline / Roo)",
        "commands": ("code", "code-insiders"),
    },
]


def detect_all_agents() -> Dict[str, AgentInfo]:
    """Detects installed tools and checks whether web-design-extractor is registered."""
    detected = {}

    for defn in AGENT_DEFINITIONS:
        agent_id = defn["id"]
        name = defn["name"]
        commands = defn["commands"]
        cfg_path = get_agent_config_path(agent_id)

        # Check binary in PATH or directory existence
        binary_found = any(shutil.which(cmd) for cmd in commands)
        dir_found = cfg_path.parent.exists()
        is_installed = binary_found or dir_found or cfg_path.exists()

        is_configured = False
        status_detail = "No detectado"

        if is_installed:
            status_detail = "Instalado" if binary_found else "Configuración encontrada"

            # Check if web-design-extractor is inside config
            if cfg_path.exists():
                try:
                    if agent_id == "codex":
                        doc = tomlkit.parse(cfg_path.read_text(encoding="utf-8"))
                        mcp_s = doc.get("mcp_servers", {})
                        if "web_design_extractor" in mcp_s or "web-design-extractor" in mcp_s:
                            is_configured = True
                    else:
                        data = json.loads(cfg_path.read_text(encoding="utf-8-sig"))
                        key = "servers" if agent_id == "vscode" else "mcpServers"
                        if isinstance(data.get(key), dict) and "web-design-extractor" in data[key]:
                            is_configured = True
                except Exception:
                    pass

        detected[agent_id] = AgentInfo(
            id=agent_id,
            name=name,
            config_path=cfg_path,
            commands=commands,
            is_installed=is_installed,
            is_configured=is_configured,
            status_detail=status_detail
        )

    return detected


def register_agent(agent_id: str) -> Tuple[bool, str]:
    """Registers web-design-extractor into the specified agent's configuration file."""
    cfg_path = get_agent_config_path(agent_id)
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    out_dir = str(get_configured_output_dir())

    python_path = str(PYTHON_EXE.resolve())
    cli_path = str(CLI_SCRIPT.resolve())

    if agent_id == "codex":
        try:
            doc = tomlkit.parse(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else tomlkit.document()
            mcp_table = doc.setdefault("mcp_servers", tomlkit.table())
            
            entry = tomlkit.table()
            entry["command"] = python_path
            entry["args"] = [cli_path, "serve"]
            entry["enabled"] = True
            entry["startup_timeout_sec"] = 60

            env_table = tomlkit.table()
            env_table["DESIGN_SPECS_DIR"] = out_dir
            entry["env"] = env_table

            mcp_table["web_design_extractor"] = entry

            cfg_path.write_text(tomlkit.dumps(doc), encoding="utf-8")
            return True, f"Registrado exitosamente en {cfg_path}"
        except Exception as e:
            return False, f"Error al registrar en Codex: {str(e)}"

    else:
        try:
            doc = {}
            if cfg_path.exists():
                text = cfg_path.read_text(encoding="utf-8-sig").strip()
                if text:
                    doc = json.loads(text)

            key = "servers" if agent_id == "vscode" else "mcpServers"
            if key not in doc or not isinstance(doc[key], dict):
                doc[key] = {}

            server_config = {
                "command": python_path,
                "args": [cli_path, "serve"],
                "env": {
                    "DESIGN_SPECS_DIR": out_dir
                }
            }

            if agent_id == "vscode":
                server_config["type"] = "stdio"

            doc[key]["web-design-extractor"] = server_config
            cfg_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return True, f"Registrado exitosamente en {cfg_path}"
        except Exception as e:
            return False, f"Error al registrar en {agent_id}: {str(e)}"


def register_all_detected_agents() -> Dict[str, Tuple[bool, str]]:
    """Registers in all agents that are detected on the machine."""
    agents = detect_all_agents()
    results = {}
    for aid, info in agents.items():
        if info.is_installed:
            success, msg = register_agent(aid)
            results[aid] = (success, msg)
    return results

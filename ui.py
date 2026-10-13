"""
Visual Terminal Identity and UI Dashboard for Web Design Extractor MCP.
Uses Rich to render high-contrast, beautiful terminal panels, status, and guides.
"""

import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

console = Console(highlight=False)

CYAN_GRADIENT = ("#38bdf8", "#0284c7", "#2563eb", "#4f46e5", "#7c3aed")

LOGO_LINES = [
    "  ___  ___ ___ ___ ___ _  _   _____  _______ ___    _   ___ _____ ___  ___  ",
    " |   \\| __/ __|_ _/ __| \\| | | __\\ \\/ |_   _| _ \\  /_\\ / __|_   _/ _ \\| _ \\ ",
    " | |) | _|\\__ \\| | (_ | .` | | _| >  <  | | |   / / _ \\ (__  | || (_) |   / ",
    " |___/|___|___/___\\___|_|\\_| |___/_/\\_\\ |_| |_|_\\/_/ \\_\\___| |_| \\___/|_|_\\ "
]


def render_logo() -> Text:
    """Renders styled gradient ASCII logo."""
    t = Text()
    for i, line in enumerate(LOGO_LINES):
        color = CYAN_GRADIENT[i % len(CYAN_GRADIENT)]
        t.append(line + "\n", style=f"bold {color}")
    return t


def show_dashboard(output_dir: Path, mcp_status: bool = True) -> None:
    """Displays the main terminal overview and status dashboard."""
    console.print()
    console.print(render_logo())

    # 1. Status Grid Table
    status_table = Table(box=box.ROUNDED, expand=True, border_style="#0284c7")
    status_table.add_column("COMPONENTE", style="bold white", width=24)
    status_table.add_column("ESTADO", style="bold", width=18)
    status_table.add_column("DETALLE / RUTA", style="dim white")

    # Storage path
    status_table.add_row(
        "Carpeta de Destino",
        "[green][OK] Activa[/green]",
        f"[cyan]{output_dir}[/cyan]"
    )

    # Playwright Chromium
    status_table.add_row(
        "Navegador Headless",
        "[green][OK] Listo[/green]",
        "Playwright Chromium v1.63 (Modo Headless)"
    )

    # Antigravity MCP integration
    mcp_label = "[green][OK] Registrado[/green]" if mcp_status else "[yellow][!] No detectado[/yellow]"
    status_table.add_row(
        "Servidor MCP Global",
        mcp_label,
        "~/.gemini/config/mcp_config.json ('web-design-extractor')"
    )

    console.print(Panel(
        status_table,
        title="[bold #38bdf8] ESTADO DEL SISTEMA [/bold #38bdf8]",
        border_style="#0284c7",
        box=box.ROUNDED
    ))

    # 2. Quick Instructions Panel
    instructions = Text()
    instructions.append("  1. Uso con Agentes de IA (Claude, Cursor, Gemini, Antigravity):\n", style="bold #38bdf8")
    instructions.append("     Simplemente escribe en tu chat:\n", style="dim")
    instructions.append("     \"Extrae el sistema de diseño de https://sitio.com\"\n", style="bold yellow")
    instructions.append("     El agente llamará automáticamente a la herramienta extract_design_system.\n\n", style="dim")

    instructions.append("  2. ¿Qué archivos se generan automáticamente?\n", style="bold #38bdf8")
    instructions.append("     - Archivo Markdown: ", style="bold white")
    instructions.append("<dominio>_design_spec.md (tokens, tipografía, divs, prompt maestro)\n", style="dim")
    instructions.append("     - Captura visual:   ", style="bold white")
    instructions.append("<dominio>_preview.png (captura completa en alta resolución)\n", style="dim")
    instructions.append(f"     Ambos se guardan de forma permanente en tu carpeta configurada.\n", style="italic green")

    console.print(Panel(
        instructions,
        title="[bold #38bdf8] GUÍA RÁPIDA DE USO [/bold #38bdf8]",
        border_style="#4f46e5",
        box=box.ROUNDED
    ))


def show_menu() -> str:
    """Displays interactive numbered menu and prompts for choice."""
    console.print()
    menu_table = Table(box=box.SIMPLE, show_header=False, expand=True)
    menu_table.add_column("Num", style="bold #fbc43f", width=5)
    menu_table.add_column("Acción", style="white")

    menu_table.add_row("[1]", "Cambiar carpeta de guardado de especificaciones (.md y .png)")
    menu_table.add_row("[2]", "Probar análisis de una web en vivo ahora mismo")
    menu_table.add_row("[3]", "Abrir carpeta de destino en el Explorador de Windows")
    menu_table.add_row("[4]", "Ver guía de prompts y ejemplos para pasarle a tu agente")
    menu_table.add_row("[5]", "Verificar estado de configuración en mcp_config.json")
    menu_table.add_row("[0]", "Salir")

    console.print(Panel(
        menu_table,
        title="[bold white] MENÚ DE CONFIGURACIÓN Y PRUEBAS [/bold white]",
        border_style="#64748b",
        box=box.ROUNDED
    ))

    choice = console.input("[bold #38bdf8]Selecciona una opción [0-5]: [/bold #38bdf8]").strip()
    return choice

"""
Visual Terminal Identity and UI Dashboard for Web Design Extractor MCP.
Uses Rich to render high-contrast, beautiful terminal panels, status, and guides.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

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
    " |___/|___|___/___\___|_|\_| |___/_/\\_\\ |_| |_|_\\/_/ \\_\\___| |_| \\___/|_|_\\ "
]


def render_logo() -> Text:
    """Renders styled gradient ASCII logo."""
    t = Text()
    for i, line in enumerate(LOGO_LINES):
        color = CYAN_GRADIENT[i % len(CYAN_GRADIENT)]
        t.append(line + "\n", style=f"bold {color}")
    return t


def show_dashboard(output_dir: Path, agents_status: Dict[str, Any]) -> None:
    """Displays the main terminal overview, agent detection status, and quick guide."""
    console.print()
    console.print(render_logo())

    # 1. System Status Table
    status_table = Table(box=box.ROUNDED, expand=True, border_style="#0284c7")
    status_table.add_column("SISTEMA BASE", style="bold white", width=22)
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
        "Playwright Chromium (Modo Headless)"
    )

    # PATH command integration
    from path_installer import is_path_installed
    if is_path_installed():
        status_table.add_row(
            "Comando Global (PATH)",
            "[green][OK] Instalado[/green]",
            "[green]Ejecutable como 'design-extractor' desde cualquier terminal[/green]"
        )
    else:
        status_table.add_row(
            "Comando Global (PATH)",
            "[yellow][!] No vinculado[/yellow]",
            "[dim]Ejecuta 'design-extractor path install' o usa la opción del menú[/dim]"
        )

    # Custom commands / Presets
    from preset_manager import get_all_presets
    presets = get_all_presets()
    preset_names = ", ".join(presets.keys())
    status_table.add_row(
        "Comandos / Presets",
        f"[cyan]{len(presets)} listos[/cyan]",
        f"[dim white]{preset_names}[/dim white]"
    )

    console.print(Panel(
        status_table,
        title="[bold #38bdf8] ESTADO DEL MOTOR DE EXTRACCIÓN [/bold #38bdf8]",
        border_style="#0284c7",
        box=box.ROUNDED
    ))

    # 2. Detected Agents Table
    agents_table = Table(box=box.ROUNDED, expand=True, border_style="#2563eb")
    agents_table.add_column("CLIENTE / CLI", style="bold white", width=28)
    agents_table.add_column("DETECCIÓN LOCAL", style="bold", width=22)
    agents_table.add_column("VINCULACIÓN MCP", style="bold", width=20)
    agents_table.add_column("ARCHIVO DE CONFIGURACIÓN", style="dim white")

    for aid, info in agents_status.items():
        if info.is_installed:
            inst_label = "[green][OK] Instalado[/green]"
        else:
            inst_label = "[dim red][-] No detectado[/dim red]"

        if info.is_configured:
            mcp_label = "[green][OK] Vinculado[/green]"
        elif info.is_installed:
            mcp_label = "[yellow][!] Pendiente[/yellow]"
        else:
            mcp_label = "[dim]N/A[/dim]"

        agents_table.add_row(
            info.name,
            inst_label,
            mcp_label,
            str(info.config_path.name)
        )

    console.print(Panel(
        agents_table,
        title="[bold #38bdf8] CLIENTES, IDES Y CLIs DE IA DETECTADOS [/bold #38bdf8]",
        border_style="#2563eb",
        box=box.ROUNDED
    ))

    # 3. Quick Instructions Panel
    instructions = Text()
    instructions.append("  1. ¿Cómo pedirle a tu IA que use el MCP en cualquier terminal?\n", style="bold #38bdf8")
    instructions.append("     Simplemente escribe en tu prompt:\n", style="dim")
    instructions.append("     \"Extrae el sistema de diseño de https://sitio.com\"\n", style="bold yellow")
    instructions.append("     La CLI/Agente llamará automáticamente a la herramienta extract_design_system.\n\n", style="dim")

    instructions.append("  2. ¿Qué archivos se generan en cada consulta?\n", style="bold #38bdf8")
    instructions.append("     - Especificación: ", style="bold white")
    instructions.append("<dominio>_design_spec.md (tokens, tipografía, divs, directivas maestras)\n", style="dim")
    instructions.append("     - Captura visual:  ", style="bold white")
    instructions.append("<dominio>_preview.png (captura completa en alta resolución)\n", style="dim")
    instructions.append(f"     Ambos se guardan de forma permanente en: {output_dir}\n", style="italic green")

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
    menu_table.add_row("[2]", "Vincular automáticamente en todos los clientes y CLIs detectadas")
    menu_table.add_row("[3]", "Probar análisis de una web en vivo ahora mismo")
    menu_table.add_row("[4]", "Abrir carpeta de destino en el Explorador de Windows")
    menu_table.add_row("[5]", "Instalar o verificar comando global en PATH (design-extractor)")
    menu_table.add_row("[6]", "Administrar comandos personalizados y presets de flujo de trabajo")
    menu_table.add_row("[7]", "Ver guía de prompts y ejemplos para pasarle a tu agente")
    menu_table.add_row("[0]", "Salir")

    console.print(Panel(
        menu_table,
        title="[bold white] MENÚ DE CONFIGURACIÓN Y ACCIONES [/bold white]",
        border_style="#64748b",
        box=box.ROUNDED
    ))

    choice = console.input("[bold #38bdf8]Selecciona una opción [0-7]: [/bold #38bdf8]").strip()
    return choice


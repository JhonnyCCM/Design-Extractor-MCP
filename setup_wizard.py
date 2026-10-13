"""
Interactive Setup Wizard and Testing Console for Web Design Extractor MCP.
Allows configuring storage directories, testing extractions with visual spinners,
and viewing agent instruction templates directly inside the terminal.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from config_manager import get_configured_output_dir, set_configured_output_dir
from core_extractor import extract_page_design_data, generate_agent_design_spec, take_screenshot
from server import _url_to_slug
from ui import console, show_dashboard, show_menu

MCP_CONFIG_PATH = Path.home() / ".gemini" / "config" / "mcp_config.json"


def is_mcp_registered() -> bool:
    """Checks if web-design-extractor is present in mcp_config.json."""
    if not MCP_CONFIG_PATH.exists():
        return False
    try:
        data = json.loads(MCP_CONFIG_PATH.read_text(encoding="utf-8"))
        return "web-design-extractor" in data.get("mcpServers", {})
    except Exception:
        return False


def sync_mcp_config_env(new_dir: str) -> None:
    """Synchronizes the DESIGN_SPECS_DIR in mcp_config.json if the file exists."""
    if not MCP_CONFIG_PATH.exists():
        return
    try:
        data = json.loads(MCP_CONFIG_PATH.read_text(encoding="utf-8"))
        if "web-design-extractor" in data.get("mcpServers", {}):
            server_entry = data["mcpServers"]["web-design-extractor"]
            if "env" not in server_entry:
                server_entry["env"] = {}
            server_entry["env"]["DESIGN_SPECS_DIR"] = new_dir
            MCP_CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


def handle_change_directory() -> None:
    """Interactively prompts user to enter a new output directory."""
    current = get_configured_output_dir()
    console.print()
    console.print(f"[bold white]Carpeta actual:[/bold white] [cyan]{current}[/cyan]")
    console.print("[dim]Introduce la ruta absoluta donde deseas guardar las hojas .md y capturas .png[/dim]")
    new_path = console.input("[bold #38bdf8]Nueva ruta (Presiona Enter para mantener la actual): [/bold #38bdf8]").strip()

    if not new_path:
        console.print("[yellow]No se realizaron cambios.[/yellow]")
        return

    try:
        resolved = set_configured_output_dir(new_path)
        sync_mcp_config_env(resolved)
        console.print(f"[green][OK] Carpeta actualizada exitosamente a:[/green] [bold cyan]{resolved}[/bold cyan]")
        console.print("[dim][OK] Sincronizado en config.json y ~/.gemini/config/mcp_config.json[/dim]")
    except Exception as e:
        console.print(f"[red]Error al configurar ruta: {str(e)}[/red]")


def handle_test_extraction() -> None:
    """Runs a live webpage analysis with Rich spinner and summary table."""
    console.print()
    url = console.input("[bold #38bdf8]Introduce la URL para analizar (ej. https://stripe.com): [/bold #38bdf8]").strip()

    if not url:
        console.print("[yellow]Operación cancelada.[/yellow]")
        return

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    out_dir = get_configured_output_dir()
    slug = _url_to_slug(url)
    target_md = out_dir / f"{slug}_design_spec.md"
    target_png = out_dir / f"{slug}_preview.png"

    try:
        with console.status(f"[bold #38bdf8]Iniciando navegador Chromium y analizando {url}...[/bold #38bdf8]", spinner="dots"):
            data = extract_page_design_data(url)
            spec_md = generate_agent_design_spec(data, url)
            target_md.write_text(spec_md, encoding="utf-8")
            take_screenshot(url, str(target_png), full_page=True)

        console.print("[green][OK] Extracción completada con éxito![/green]")

        # Summary Table
        summary_table = Table(box=box.ROUNDED, expand=True, border_style="#38bdf8")
        summary_table.add_column("PROPIEDAD", style="bold white", width=22)
        summary_table.add_column("VALOR EXTRAÍDO", style="cyan")

        summary_table.add_row("Título de Página", data.get("title", "N/A"))
        summary_table.add_row("Tema Detectado", "Modo Oscuro (Dark)" if data.get("isDark") else "Modo Claro (Light)")
        summary_table.add_row("Fondo Canvas", data.get("bodyBg", "N/A"))
        summary_table.add_row("Fuente de Títulos", (data.get("typography", {}).get("h1") or {}).get("fontFamily", "Inter"))
        summary_table.add_row("Tech Stack / Frameworks", ", ".join(data.get("techStack", [])) or "Custom HTML/CSS")
        summary_table.add_row("Archivo Markdown", str(target_md))
        summary_table.add_row("Captura PNG", str(target_png))

        console.print(Panel(summary_table, title="[bold #38bdf8] RESUMEN DE LA EXTRACCIÓN [/bold #38bdf8]", box=box.ROUNDED))

        # Ask to open
        ask_open = console.input("[bold #fbc43f]¿Deseas abrir la carpeta de destino en el Explorador? [S/n]: [/bold #fbc43f]").strip().lower()
        if ask_open in ["", "s", "si", "y", "yes"]:
            handle_open_folder()

    except Exception as e:
        console.print(f"[red]Error durante la extracción: {str(e)}[/red]")


def handle_open_folder() -> None:
    """Opens target output directory in Windows File Explorer."""
    out_dir = get_configured_output_dir()
    try:
        subprocess.run(["explorer", str(out_dir)], check=False)
        console.print(f"[green][OK] Abriendo Explorador en:[/green] [cyan]{out_dir}[/cyan]")
    except Exception as e:
        console.print(f"[red]No se pudo abrir el explorador: {str(e)}[/red]")


def handle_view_agent_guide() -> None:
    """Shows the agent prompt guide."""
    guide = Text()
    guide.append("¿Cómo usar las hojas de especificación con otros agentes?\n\n", style="bold #38bdf8")
    guide.append("1. Localiza el archivo .md generado en tu carpeta de especificaciones.\n", style="white")
    guide.append("2. Abre el archivo y copia la sección final:\n", style="white")
    guide.append("   '### AGENT MASTER DIRECTIVES: DESIGN FIDELITY RULES'\n\n", style="bold yellow")
    guide.append("3. Pega ese bloque en el prompt de tu agente (Cursor, Gemini, Claude, etc.) junto con tu requerimiento:\n", style="white")
    guide.append("   Ejemplo: 'Construye un dashboard de finanzas siguiendo estrictamente las directivas de este sistema de diseño [pegar directivas]'\n\n", style="dim")
    guide.append("4. El agente respetará la paleta exacta, las fuentes, radios de 18px o 6px, y la estructura de divs.\n", style="green")

    console.print(Panel(guide, title="[bold white] GUÍA DE PROMPTS PARA AGENTES [/bold white]", box=box.ROUNDED, border_style="#4f46e5"))


def handle_check_mcp_config() -> None:
    """Inspects and displays mcp_config.json configuration."""
    console.print()
    if not MCP_CONFIG_PATH.exists():
        console.print(f"[red]No se encontró el archivo {MCP_CONFIG_PATH}[/red]")
        return

    try:
        data = json.loads(MCP_CONFIG_PATH.read_text(encoding="utf-8"))
        cfg = data.get("mcpServers", {}).get("web-design-extractor")
        if cfg:
            console.print("[green][OK] Servidor 'web-design-extractor' registrado correctamente:[/green]")
            console.print(Panel(json.dumps(cfg, indent=2), title="[bold cyan] mcp_config.json [/bold cyan]", box=box.ROUNDED))
        else:
            console.print("[yellow]! El servidor no está registrado en mcpServers.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error al leer mcp_config.json: {str(e)}[/red]")


def run_wizard() -> None:
    """Main interactive wizard loop."""
    while True:
        output_dir = get_configured_output_dir()
        mcp_ok = is_mcp_registered()
        show_dashboard(output_dir, mcp_ok)
        choice = show_menu()

        if choice == "1":
            handle_change_directory()
        elif choice == "2":
            handle_test_extraction()
        elif choice == "3":
            handle_open_folder()
        elif choice == "4":
            handle_view_agent_guide()
        elif choice == "5":
            handle_check_mcp_config()
        elif choice in ["0", "q", "exit", "salir"]:
            console.print("\n[bold green]¡Hasta pronto! Que disfrutes construyendo grandes interfaces.[/bold green]\n")
            break
        else:
            console.print("[red]Opción no válida. Elige un número del 0 al 5.[/red]")

        console.input("\n[dim]Presiona Enter para continuar...[/dim]")


if __name__ == "__main__":
    run_wizard()

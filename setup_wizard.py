"""
Interactive Setup Wizard and Testing Console for Web Design Extractor MCP.
Allows configuring storage directories, auto-registering into detected AI agents and CLIs,
and testing web extractions directly inside the terminal.
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
from agent_integrator import detect_all_agents, register_all_detected_agents, register_agent


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
        console.print(f"[green][OK] Carpeta actualizada exitosamente a:[/green] [bold cyan]{resolved}[/bold cyan]")
        
        # Sync configured agents
        console.print("[dim]Sincronizando la nueva ruta en las configuraciones de agentes detectados...[/dim]")
        register_all_detected_agents()
        console.print("[green][OK] Agentes actualizados con la nueva ruta de guardado.[/green]")
    except Exception as e:
        console.print(f"[red]Error al configurar ruta: {str(e)}[/red]")


def handle_register_all_agents() -> None:
    """Detects and registers the MCP server in all installed agents and CLIs."""
    console.print()
    with console.status("[bold #38bdf8]Detectando clientes y registrando servidor MCP...[/bold #38bdf8]", spinner="dots"):
        results = register_all_detected_agents()

    res_table = Table(box=box.ROUNDED, expand=True, border_style="#0284c7")
    res_table.add_column("CLIENTE / CLI", style="bold white", width=28)
    res_table.add_column("RESULTADO", style="bold", width=18)
    res_table.add_column("DETALLE", style="dim white")

    agents = detect_all_agents()
    for aid, (success, msg) in results.items():
        name = agents[aid].name if aid in agents else aid
        status_str = "[green][OK] Vinculado[/green]" if success else "[red][X] Error[/red]"
        res_table.add_row(name, status_str, msg)

    console.print(Panel(
        res_table,
        title="[bold #38bdf8] VINCULACIÓN EN CLIENTES Y CLIs [/bold #38bdf8]",
        box=box.ROUNDED
    ))


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
    guide.append("¿Cómo pedirle a tu IA que use el MCP en cualquier terminal o IDE?\n\n", style="bold #38bdf8")
    guide.append("1. Si usas Antigravity, Codex CLI, Claude Desktop o Cursor:\n", style="white")
    guide.append("   Escribe directamente en tu chat:\n", style="dim")
    guide.append("   \"Extrae el sistema de diseño de https://sitio.com\"\n\n", style="bold yellow")
    guide.append("   El agente llamará automáticamente a la herramienta extract_design_system del servidor.\n\n", style="white")
    guide.append("2. Si quieres usar la especificación para construir una nueva web:\n", style="bold #38bdf8")
    guide.append("   Dile a tu agente:\n", style="dim")
    guide.append("   \"Usa la especificación generada de https://sitio.com y créame una web de [tu proyecto] aplicando exactamente sus colores, tipografías y estructura de contenedores.\"\n\n", style="bold green")
    guide.append("3. Todos los archivos se mantendrán sincronizados en tu carpeta centralizada de especificaciones.\n", style="italic")

    console.print(Panel(guide, title="[bold white] GUÍA DE PROMPTS PARA AGENTES [/bold white]", box=box.ROUNDED, border_style="#4f46e5"))


def run_wizard() -> None:
    """Main interactive wizard loop."""
    while True:
        output_dir = get_configured_output_dir()
        agents = detect_all_agents()
        show_dashboard(output_dir, agents)
        choice = show_menu()

        if choice == "1":
            handle_change_directory()
        elif choice == "2":
            handle_register_all_agents()
        elif choice == "3":
            handle_test_extraction()
        elif choice == "4":
            handle_open_folder()
        elif choice == "5":
            handle_view_agent_guide()
        elif choice in ["0", "q", "exit", "salir"]:
            console.print("\n[bold green]¡Hasta pronto! Que disfrutes construyendo grandes interfaces.[/bold green]\n")
            break
        else:
            console.print("[red]Opción no válida. Elige un número del 0 al 5.[/red]")

        console.input("\n[dim]Presiona Enter para continuar...[/dim]")


if __name__ == "__main__":
    run_wizard()

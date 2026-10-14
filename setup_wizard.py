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


def handle_path_integration() -> None:
    """Interactively manages global PATH integration for design-extractor."""
    from path_installer import is_path_installed, install_global_command, uninstall_global_command
    console.print()
    installed = is_path_installed()

    if installed:
        console.print("[green][OK] El comando global 'design-extractor' ya está instalado en tu PATH.[/green]")
        console.print("[dim]Puedes invocarlo directamente desde cualquier terminal (CMD, PowerShell, Bash, Git Bash).[/dim]")
        action = console.input("\n[bold #fbc43f]¿Deseas desinstalar el comando global de tu PATH? [s/N]: [/bold #fbc43f]").strip().lower()
        if action in ["s", "si", "y", "yes"]:
            ok, msg = uninstall_global_command()
            status = "[green][OK][/green]" if ok else "[red][ERROR][/red]"
            console.print(f"{status} {msg}")
    else:
        console.print("[yellow][!] El comando global 'design-extractor' aún no está vinculado en tu PATH.[/yellow]")
        console.print("[dim]Esto te permitirá usar 'design-extractor' sin escribir rutas a Python ni navegar a la carpeta del proyecto.[/dim]")
        action = console.input("\n[bold #38bdf8]¿Deseas instalar el comando global ahora? [S/n]: [/bold #38bdf8]").strip().lower()
        if action in ["", "s", "si", "y", "yes"]:
            ok, msg = install_global_command()
            status = "[green][OK][/green]" if ok else "[red][ERROR][/red]"
            console.print(f"{status} {msg}")


def handle_manage_presets() -> None:
    """Interactively manages workflow presets and custom commands."""
    from preset_manager import get_all_presets, create_or_update_preset, delete_preset, run_preset

    while True:
        console.print()
        presets = get_all_presets()

        p_table = Table(box=box.ROUNDED, expand=True, border_style="#38bdf8")
        p_table.add_column("COMANDO / PRESET", style="bold cyan", width=18)
        p_table.add_column("DESCRIPCIÓN", style="white", width=36)
        p_table.add_column("CAPTURA", style="bold", width=10)
        p_table.add_column("ESPERA (s)", style="bold", width=10)
        p_table.add_column("CARPETA DE SALIDA", style="dim white")

        for name, p_data in presets.items():
            shot = "[green]Sí[/green]" if p_data.get("screenshot", True) else "[dim red]No[/dim red]"
            wait = f"{p_data.get('wait_seconds', 2)}s"
            out = p_data.get("output_dir") or "[dim]Predeterminada global[/dim]"
            desc = p_data.get("description", "")
            p_table.add_row(name, desc, shot, wait, str(out))

        console.print(Panel(
            p_table,
            title="[bold #38bdf8] COMANDOS PERSONALIZADOS Y PRESETS DISPONIBLES [/bold #38bdf8]",
            box=box.ROUNDED
        ))

        console.print("[bold white]Opciones:[/bold white]")
        console.print("  [1] Ejecutar un preset sobre una URL ahora")
        console.print("  [2] Crear o editar un comando personalizado")
        console.print("  [3] Eliminar un comando personalizado")
        console.print("  [0] Volver al menú principal")

        opt = console.input("\n[bold #38bdf8]Elige una opción [0-3]: [/bold #38bdf8]").strip()

        if opt == "1":
            p_name = console.input("[bold #38bdf8]Nombre del preset a ejecutar (ej: quick, full): [/bold #38bdf8]").strip().lower()
            if p_name not in presets:
                console.print(f"[red]El preset '{p_name}' no existe.[/red]")
                continue
            url = console.input("[bold #38bdf8]URL de la página web a analizar: [/bold #38bdf8]").strip()
            if not url:
                console.print("[yellow]Operación cancelada.[/yellow]")
                continue
            try:
                with console.status(f"[bold #38bdf8]Ejecutando preset '{p_name}' sobre {url}...[/bold #38bdf8]", spinner="dots"):
                    res = run_preset(p_name, url)
                console.print(f"[green][OK] Extracción con preset '{p_name}' finalizada![/green]")
                console.print(f"  Markdown: [cyan]{res['spec_file']}[/cyan]")
                if res['preview_file']:
                    console.print(f"  Captura:  [cyan]{res['preview_file']}[/cyan]")
            except Exception as e:
                console.print(f"[red]Error al ejecutar preset: {str(e)}[/red]")

        elif opt == "2":
            p_name = console.input("[bold #38bdf8]Nombre para el comando (ej: landing, mobile): [/bold #38bdf8]").strip().lower()
            if not p_name:
                continue
            desc = console.input("[dim]Descripción del flujo: [/dim]").strip()
            out = console.input("[dim]Carpeta de salida personalizada (Enter para usar la global): [/dim]").strip()
            shot_str = console.input("[dim]¿Tomar captura de pantalla PNG? [S/n]: [/dim]").strip().lower()
            screenshot = shot_str not in ["n", "no", "false", "0"]
            wait_str = console.input("[dim]Segundos de espera para hidratación JS [1-15, default 2]: [/dim]").strip()
            try:
                wait_sec = int(wait_str) if wait_str else 2
            except ValueError:
                wait_sec = 2

            create_or_update_preset(
                name=p_name,
                description=desc,
                output_dir=out if out else None,
                screenshot=screenshot,
                wait_seconds=wait_sec
            )
            console.print(f"[green][OK] Comando personalizado '{p_name}' guardado exitosamente.[/green]")
            console.print(f"[dim]Ahora puedes invocarlo directamente en cualquier terminal:[/dim]")
            console.print(f"  [bold yellow]design-extractor {p_name} <url>[/bold yellow]")

        elif opt == "3":
            p_name = console.input("[bold #fbc43f]Nombre del comando a eliminar: [/bold #fbc43f]").strip().lower()
            if p_name in ["quick", "full"]:
                console.print(f"[yellow]El preset '{p_name}' es un valor por defecto del sistema y no puede eliminarse.[/yellow]")
            else:
                if delete_preset(p_name):
                    console.print(f"[green][OK] Comando '{p_name}' eliminado.[/green]")
                else:
                    console.print(f"[yellow]No se encontró el comando personalizado '{p_name}'.[/yellow]")

        elif opt in ["0", "q", "exit", "volver"]:
            break


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
            handle_path_integration()
        elif choice == "6":
            handle_manage_presets()
        elif choice == "7":
            handle_view_agent_guide()
        elif choice in ["0", "q", "exit", "salir"]:
            console.print("\n[bold green]¡Hasta pronto! Que disfrutes construyendo grandes interfaces.[/bold green]\n")
            break
        else:
            console.print("[red]Opción no válida. Elige un número del 0 al 7.[/red]")

        console.input("\n[dim]Presiona Enter para continuar...[/dim]")


if __name__ == "__main__":
    run_wizard()


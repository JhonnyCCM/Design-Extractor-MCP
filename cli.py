"""
Unified CLI Entry Point for Web Design Extractor MCP (design-extractor).
Supports:
  - 'setup' or 'run' (default): Interactive setup wizard like Moodle MCP
  - 'status': Display current configuration dashboard, detected agents, and PATH status
  - 'install-agents': Automatically configure all detected AI agents & CLIs
  - 'extract <url>': Run live extraction from command line
  - 'path {install,uninstall,status}': Manage global PATH command integration
  - 'custom {list,add,delete,run}': Manage or execute custom workflow presets
  - '<preset_name> <url>': Direct shortcut execution for any custom workflow
  - 'serve': Start the MCP server for an AI client
"""

import sys
import argparse
from pathlib import Path

from config_manager import get_configured_output_dir
from ui import show_dashboard, console
from setup_wizard import run_wizard
from agent_integrator import detect_all_agents, register_all_detected_agents
from path_installer import is_path_installed, install_global_command, uninstall_global_command
from preset_manager import get_all_presets, get_preset, create_or_update_preset, delete_preset, run_preset


def main():
    known_commands = {
        "setup", "run", "status", "install-agents", "serve",
        "extract", "path", "custom", "preset", "update", "self-update", "check-update",
        "-h", "--help"
    }


    # Direct shortcut for custom presets: e.g. design-extractor quick https://stripe.com
    if len(sys.argv) > 1 and sys.argv[1] not in known_commands and not sys.argv[1].startswith("-"):
        preset_name = sys.argv[1].lower()
        preset = get_preset(preset_name)
        if preset:
            shortcut_parser = argparse.ArgumentParser(
                prog=f"design-extractor {preset_name}",
                description=f"Ejecución directa del preset '{preset_name}': {preset.get('description', '')}"
            )
            shortcut_parser.add_argument("url", nargs="?", default=None, help="URL de la página web a analizar")
            shortcut_parser.add_argument("--url", dest="opt_url", default=None, help="URL alternativa")
            shortcut_parser.add_argument("-o", "--output", help="Carpeta o ruta de salida personalizada", default=None)
            s_args = shortcut_parser.parse_args(sys.argv[2:])

            target_url = s_args.opt_url or s_args.url
            if not target_url:
                shortcut_parser.error(f"Se requiere una URL para ejecutar el preset '{preset_name}'. Ej: design-extractor {preset_name} https://stripe.com")

            print(f"[*] Ejecutando flujo personalizado '{preset_name}' sobre {target_url}...")
            try:
                res = run_preset(preset_name, target_url, custom_output=s_args.output)
                print(f"[OK] Especificación Markdown guardada en: {res['spec_file']}")
                if res.get("preview_file"):
                    print(f"[OK] Captura de pantalla guardada en:   {res['preview_file']}")
            except Exception as e:
                print(f"[ERROR] Falló la ejecución del preset: {e}")
                sys.exit(1)
            return

    parser = argparse.ArgumentParser(
        prog="design-extractor",
        description="CLI y Servidor MCP para ingeniería inversa y extracción de sistemas de diseño web."
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Command: setup / run
    subparsers.add_parser("setup", help="Abrir pantalla interactiva de configuración y pruebas")
    subparsers.add_parser("run", help="Alias de setup")

    # Command: status
    subparsers.add_parser("status", help="Ver estado de componentes, PATH y clientes IA detectados")

    # Command: install-agents
    subparsers.add_parser("install-agents", help="Vincular automáticamente el servidor MCP en todas las CLIs detectadas")

    # Command: serve
    subparsers.add_parser("serve", help="Iniciar servidor MCP en modo stdio para clientes IA")

    # Command: extract
    extract_parser = subparsers.add_parser("extract", help="Extraer el diseño de una URL directamente")
    extract_parser.add_argument("url", help="URL a analizar (ej: https://stripe.com)")
    extract_parser.add_argument("-o", "--output", help="Ruta de guardado personalizada", default=None)

    # Command: path
    path_parser = subparsers.add_parser("path", help="Gestionar comando global en el PATH del sistema")
    path_sub = path_parser.add_subparsers(dest="path_action", help="Acción de PATH")
    path_sub.add_parser("install", help="Instalar comando global 'design-extractor' en el PATH")
    path_sub.add_parser("uninstall", help="Desinstalar comando global del PATH")
    path_sub.add_parser("status", help="Comprobar si 'design-extractor' está accesible en PATH")

    # Commands: custom / preset
    for cmd_alias in ["custom", "preset"]:
        custom_parser = subparsers.add_parser(cmd_alias, help="Gestionar o ejecutar flujos de trabajo personalizados")
        c_sub = custom_parser.add_subparsers(dest="custom_action", help="Acción sobre comandos personalizados")

        c_sub.add_parser("list", help="Listar todos los comandos personalizados y presets")

        c_add = c_sub.add_parser("add", help="Crear o actualizar un comando personalizado")
        c_add.add_argument("name", help="Nombre identificador (ej: landing, mobile)")
        c_add.add_argument("--desc", default="", help="Descripción del flujo de trabajo")
        c_add.add_argument("-o", "--output", default=None, help="Carpeta de salida predefinida para este comando")
        c_add.add_argument("--no-screenshot", action="store_true", help="Desactivar captura de pantalla PNG")
        c_add.add_argument("--wait", type=int, default=2, help="Segundos de espera para hidratación JS (default: 2)")

        c_del = c_sub.add_parser("delete", help="Eliminar un comando personalizado")
        c_del.add_argument("name", help="Nombre del comando a eliminar")

        c_run = c_sub.add_parser("run", help="Ejecutar un comando o preset personalizado")
        c_run.add_argument("name", help="Nombre del comando a ejecutar")
        c_run.add_argument("url", help="URL a analizar")
        c_run.add_argument("-o", "--output", default=None, help="Carpeta de salida personalizada")

    # Command: update / self-update
    update_parser = subparsers.add_parser("update", help="Actualizar Design Extractor automáticamente desde GitHub")
    update_parser.add_argument("--force", action="store_true", help="Forzar reinstalación aunque esté al día")
    subparsers.add_parser("self-update", help="Alias de update")

    # Command: check-update
    subparsers.add_parser("check-update", help="Comprobar si existen nuevas actualizaciones en GitHub sin instalarlas")

    args = parser.parse_args()


    if args.command in ["setup", "run"] or args.command is None:
        run_wizard()

    elif args.command == "status":
        output_dir = get_configured_output_dir()
        agents = detect_all_agents()
        show_dashboard(output_dir, agents)

    elif args.command == "install-agents":
        print("[*] Detectando clientes IA y registrando servidor MCP...")
        results = register_all_detected_agents()
        for aid, (ok, msg) in results.items():
            status = "[OK]" if ok else "[ERROR]"
            print(f" {status} {aid}: {msg}")

    elif args.command == "serve":
        from server import mcp
        mcp.run()

    elif args.command == "extract":
        from core_extractor import extract_page_design_data, generate_agent_design_spec, take_screenshot
        from server import _url_to_slug
        url = args.url
        out_dir = get_configured_output_dir()
        slug = _url_to_slug(url)
        target_md = Path(args.output).resolve() if args.output else out_dir / f"{slug}_design_spec.md"
        target_png = target_md.parent / f"{slug}_preview.png"

        print(f"[*] Analizando {url}...")
        data = extract_page_design_data(url)
        spec_md = generate_agent_design_spec(data, url)
        target_md.write_text(spec_md, encoding="utf-8")
        take_screenshot(url, str(target_png), full_page=True)
        print(f"[OK] Especificación guardada en: {target_md}")
        print(f"[OK] Captura guardada en: {target_png}")

    elif args.command == "path":
        action = args.path_action or "status"
        if action == "install":
            ok, msg = install_global_command()
            status = "[OK]" if ok else "[ERROR]"
            print(f"{status} {msg}")
        elif action == "uninstall":
            ok, msg = uninstall_global_command()
            status = "[OK]" if ok else "[ERROR]"
            print(f"{status} {msg}")
        elif action == "status":
            if is_path_installed():
                print("[OK] 'design-extractor' está instalado y accesible en tu PATH.")
            else:
                print("[!] 'design-extractor' NO está en el PATH. Ejecuta 'design-extractor path install' para instalarlo.")

    elif args.command in ["custom", "preset"]:
        action = args.custom_action or "list"
        if action == "list":
            presets = get_all_presets()
            print("\n=== COMANDOS PERSONALIZADOS Y PRESETS DISPONIBLES ===")
            for name, p in presets.items():
                shot = "Sí" if p.get("screenshot", True) else "No"
                wait = f"{p.get('wait_seconds', 2)}s"
                out = p.get("output_dir") or "(Directorio global predeterminado)"
                desc = p.get("description", "")
                print(f" • {name}:")
                print(f"     Descripción: {desc}")
                print(f"     Captura: {shot} | Espera: {wait} | Salida: {out}")
                print(f"     Uso directo: design-extractor {name} <url>\n")

        elif action == "add":
            created = create_or_update_preset(
                name=args.name,
                description=args.desc,
                output_dir=args.output,
                screenshot=not args.no_screenshot,
                wait_seconds=args.wait
            )
            print(f"[OK] Comando personalizado '{args.name}' registrado exitosamente.")
            print(f"     Puedes ejecutarlo directamente con: design-extractor {args.name} <url>")

        elif action == "delete":
            if args.name in ["quick", "full"]:
                print(f"[!] El preset '{args.name}' es parte del sistema y no puede eliminarse.")
            else:
                if delete_preset(args.name):
                    print(f"[OK] Comando personalizado '{args.name}' eliminado.")
                else:
                    print(f"[!] No se encontró el comando '{args.name}'.")

        elif action == "run":
            print(f"[*] Ejecutando preset '{args.name}' sobre {args.url}...")
            try:
                res = run_preset(args.name, args.url, custom_output=args.output)
                print(f"[OK] Especificación Markdown: {res['spec_file']}")
                if res.get("preview_file"):
                    print(f"[OK] Captura de pantalla:   {res['preview_file']}")
            except Exception as e:
                print(f"[ERROR] {e}")
                sys.exit(1)

    elif args.command in ["update", "self-update"]:
        from updater import apply_update, check_for_updates
        print("[*] Comprobando actualizaciones en GitHub...")
        has_update, msg, remote_id = check_for_updates(force=True)
        if not has_update and not getattr(args, "force", False):
            print(f"[OK] {msg}")
        else:
            print(f"[*] {msg}")
            print("[*] Descargando cambios e instalando dependencias...")
            ok, update_msg = apply_update()
            status = "[OK]" if ok else "[ERROR]"
            print(f"{status} {update_msg}")

    elif args.command == "check-update":
        from updater import check_for_updates
        print("[*] Comprobando actualizaciones en GitHub...")
        has_update, msg, remote_id = check_for_updates(force=True)
        status = "[!]" if has_update else "[OK]"
        print(f"{status} {msg}")


if __name__ == "__main__":
    main()


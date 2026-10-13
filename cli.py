"""
Unified CLI Entry Point for Web Design Extractor MCP.
Supports:
  - 'setup' or 'run' (default): Interactive setup wizard like Moodle MCP
  - 'status': Display current configuration dashboard and detected agents
  - 'install-agents': Automatically configure all detected AI agents & CLIs
  - 'extract <url>': Run live extraction from command line
  - 'serve': Start the MCP server for an AI client
"""

import sys
import argparse
from pathlib import Path

from config_manager import get_configured_output_dir
from ui import show_dashboard
from setup_wizard import run_wizard
from agent_integrator import detect_all_agents, register_all_detected_agents


def main():
    parser = argparse.ArgumentParser(
        prog="web-design-extractor",
        description="CLI y Servidor MCP para ingeniería inversa y extracción de sistemas de diseño web."
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Command: setup / run
    subparsers.add_parser("setup", help="Abrir pantalla interactiva de configuración y pruebas (estilo Moodle MCP)")
    subparsers.add_parser("run", help="Alias de setup")

    # Command: status
    subparsers.add_parser("status", help="Ver estado de componentes y clientes IA detectados")

    # Command: install-agents
    subparsers.add_parser("install-agents", help="Vincular automáticamente el servidor MCP en todas las CLIs detectadas")

    # Command: serve
    subparsers.add_parser("serve", help="Iniciar servidor MCP en modo stdio para clientes IA")

    # Command: extract
    extract_parser = subparsers.add_parser("extract", help="Extraer el diseño de una URL directamente")
    extract_parser.add_argument("url", help="URL a analizar (ej: https://stripe.com)")
    extract_parser.add_argument("-o", "--output", help="Ruta de guardado personalizada", default=None)

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
        print(f"[+] Especificación guardada en: {target_md}")
        print(f"[+] Captura guardada en: {target_png}")


if __name__ == "__main__":
    main()

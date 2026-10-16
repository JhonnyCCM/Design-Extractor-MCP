# Design Extractor MCP 🌐✨
> **Model Context Protocol (MCP) Server & CLI para ingeniería inversa de sistemas de diseño, estructuras de contenedores, tokens W3C DTCG, temas Shadcn UI, Tailwind v4 y directivas para Agentes de IA.**

[![MCP Standard](https://img.shields.io/badge/MCP-Protocol%201.0-blue.svg)](https://modelcontextprotocol.io)
[![Version](https://img.shields.io/badge/Version-1.4.0-brightgreen.svg)](https://github.com/JhonnyCCM/Design-Extractor-MCP)
[![CI Tests](https://img.shields.io/badge/CI-Passing-brightgreen.svg)](https://github.com/JhonnyCCM/Design-Extractor-MCP/actions)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://python.org)
[![Playwright](https://img.shields.io/badge/Engine-Playwright%20Chromium-orange.svg)](https://playwright.dev)
[![W3C DTCG](https://img.shields.io/badge/Tokens-W3C%20DTCG%20Standard-purple.svg)](https://design-tokens.github.io/community-group/format/)
[![Shadcn UI](https://img.shields.io/badge/Themes-Shadcn%20UI%20(HSL)-black.svg)](https://ui.shadcn.com)
[![Tailwind CSS v4](https://img.shields.io/badge/Themes-Tailwind%20v4%20(@theme)-06B6D4.svg)](https://tailwindcss.com)

---

## ⚡ Instalación en Un Paso (One-Liner Installers)

### 🪟 Windows (PowerShell)
Abre PowerShell y ejecuta:
```powershell
irm https://raw.githubusercontent.com/JhonnyCCM/Design-Extractor-MCP/main/INSTALAR-WINDOWS.ps1 | iex
```
*O si ya clonaste el repositorio localmente:*
```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR-WINDOWS.ps1
```

### 🍎🐧 Linux & macOS (Bash)
```bash
curl -sSL https://raw.githubusercontent.com/JhonnyCCM/Design-Extractor-MCP/main/install.sh | bash
```

El instalador automático:
1. Comprueba y valida Python 3.10+.
2. Crea el entorno virtual aislado `.venv`.
3. Instala todas las dependencias requeridas (`mcp`, `playwright`, `rich`, `pydantic`, `tomlkit`).
4. Descarga y verifica el motor Chromium headless de Playwright.
5. Registra el comando global `design-extractor` en tu terminal (PATH).
6. Auto-detecta y configura clientes IA locales (**Google Antigravity**, **Claude Desktop**, **Cursor**, **Windsurf**, **VS Code**).

---

## 🎯 ¿Qué hace este proyecto?

**Design Extractor MCP** es un motor integral de ingeniería inversa que navega cualquier página web en tiempo real usando un navegador headless (Playwright) para inspeccionar tanto el código fuente como los estilos computados del DOM.

En cada extracción genera y emite **5 artefactos de producción atómicos**:
1. 📄 **`{slug}_design_spec.md`**: Especificación completa en Markdown con directivas maestras para Agentes de IA.
2. 💎 **`{slug}_design_tokens.json`**: Tokens de diseño estándar **W3C DTCG** (Design Tokens Community Group) para Figma y Style Dictionary.
3. 🎨 **`{slug}_shadcn_globals.css`**: Hoja de estilos con variables HSL completas para `:root` (Light) y `.dark` (Dark mode) lista para proyectos Shadcn UI / Radix.
4. ⚡ **`{slug}_tailwind_v4.css`**: Configuración moderna CSS-first con la directiva `@theme` para **Tailwind CSS v4**.
5. 📸 **`{slug}_preview.png`**: Captura de pantalla completa en alta resolución para referencia visual y multimodal.

### Capacidades Destacadas:
- **🎨 Paleta y Tokens de Color:** Fondos de canvas, superficies/tarjetas, colores de texto (alto contraste y atenuado), acento de marca y bordes, con normalización automática a HEX/RGBA.
- **🌓 Probeta Dual-Theme (Modo Claro & Oscuro):** Emula automáticamente `prefers-color-scheme: dark` e inspecciona clases `.dark` o `data-theme` para sincronizar tokens semánticos en ambos modos.
- **♿ Auditoría de Accesibilidad WCAG 2.1:** Cálculo matemático de luminancia relativa y contrast ratios de color (niveles AA / AAA) entre pares de texto y fondo.
- **📱 Matriz Responsiva Multi-Viewport:** Probeta activa en vivo probando Desktop (1440px), Tablet (768px) y Mobile (375px), detectando la transformación de títulos, padding, comportamiento de grid y menús hamburguesa.
- **🖼️ Activos de Marca y Gráficos Vectoriales:** Extracción de favicons, logotipos SVG completos (outerHTML) y conteo de vectores en pantalla.
- **🔤 Sistema Tipográfico y Fuentes Web:** Jerarquía exacta (**H1, H2, H3 y Párrafos**) con tamaños, pesos, interlineados, tracking y snippets de importación de Google Fonts / `@font-face`.
- **📐 Arquitectura de Layout y Divs:** Anchuras máximas de contenedor (`max-w-*`), espaciado rítmico (`py-16`), y esqueletos estructurales HTML limpios de **Header**, **Hero**, **Cards** y **Botones**.
- **🔐 Soporte de Sesiones Autenticadas (Moodle, SaaS, SSO):** Grabador interactivo de login (`design-extractor login <url>`) y soporte de cookies (`--cookie`) para auditar plataformas que requieren usuario y contraseña.
- **🤖 Prompt Maestro para Agentes (Master Directives):** Genera una hoja de instrucciones exhaustiva en Markdown (`.md`) lista para copiar y pegar a cualquier Agente de IA para replicar el diseño.

---

## 🔌 Compatibilidad Universal con Agentes de IA

Este servidor sigue el estándar abierto **Model Context Protocol (MCP)** mediante transporte estándar `stdio`. **Es 100% compatible con cualquier cliente, IDE o CLI de IA que soporte MCP:**

### 1. Google Antigravity / Gemini CLI
En tu archivo de configuración global `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "web-design-extractor": {
      "command": "C:\\ruta\\a\\tu\\entorno\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\ruta\\a\\web-design-extractor-mcp\\cli.py",
        "serve"
      ],
      "env": {
        "DESIGN_SPECS_DIR": "C:\\Users\\jonni\\Desktop\\MD instrucciones web"
      }
    }
  }
}
```

### 2. Claude Desktop / Claude Code CLI
En tu archivo `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "web-design-extractor": {
      "command": "python",
      "args": [
        "/ruta/absoluta/a/web-design-extractor-mcp/cli.py",
        "serve"
      ],
      "env": {
        "DESIGN_SPECS_DIR": "/ruta/a/tus/especificaciones"
      }
    }
  }
}
```

### 3. Cursor / Codex / Windsurf / VS Code (Roo-Code)
En el archivo de configuración de MCP (ejemplo `mcp.json` o settings de la extensión):

```json
{
  "mcpServers": {
    "web-design-extractor": {
      "command": "python",
      "args": ["/ruta/a/web-design-extractor-mcp/cli.py", "serve"],
      "env": {
        "DESIGN_SPECS_DIR": "/ruta/a/tus/especificaciones"
      }
    }
  }
}
```

---

## 💻 Uso Directo en Terminal (Comando Global `design-extractor`)

Puedes ejecutar `design-extractor` de forma global desde cualquier carpeta de tu terminal sin necesidad de escribir rutas complejas a Python:

```bash
# 1. Comprobar estado e integración en PATH:
design-extractor status

# 2. Abrir asistente interactivo de configuración y dashboard TUI:
design-extractor setup

# 3. Extraer una web pública (emite .md, tokens .json, Shadcn .css, Tailwind v4 .css y preview .png):
design-extractor extract https://stripe.com

# 4. Iniciar sesión interactiva en una web protegida (Moodle, SaaS, SSO):
design-extractor login https://moodle.miuniversidad.edu/login/index.php -o auth.json

# 5. Extraer una página privada usando la sesión guardada:
design-extractor extract https://moodle.miuniversidad.edu/mod/assign/view.php?id=123 -s auth.json

# 6. O pasar la cookie de sesión directamente:
design-extractor extract https://moodle.miuniversidad.edu/my -c "MoodleSession=abc123xyz"

# 7. Vincular automáticamente con todos los clientes IA detectados:
design-extractor install-agents

# 8. Comprobar o descargar actualizaciones automáticas:
design-extractor check-update
design-extractor update
```

---

## 🔄 Auto-Update y Actualizaciones

Design Extractor incluye un motor de auto-actualización inteligente que consulta el repositorio oficial en GitHub y actualiza el código, dependencias y shims en un solo paso:

```bash
# Comprobar si hay actualizaciones disponibles:
design-extractor check-update

# Descargar e instalar la última versión desde GitHub:
design-extractor update
```

*(También disponible de forma gráfica en la opción `[8]` del menú interactivo `design-extractor setup` o directamente mediante la herramienta MCP `update_server` para agentes de IA)*.

---

## ⚡ Comandos Personalizados y Flujos de Trabajo (Presets)

Design Extractor permite definir atajos y flujos de trabajo reutilizables con tiempos de hidratación, directorios personalizados y opciones de captura preconfiguradas:

### 1. Presets Nativos Incluidos:
- **`quick`**: Extracción ultrarrápida sin captura de pantalla (`screenshot=false`, espera de 1s).
  ```bash
  design-extractor quick https://stripe.com
  ```
- **`full`**: Extracción completa de alta fidelidad con captura de pantalla y espera prolongada para SPAs/Next.js (`screenshot=true`, espera de 4s).
  ```bash
  design-extractor full https://linear.app
  ```

### 2. Gestión de Comandos Personalizados:
```bash
# Listar todos los presets disponibles:
design-extractor custom list

# Crear un nuevo comando personalizado:
design-extractor custom add landing --desc "Flujo para landing pages interactivas" --wait 3

# Ejecutar tu comando recién creado directamente:
design-extractor landing https://supabase.com

# Eliminar un comando personalizado:
design-extractor custom delete landing
```

---

## 🛠️ Herramientas MCP Expuestas

Cuando un Agente de IA se conecta a este servidor, tiene acceso a las siguientes herramientas modulares:

| Herramienta | Parámetros | Descripción |
| :--- | :--- | :--- |
| **`extract_design_system`** | `url`, `output_file`, `storage_state`, `cookie` | Visita la web, extrae el sistema completo, emite todos los artefactos (`.md`, `.json`, `shadcn.css`, `tailwind_v4.css`, `.png`), y devuelve la especificación maestra. |
| **`extract_design_tokens`** | `url`, `output_file`, `storage_state`, `cookie` | Extrae y guarda tokens de diseño estándar W3C DTCG en formato JSON compatible con Figma y Style Dictionary. |
| **`generate_shadcn_theme`** | `url`, `storage_state`, `cookie` | Genera un archivo `globals.css` completo con variables HSL para `:root` y `.dark` listo para proyectos Shadcn UI. |
| **`generate_tailwind_v4_theme`** | `url`, `storage_state`, `cookie` | Genera la configuración moderna CSS-first con la directiva `@theme` para Tailwind CSS v4. |
| **`extract_brand_assets`** | `url`, `storage_state`, `cookie` | Extrae activos visuales de identidad: favicon, logotipo principal SVG y métricas de iconos vectoriales. |
| **`check_accessibility_audit`** | `url`, `storage_state`, `cookie` | Realiza una auditoría matemática de contraste WCAG 2.1 con ratios y niveles AA/AAA entre textos y fondos. |
| **`inspect_component`** | `url`, `selector`, `storage_state`, `cookie` | Inspecciona un elemento específico por selector CSS devolviendo sus dimensiones exactas, bordes y HTML. |
| **`generate_tailwind_theme`** | `url`, `storage_state`, `cookie` | Extrae los tokens de la página y devuelve un bloque listo para copiar en `tailwind.config.js` (Tailwind v3). |
| **`inspect_page_source`** | `url`, `storage_state`, `cookie` | Realiza auditoría del código fuente: frameworks detectados, breakpoints `@media` y clases de utilidad. |
| **`capture_page_screenshot`** | `url`, `output_path`, `storage_state`, `cookie` | Captura una imagen de alta resolución de la página completa. |
| **`set_output_directory`** | `path` | Actualiza y persiste la carpeta de guardado de los archivos. |
| **`get_output_directory`** | *(ninguno)* | Devuelve la ruta de la carpeta activa actual. |
| **`check_for_updates`** | *(ninguno)* | Comprueba si existe una versión más reciente en GitHub. |
| **`update_server`** | *(ninguno)* | Descarga automáticamente la última versión desde GitHub y actualiza dependencias. |

---

## 📂 Estructura del Repositorio

```text
web-design-extractor-mcp/
├── .github/
│   ├── ISSUE_TEMPLATE/     # Plantillas oficiales para reporte de bugs y sugerencias
│   ├── workflows/ci.yml    # CI automático en Windows y Ubuntu con Python 3.10-3.12
│   └── PULL_REQUEST_TEMPLATE.md
├── tests/                  # Suite integral de pruebas unitarias
│   ├── __init__.py
│   ├── test_phase3.py
│   ├── test_phase4.py
│   └── test_project_structure.py
├── INSTALAR-WINDOWS.ps1    # Instalador automático en 1 clic para PowerShell
├── install.sh              # Instalador automático para Linux y macOS
├── cli.py                  # Punto de entrada unificado y ejecutor de comandos (design-extractor)
├── server.py               # Servidor MCP (FastMCP) con todas las herramientas expuestas
├── core_extractor.py       # Motor de análisis DOM, estilos computados y Playwright
├── setup_wizard.py         # Asistente interactivo de terminal estilo Moodle MCP
├── ui.py                   # Componentes visuales, tablas y dashboard renderizados con Rich
├── updater.py              # Motor de auto-actualización inteligente con GitHub
├── system_checker.py       # Auto-diagnóstico y auto-reparación de Playwright Chromium
├── storage.py              # Escritura atómica a prueba de fallos y caché con TTL
├── path_installer.py       # Integración global del comando en PATH (Windows/Linux/macOS)
├── preset_manager.py       # Gestor de flujos de trabajo personalizados y presets
├── config_manager.py       # Gestor de carpetas y persistencia de configuración
├── configurar.bat          # Lanzador rápido para terminal en Windows
├── pyproject.toml          # Especificación de empaquetado moderno y metadatos (v1.4.0)
├── requirements.txt        # Dependencias de producción
├── .editorconfig           # Estándar de formato para editores e IDEs
├── .gitignore              # Exclusiones seguras de Git (artefactos, auth, temporales)
├── CONTRIBUTING.md         # Guía de contribución para la comunidad
├── CODE_OF_CONDUCT.md      # Código de conducta (Contributor Covenant v2.1)
├── SECURITY.md             # Política de divulgación responsable de vulnerabilidades
├── LICENSE                 # Licencia oficial MIT
└── README.md               # Documentación y manual de uso
```

---

## 🧪 Pruebas Unitarias

Para ejecutar el suite de pruebas en tu máquina:
```bash
python -m unittest discover tests
```

---

## 🤝 Comunidad y Contribución

¡Las contribuciones son bienvenidas! Consulta nuestras guías comunitarias:
- [Guía de Contribución](CONTRIBUTING.md)
- [Código de Conducta](CODE_OF_CONDUCT.md)
- [Política de Seguridad](SECURITY.md)

---

## 📄 Licencia

Distribuido bajo la [Licencia MIT](LICENSE). Libre para uso personal, educativo y comercial.

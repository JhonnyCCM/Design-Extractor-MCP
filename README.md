# Design Extractor MCP 🌐✨
> **Model Context Protocol (MCP) Server & CLI para ingeniería inversa de sistemas de diseño, estructuras de contenedores, tokens W3C DTCG y directivas para Agentes de IA.**

[![MCP Standard](https://img.shields.io/badge/MCP-Protocol%201.0-blue.svg)](https://modelcontextprotocol.io)
[![Version](https://img.shields.io/badge/Version-1.3.0-brightgreen.svg)](https://github.com/JhonnyCCM/Design-Extractor-MCP)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://python.org)
[![Playwright](https://img.shields.io/badge/Engine-Playwright%20Chromium-orange.svg)](https://playwright.dev)
[![W3C DTCG](https://img.shields.io/badge/Tokens-W3C%20DTCG%20Standard-purple.svg)](https://design-tokens.github.io/community-group/format/)

---

## 🎯 ¿Qué hace este proyecto?

**Design Extractor MCP** es un motor de ingeniería inversa que navega cualquier página web en tiempo real usando un navegador headless (Playwright) para inspeccionar tanto el código fuente como los estilos computados del DOM.

Extrae automáticamente:
1. **🎨 Paleta y Tokens de Color:** Fondos de canvas, superficies/tarjetas, colores de texto (alto contraste y atenuado), acento de marca y bordes, con normalización automática a HEX/RGBA.
2. **🌓 Probeta Dual-Theme (Modo Claro & Oscuro):** Emula automáticamente `prefers-color-scheme: dark` e inspecciona clases `.dark` o `data-theme` para sincronizar tokens semánticos en ambos modos.
3. **♿ Auditoría de Accesibilidad WCAG 2.1:** Cálculo matemático de luminancia relativa y contrast ratios de color (niveles AA / AAA) entre pares de texto y fondo.
4. **📱 Matriz Responsiva Multi-Viewport:** Probeta activa en vivo probando Desktop (1440px), Tablet (768px) y Mobile (375px), detectando la transformación de títulos, padding, comportamiento de grid y menús hamburguesa.
5. **💎 Tokens W3C DTCG Estándar (`design-tokens.json`):** Exportación en el formato estándar de la W3C (*Design Tokens Community Group*), compatible directamente con Figma Tokens, Style Dictionary y Tailwind CSS.
6. **🔤 Sistema Tipográfico y Fuentes Web:** Jerarquía exacta (**H1, H2, H3 y Párrafos**) con tamaños, pesos, interlineados, tracking y snippets de importación de Google Fonts / `@font-face`.
7. **📐 Arquitectura de Layout y Divs:** Anchuras máximas de contenedor (`max-w-*`), espaciado rítmico (`py-16`), y esqueletos estructurales HTML limpios de **Header**, **Hero**, **Cards** y **Botones**.
8. **🔐 Soporte de Sesiones Autenticadas (Moodle, SaaS, SSO):** Grabador interactivo de login (`design-extractor login <url>`) y soporte de cookies (`--cookie`) para auditar plataformas que requieren usuario y contraseña.
9. **🤖 Prompt Maestro para Agentes (Master Directives):** Genera una hoja de instrucciones exhaustiva en Markdown (`.md`) lista para copiar y pegar a cualquier Agente de IA para replicar el diseño.
10. **📸 Capturas de Pantalla:** Captura automáticamente una imagen completa en alta resolución (`.png`) para referencia visual.

---

## 🔌 Compatibilidad Universal

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

### 4. Uso Directo en Terminal (Comando Global `design-extractor`)

Puedes ejecutar `design-extractor` de forma global desde cualquier carpeta de tu terminal sin necesidad de escribir rutas complejas a Python:

```bash
# 1. Comprobar estado e integración en PATH:
design-extractor status

# 2. Abrir asistente interactivo de configuración y dashboard:
design-extractor setup

# 3. Extraer una web pública y guardar .md, .json y .png:
design-extractor extract https://stripe.com

# 4. Iniciar sesión interactiva en una web protegida (Moodle, SaaS, SSO):
design-extractor login https://moodle.miuniversidad.edu/login/index.php -o auth.json

# 5. Extraer una página privada usando la sesión guardada:
design-extractor extract https://moodle.miuniversidad.edu/mod/assign/view.php?id=123 -s auth.json

# 6. O pasar la cookie de sesión directamente:
design-extractor extract https://moodle.miuniversidad.edu/my -c "MoodleSession=abc123xyz"

# 7. Vincular automáticamente con todos los clientes IA detectados:
design-extractor install-agents

# 8. Comprobar o descargar actualizaciones:
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

## 🌐 Integración en PATH del Sistema

Para tener el comando `design-extractor` disponible en cualquier terminal (PowerShell, CMD, Bash, Git Bash):

```bash
# Instalar shim global en tu PATH de usuario:
design-extractor path install

# Comprobar estado:
design-extractor path status

# O mediante pip editable:
pip install -e .
```
*(También puedes instalarlo interactivamente seleccionando la opción `[5]` en `design-extractor setup`)*.

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar el repositorio
```bash
git clone https://github.com/JhonnyCCM/Design-Extractor-MCP.git
cd Design-Extractor-MCP
```

### 2. Crear entorno virtual e instalar dependencias
En Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

En Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 3. Asistente Interactivo de Configuración
Para abrir la pantalla de configuración :

- **En Windows:** Haz doble clic en `configurar.bat` o ejecuta:
  ```powershell
  python cli.py setup
  ```
- **En Linux / Mac:**
  ```bash
  python3 cli.py setup
  ```

Desde este menú interactivo puedes:
- `[1]` Cambiar la carpeta permanente donde se guardan tus `.md`, `.json` y `.png`.
- `[2]` Vincular automáticamente en todos los clientes IA y CLIs detectadas.
- `[3]` Probar la extracción en vivo de cualquier URL (pública o autenticada).
- `[4]` Abrir la carpeta de destino en el Explorador de archivos de Windows.
- `[5]` Instalar o verificar comando global en PATH (`design-extractor`).
- `[6]` Administrar comandos personalizados y presets de flujo de trabajo.
- `[7]` Ver la guía de prompts y ejemplos para pasarle a tu agente de IA.
- `[8]` Buscar o instalar actualizaciones automáticas desde GitHub (Auto-Update).
- `[9]` Iniciar sesión interactiva en un sitio web y guardar credenciales (`auth.json`).
- `[0]` Salir del asistente.

---

## 🛠️ Herramientas MCP Expuestas

Cuando un Agente de IA se conecta a este servidor, tiene acceso a las siguientes herramientas:

| Herramienta | Parámetros | Descripción |
| :--- | :--- | :--- |
| **`extract_design_system`** | `url`, `output_file`, `storage_state`, `cookie` | Visita la web, extrae el sistema completo, guarda el archivo `.md`, los tokens W3C `.json` y la captura `.png`, y devuelve la especificación maestra. |
| **`extract_design_tokens`** | `url`, `output_file`, `storage_state`, `cookie` | Extrae y guarda tokens de diseño estándar W3C DTCG en formato JSON compatible con Figma y Style Dictionary. |
| **`inspect_component`** | `url`, `selector`, `storage_state`, `cookie` | Inspecciona un elemento específico por selector CSS (ej. `header`, `.pricing-card`, `button.cta`) devolviendo sus dimensiones exactas, bordes y HTML. |
| **`generate_tailwind_theme`** | `url`, `storage_state`, `cookie` | Extrae los tokens de la página y devuelve un bloque listo para copiar en `tailwind.config.js`. |
| **`inspect_page_source`** | `url`, `storage_state`, `cookie` | Realiza auditoría del código fuente: frameworks detectados, breakpoints `@media` y clases de utilidad. |
| **`capture_page_screenshot`** | `url`, `output_path`, `storage_state`, `cookie` | Captura una imagen de alta resolución de la página completa. |
| **`set_output_directory`** | `path` | Actualiza y persiste la carpeta de guardado de los archivos. |
| **`get_output_directory`** | *(ninguno)* | Devuelve la ruta de la carpeta activa actual. |
| **`check_for_updates`** | *(ninguno)* | Comprueba si existe una versión más reciente en GitHub. |
| **`update_server`** | *(ninguno)* | Descarga automáticamente la última versión desde GitHub y actualiza dependencias. |

---

## 📋 Ejemplo del Markdown Generado para Agentes

Cada extracción genera un archivo con directivas maestras listas para pasar a tu agente:

```markdown
### AGENT MASTER DIRECTIVES: DESIGN FIDELITY RULES

1. CANVAS & PALETTE CONSTRAINTS:
   - Root background MUST be '#181733' with default text '#ffffff'.
   - Surfaces/Cards MUST use '#1c1b3d' with border 'rgba(255, 255, 255, 0.08)'.
   - Accent color '#fbc43f' is reserved for primary CTA buttons and live badges.

2. TYPOGRAPHY RULES:
   - Headings font: 'Oswald' (condensed, uppercase).
   - Body font: 'Inter'.
   - Hero Title (H1): 72px scale, extrabold (800), line-height 0.95.

3. CONTAINER & WRAPPER ARCHITECTURE:
   - Wrap each section in:
     <section class="py-16 md:py-24"><div class="max-w-[1480px] mx-auto px-4 sm:px-6">...</div></section>
   - Grid layout: grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6.
```

---

## 📂 Estructura del Repositorio

```text
web-design-extractor-mcp/
├── cli.py               # Punto de entrada unificado y ejecutor de atajos (design-extractor)
├── setup_wizard.py      # Asistente interactivo de terminal estilo Moodle MCP
├── ui.py                # Componentes visuales, tablas y dashboard renderizados con Rich
├── updater.py           # Motor de auto-actualización inteligente con GitHub
├── system_checker.py    # Auto-diagnóstico y auto-reparación de Playwright Chromium
├── storage.py           # Escritura atómica a prueba de fallos y caché con TTL
├── path_installer.py    # Integración global del comando en PATH (Windows/Linux/macOS)
├── preset_manager.py    # Gestor de flujos de trabajo personalizados y presets
├── server.py            # Servidor MCP (FastMCP) con todas las herramientas expuestas
├── core_extractor.py    # Motor de análisis DOM, estilos computados y Playwright
├── config_manager.py    # Gestor de carpetas y persistencia de configuración
├── configurar.bat       # Lanzador rápido para terminal en Windows
├── pyproject.toml       # Especificación de paquete estándar y entry point
├── requirements.txt     # Dependencias de Python
├── .gitignore           # Exclusiones de Git (entornos, temporales, logs)
└── README.md            # Documentación completa
```


---

## 📄 Licencia

Licencia MIT. Libre para uso personal y comercial.

# Web Design Extractor MCP 🌐✨
> **Model Context Protocol (MCP) Server & CLI para ingeniería inversa de sistemas de diseño, estructuras de contenedores y generación de directivas para Agentes de IA.**

[![MCP Standard](https://img.shields.io/badge/MCP-Protocol%201.0-blue.svg)](https://modelcontextprotocol.io)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://python.org)
[![Playwright](https://img.shields.io/badge/Engine-Playwright%20Chromium-orange.svg)](https://playwright.dev)
[![Rich Terminal](https://img.shields.io/badge/UI-Rich%20Terminal-purple.svg)](https://github.com/Textualize/rich)

---

## 🎯 ¿Qué hace este proyecto?

**Web Design Extractor MCP** es un servidor que navega cualquier página web en tiempo real usando un navegador headless (Playwright) para inspeccionar tanto el código fuente como los estilos computados del DOM.

Extrae automáticamente:
1. **🎨 Paleta y Tokens de Color:** Fondos de canvas, superficies/tarjetas, colores de texto (alto contraste y atenuado), acento de marca y bordes, con normalización automática a HEX/RGBA.
2. **🔤 Sistema Tipográfico Completo:** Familias tipográficas para títulos y cuerpo, jerarquía exacta (**H1, H2, H3, H4 y Párrafos**) con tamaños en píxeles, pesos (`font-weight`), interlineados (`line-height`) y espaciado de letras (`letter-spacing`).
3. **📐 Arquitectura de Layout y Divs:** Anchuras máximas de contenedor (`max-w-*`), espaciado rítmico de secciones (`py-16` / `py-24`), patrones de rejilla (`CSS Grid` y `Flexbox`), y esqueletos estructurales HTML limpios de **Header**, **Hero**, **Cards** y **Botones**.
4. **🔍 Inteligencia de Código Fuente:** Detección de frameworks en el HTML (**Next.js, React, Vue, Astro, Webflow, Shopify, WordPress, Tailwind CSS**), puntos de interrupción responsivos reales (`@media` del CSS original) y animaciones `@keyframes`.
5. **🤖 Prompt Maestro para Agentes (Master Directives):** Genera una hoja de instrucciones exhaustiva en Markdown (`.md`) lista para copiar y pegar a cualquier Agente de IA para que replique el diseño con 100% de fidelidad visual.
6. **📸 Capturas de Pantalla:** Captura automáticamente una imagen completa en alta resolución (`.png`) para referencia visual.

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

### 4. Uso Directo en Terminal (Sin Agentes / Standalone)
No necesitas obligatoriamente un agente para usarlo:
```bash
# Extraer una web y guardarla en tu carpeta configurada:
python cli.py extract https://stripe.com

# Ver el estado y dashboard:
python cli.py status

# Abrir el asistente interactivo de configuración:
python cli.py setup
```

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/web-design-extractor-mcp.git
cd web-design-extractor-mcp
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
Para abrir la pantalla de configuración (estilo Moodle MCP):

- **En Windows:** Haz doble clic en `configurar.bat` o ejecuta:
  ```powershell
  python cli.py setup
  ```
- **En Linux / Mac:**
  ```bash
  python3 cli.py setup
  ```

Desde este menú interactivo puedes:
- `[1]` Cambiar la carpeta permanente donde se guardan tus `.md` y `.png`.
- `[2]` Probar la extracción en vivo de cualquier URL con barra de progreso.
- `[3]` Abrir la carpeta de destino en el Explorador de archivos.
- `[4]` Ver la guía de prompts para agentes.
- `[5]` Comprobar el estado de registro en `mcp_config.json`.

---

## 🛠️ Herramientas MCP Expuestas

Cuando un Agente de IA se conecta a este servidor, tiene acceso a las siguientes herramientas:

| Herramienta | Parámetros | Descripción |
| :--- | :--- | :--- |
| **`extract_design_system`** | `url` *(str)*, `output_file` *(opcional)* | Visita la web, extrae el sistema completo, guarda el archivo `.md` y la captura `.png` en la carpeta configurada, y devuelve la hoja de especificaciones. |
| **`inspect_component`** | `url` *(str)*, `selector` *(str)* | Inspecciona un elemento específico por selector CSS (ej. `header`, `.pricing-card`, `button.cta`) devolviendo sus dimensiones exactas, bordes y HTML. |
| **`generate_tailwind_theme`** | `url` *(str)* | Extrae los tokens de la página y devuelve un bloque listo para copiar en `tailwind.config.js`. |
| **`inspect_page_source`** | `url` *(str)* | Realiza auditoría del código fuente: frameworks detectados, breakpoints `@media` y clases de utilidad. |
| **`capture_page_screenshot`** | `url` *(str)*, `output_path` *(opcional)* | Captura una imagen de alta resolución de la página completa. |
| **`set_output_directory`** | `path` *(str)* | Actualiza y persiste la carpeta de guardado de los archivos. |
| **`get_output_directory`** | *(ninguno)* | Devuelve la ruta de la carpeta activa actual. |

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
├── cli.py               # Punto de entrada unificado (setup, status, extract, serve)
├── setup_wizard.py      # Asistente interactivo de terminal estilo Moodle MCP
├── ui.py                # Componentes visuales y tablas renderizadas con Rich
├── server.py            # Servidor MCP (FastMCP) con todas las herramientas expuestas
├── core_extractor.py    # Motor de análisis DOM, estilos computados y Playwright
├── config_manager.py    # Gestor de carpetas y persistencia de configuración
├── configurar.bat       # Lanzador rápido para terminal en Windows
├── requirements.txt     # Dependencias de Python
├── .gitignore           # Exclusiones de Git (entornos, temporales, logs)
└── README.md            # Documentación completa
```

---

## 📄 Licencia

Licencia MIT. Libre para uso personal y comercial.

# ==============================================================================
# Design Extractor MCP - Instalador Automático para Windows (PowerShell)
# Repositorio: https://github.com/JhonnyCCM/Design-Extractor-MCP
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Instalador Design Extractor MCP"

function Write-Step {
    param([string]$Text)
    Write-Host "`n[+] $Text" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Text)
    Write-Host "[OK] $Text" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Text)
    Write-Host "[!] $Text" -ForegroundColor Yellow
}

function Write-ErrorMsg {
    param([string]$Text)
    Write-Host "[ERROR] $Text" -ForegroundColor Red
}

Clear-Host
Write-Host "=====================================================================" -ForegroundColor Magenta
Write-Host "             DESIGN EXTRACTOR MCP - INSTALADOR WINDOWS               " -ForegroundColor Magenta
Write-Host "    Ingeniería Inversa de UI/UX, Tokens W3C, Shadcn UI y Tailwind v4 " -ForegroundColor DarkGray
Write-Host "=====================================================================" -ForegroundColor Magenta

# 1. Determinar directorio de instalación
$ProjectDir = $PSScriptRoot
if (-not $ProjectDir) {
    $ProjectDir = (Get-Location).Path
}
Set-Location -Path $ProjectDir

# 2. Verificar Python
Write-Step "Comprobando entorno de Python (>= 3.10)..."
$PythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCmd = "py -3"
}

if (-not $PythonCmd) {
    Write-ErrorMsg "Python no fue detectado en el sistema."
    Write-Host "Por favor instala Python 3.10 o superior marcando 'Add python.exe to PATH'."
    Write-Host "Puedes instalarlo ejecutando en otra terminal: winget install Python.Python.3.11" -ForegroundColor Yellow
    pause
    exit 1
}

$PyVersion = & ([scriptblock]::Create("$PythonCmd --version")) 2>&1
Write-Success "Python detectado: $PyVersion"

# 3. Crear entorno virtual (.venv)
$VenvDir = Join-Path $ProjectDir ".venv"
$VenvPy = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $VenvPy)) {
    Write-Step "Creando entorno virtual aislado (.venv)..."
    & ([scriptblock]::Create("$PythonCmd -m venv `"$VenvDir`""))
    if (-not (Test-Path $VenvPy)) {
        Write-ErrorMsg "No se pudo inicializar el entorno virtual .venv."
        pause
        exit 1
    }
    Write-Success "Entorno virtual creado en: $VenvDir"
} else {
    Write-Success "Entorno virtual existente reutilizado: $VenvDir"
}

# 4. Actualizar pip e instalar dependencias
Write-Step "Instalando dependencias de producción (mcp, playwright, rich, pydantic)..."
& $VenvPy -m pip install --upgrade pip --quiet
$ReqFile = Join-Path $ProjectDir "requirements.txt"
if (Test-Path $ReqFile) {
    & $VenvPy -m pip install -r $ReqFile --quiet
} else {
    & $VenvPy -m pip install "mcp>=1.3.0,<2.0.0" "playwright>=1.40.0" "rich>=13.0.0" "pydantic>=2.0.0" "tomlkit>=0.13.0" --quiet
}
Write-Success "Dependencias instaladas correctamente."

# 5. Instalar navegador Chromium para Playwright
Write-Step "Instalando navegador headless Chromium para Playwright..."
try {
    & $VenvPy -m playwright install chromium
    Write-Success "Chromium verificado y listo para extracciones."
} catch {
    Write-Warning "Hubo una advertencia al instalar Chromium. Verificando ejecutable..."
}

# 6. Instalar comando global en PATH
Write-Step "Instalando comando global 'design-extractor' en tu terminal..."
try {
    & $VenvPy cli.py path install
    Write-Success "Comando 'design-extractor' disponible globalmente."
} catch {
    Write-Warning "No se pudo registrar el comando en WindowsApps. Puedes usar .venv\Scripts\python cli.py"
}

# 7. Auto-detectar e integrar clientes IA (Antigravity, Claude, Cursor, Windsurf, VS Code)
Write-Step "Buscando agentes y herramientas de IA locales para registrar MCP..."
try {
    & $VenvPy cli.py install-agents
} catch {
    Write-Warning "No se completó la integración automática de agentes."
}

# 8. Verificación final y resumen
Write-Host "`n=====================================================================" -ForegroundColor Green
Write-Host "               ¡INSTALACIÓN COMPLETADA CON ÉXITO!                    " -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "Ahora puedes usar Design Extractor desde cualquier terminal:`n"
Write-Host "  1. Menú interactivo TUI:       " -NoNewline; Write-Host "design-extractor" -ForegroundColor Cyan
Write-Host "  2. Extracción directa:         " -NoNewline; Write-Host "design-extractor extract https://ejemplo.com" -ForegroundColor Cyan
Write-Host "  3. Iniciar sesión interactiva: " -NoNewline; Write-Host "design-extractor login https://moodle.edu" -ForegroundColor Cyan
Write-Host "  4. Ver estado de agentes MCP:  " -NoNewline; Write-Host "design-extractor status" -ForegroundColor Cyan
Write-Host "  5. Actualizar en un clic:      " -NoNewline; Write-Host "design-extractor update" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor DarkGray
Write-Host "Presiona cualquier tecla para abrir el menú principal o salir..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

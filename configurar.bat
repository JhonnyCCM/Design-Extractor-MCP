@echo off
title Web Design Extractor MCP - Asistente de Configuracion
cd /d "%~dp0"

if not exist "%~dp0.venv\Scripts\python.exe" (
    echo [!] El entorno virtual .venv no fue encontrado.
    echo [*] Iniciando instalador automatico para Windows...
    powershell -ExecutionPolicy Bypass -File "%~dp0INSTALAR-WINDOWS.ps1"
    exit /b %ERRORLEVEL%
)

"%~dp0.venv\Scripts\python.exe" "%~dp0cli.py" setup

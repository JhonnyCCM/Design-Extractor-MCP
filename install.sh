#!/usr/bin/env bash
# ==============================================================================
# Design Extractor MCP - Automated Installer for Linux & macOS
# Repository: https://github.com/JhonnyCCM/Design-Extractor-MCP
# ==============================================================================

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}=====================================================================${NC}"
echo -e "${CYAN}             DESIGN EXTRACTOR MCP - UNIX INSTALLER                   ${NC}"
echo -e "    Reverse Engineering for Web UI/UX, W3C Tokens, Shadcn & TW v4   "
echo -e "${CYAN}=====================================================================${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Check Python 3.10+
echo -e "\n${CYAN}[+] Checking Python 3.10+...${NC}"
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo -e "${RED}[ERROR] Python 3 was not found in PATH.${NC}"
    echo "Please install Python 3.10 or newer (e.g. sudo apt install python3 python3-venv or brew install python)."
    exit 1
fi

PY_VER=$($PYTHON_BIN --version 2>&1)
echo -e "${GREEN}[OK] Found $PY_VER${NC}"

# 2. Virtual environment (.venv)
VENV_DIR="$SCRIPT_DIR/.venv"
VENV_PY="$VENV_DIR/bin/python"

if [ ! -f "$VENV_PY" ]; then
    echo -e "\n${CYAN}[+] Creating virtual environment (.venv)...${NC}"
    $PYTHON_BIN -m venv "$VENV_DIR"
    echo -e "${GREEN}[OK] Virtual environment created at $VENV_DIR${NC}"
else
    echo -e "${GREEN}[OK] Reusing existing virtual environment at $VENV_DIR${NC}"
fi

# 3. Dependencies
echo -e "\n${CYAN}[+] Installing dependencies...${NC}"
"$VENV_PY" -m pip install --upgrade pip --quiet
if [ -f "requirements.txt" ]; then
    "$VENV_PY" -m pip install -r requirements.txt --quiet
fi
echo -e "${GREEN}[OK] Dependencies successfully installed.${NC}"

# 4. Playwright Chromium
echo -e "\n${CYAN}[+] Installing Playwright Chromium browser engine...${NC}"
"$VENV_PY" -m playwright install chromium || true
echo -e "${GREEN}[OK] Playwright Chromium configured.${NC}"

# 5. Global PATH Command
echo -e "\n${CYAN}[+] Installing global 'design-extractor' command to ~/.local/bin...${NC}"
"$VENV_PY" cli.py path install || true

# 6. Auto-integrate AI Agents
echo -e "\n${CYAN}[+] Detecting and registering MCP server with local AI agents...${NC}"
"$VENV_PY" cli.py install-agents || true

echo -e "\n${GREEN}=====================================================================${NC}"
echo -e "${GREEN}             INSTALLATION COMPLETED SUCCESSFULLY!                    ${NC}"
echo -e "${GREEN}=====================================================================${NC}"
echo -e "You can now execute Design Extractor from anywhere:"
echo -e "  - Interactive Menu:    ${CYAN}design-extractor${NC}"
echo -e "  - Direct Extraction:   ${CYAN}design-extractor extract https://example.com${NC}"
echo -e "  - Login Session:       ${CYAN}design-extractor login https://moodle.edu${NC}"
echo -e "  - Agent Status:        ${CYAN}design-extractor status${NC}"
echo -e "  - Auto-Update:         ${CYAN}design-extractor update${NC}"
echo -e "${CYAN}=====================================================================${NC}\n"

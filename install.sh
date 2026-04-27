#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────
#  portctl — installer for macOS (zsh)
# ─────────────────────────────────────────────

TOOL_NAME="portctl"
INSTALL_DIR="/usr/local/bin"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$SCRIPT_DIR/portctl.py"
TARGET="$INSTALL_DIR/$TOOL_NAME"
ZSHRC="$HOME/.zshrc"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

print_banner() {
  echo ""
  echo -e "${CYAN}${BOLD}  🔌 portctl installer${RESET}"
  echo -e "${DIM}  ─────────────────────────────${RESET}"
  echo ""
}

step()    { echo -e "  ${CYAN}→${RESET} $1"; }
ok()      { echo -e "  ${GREEN}✓${RESET} $1"; }
warn()    { echo -e "  ${YELLOW}⚠${RESET}  $1"; }
fail()    { echo -e "  ${RED}✗${RESET}  $1"; exit 1; }

# ── Checks ───────────────────────────────────

print_banner

# macOS only
if [[ "$(uname)" != "Darwin" ]]; then
  fail "Este instalador es solo para macOS."
fi

# portctl.py must exist next to this script
if [[ ! -f "$SOURCE" ]]; then
  fail "No se encontró portctl.py en $SCRIPT_DIR"
fi

# Python 3
step "Buscando Python 3..."
PYTHON=""
for candidate in python3 python; do
  if command -v "$candidate" &>/dev/null; then
    version=$("$candidate" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    major="${version%%.*}"
    if [[ "$major" -ge 3 ]]; then
      PYTHON="$candidate"
      ok "Usando $($candidate --version 2>&1)  ($(command -v $candidate))"
      break
    fi
  fi
done

if [[ -z "$PYTHON" ]]; then
  warn "Python 3 no encontrado."
  step "Instalando Python 3 vía Homebrew..."
  if ! command -v brew &>/dev/null; then
    fail "Homebrew tampoco está instalado. Instala Python 3 manualmente: https://python.org"
  fi
  brew install python3
  PYTHON="python3"
  ok "Python 3 instalado."
fi

# ── Dependencies ─────────────────────────────

step "Instalando dependencias Python (rich, typer, psutil)..."
if "$PYTHON" -m pip install --quiet --upgrade rich typer psutil 2>/dev/null; then
  ok "Dependencias instaladas."
else
  # Try with --break-system-packages (Python 3.11+ on some macOS setups)
  if "$PYTHON" -m pip install --quiet --upgrade --break-system-packages rich typer psutil 2>/dev/null; then
    ok "Dependencias instaladas (--break-system-packages)."
  else
    # Fallback: pipx or user install
    warn "pip con permisos normales falló, intentando --user..."
    "$PYTHON" -m pip install --quiet --upgrade --user rich typer psutil \
      || fail "No se pudieron instalar las dependencias. Ejecuta manualmente:\n    pip3 install rich typer psutil"
    ok "Dependencias instaladas (--user)."
  fi
fi

# ── Install binary ────────────────────────────

step "Instalando $TOOL_NAME en $INSTALL_DIR..."

# Fix shebang in source to use the found Python, then symlink
PYTHON_PATH="$(command -v "$PYTHON")"
sed -i '' "1s|.*|#!${PYTHON_PATH}|" "$SOURCE"
chmod +x "$SOURCE"

# Symlink so edits to portctl.py take effect immediately (no reinstall needed)
if [[ ! -w "$INSTALL_DIR" ]]; then
  step "$INSTALL_DIR requiere sudo..."
  sudo ln -sf "$SOURCE" "$TARGET"
else
  ln -sf "$SOURCE" "$TARGET"
fi

ok "$TOOL_NAME instalado en $TARGET"

# ── PATH check ────────────────────────────────

if ! echo "$PATH" | tr ':' '\n' | grep -qx "$INSTALL_DIR"; then
  warn "$INSTALL_DIR no está en tu PATH."
  step "Añadiendo $INSTALL_DIR al PATH en $ZSHRC..."
  {
    echo ""
    echo "# portctl"
    echo "export PATH=\"$INSTALL_DIR:\$PATH\""
  } >> "$ZSHRC"
  ok "Añadido a $ZSHRC"
  RELOAD_NEEDED=true
else
  ok "$INSTALL_DIR ya está en PATH."
  RELOAD_NEEDED=false
fi

# ── Alias (optional) ─────────────────────────

if ! grep -q "alias portctl" "$ZSHRC" 2>/dev/null; then
  # Only add alias if binary name != 'portctl' for some reason — skip, binary is already named portctl
  :
fi

# ── Done ──────────────────────────────────────

echo ""
echo -e "${DIM}  ─────────────────────────────${RESET}"
echo -e "  ${GREEN}${BOLD}¡Instalación completada!${RESET}"
echo ""

if [[ "${RELOAD_NEEDED:-false}" == "true" ]]; then
  echo -e "  Recarga tu terminal o ejecuta:"
  echo -e "  ${CYAN}  source ~/.zshrc${RESET}"
  echo ""
fi

echo -e "  ${BOLD}Comandos:${RESET}"
echo -e "  ${DIM}  portctl --help               # muestra la ayuda${RESET}"
echo -e "  ${DIM}  portctl list                 # lista todos los puertos abiertos${RESET}"
echo -e "  ${DIM}  portctl list -s listen       # filtra: listen | established | close_wait${RESET}"
echo -e "  ${DIM}  portctl kill 3000            # cierra el proceso en el puerto 3000${RESET}"
echo -e "  ${DIM}  portctl kill 3000 --force    # fuerza el cierre con SIGKILL${RESET}"
echo -e "  ${DIM}  portctl interactive          # menu interactivo para seleccionar y cerrar puertos${RESET}"
echo ""

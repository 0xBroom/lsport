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
  fail "This installer is for macOS only."
fi

# portctl.py must exist next to this script
if [[ ! -f "$SOURCE" ]]; then
  fail "portctl.py not found in $SCRIPT_DIR"
fi

# Python 3
step "Looking for Python 3..."
PYTHON=""
for candidate in python3 python; do
  if command -v "$candidate" &>/dev/null; then
    version=$("$candidate" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    major="${version%%.*}"
    if [[ "$major" -ge 3 ]]; then
      PYTHON="$candidate"
      ok "Using $($candidate --version 2>&1)  ($(command -v $candidate))"
      break
    fi
  fi
done

if [[ -z "$PYTHON" ]]; then
  warn "Python 3 not found."
  step "Installing Python 3 via Homebrew..."
  if ! command -v brew &>/dev/null; then
    fail "Homebrew is not installed either. Install Python 3 manually: https://python.org"
  fi
  brew install python3
  PYTHON="python3"
  ok "Python 3 installed."
fi

# ── Dependencies ─────────────────────────────

step "Installing Python dependencies (rich, typer, psutil)..."
if "$PYTHON" -m pip install --quiet --upgrade rich typer psutil 2>/dev/null; then
  ok "Dependencies installed."
else
  # Try with --break-system-packages (Python 3.11+ on some macOS setups)
  if "$PYTHON" -m pip install --quiet --upgrade --break-system-packages rich typer psutil 2>/dev/null; then
    ok "Dependencies installed (--break-system-packages)."
  else
    # Fallback: pipx or user install
    warn "pip with normal permissions failed, trying --user..."
    "$PYTHON" -m pip install --quiet --upgrade --user rich typer psutil \
      || fail "Could not install dependencies. Run manually:\n    pip3 install rich typer psutil"
    ok "Dependencies installed (--user)."
  fi
fi

# ── Install binary ────────────────────────────

step "Installing $TOOL_NAME in $INSTALL_DIR..."

# Fix shebang in source to use the found Python, then symlink
PYTHON_PATH="$(command -v "$PYTHON")"
sed -i '' "1s|.*|#!${PYTHON_PATH}|" "$SOURCE"
chmod +x "$SOURCE"

# Symlink so edits to portctl.py take effect immediately (no reinstall needed)
if [[ ! -w "$INSTALL_DIR" ]]; then
  step "$INSTALL_DIR requires sudo..."
  sudo ln -sf "$SOURCE" "$TARGET"
else
  ln -sf "$SOURCE" "$TARGET"
fi

ok "$TOOL_NAME installed at $TARGET"

# ── PATH check ────────────────────────────────

if ! echo "$PATH" | tr ':' '\n' | grep -qx "$INSTALL_DIR"; then
  warn "$INSTALL_DIR is not in your PATH."
  step "Adding $INSTALL_DIR to PATH in $ZSHRC..."
  {
    echo ""
    echo "# portctl"
    echo "export PATH=\"$INSTALL_DIR:\$PATH\""
  } >> "$ZSHRC"
  ok "Added to $ZSHRC"
  RELOAD_NEEDED=true
else
  ok "$INSTALL_DIR is already in PATH."
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
echo -e "  ${GREEN}${BOLD}Installation complete!${RESET}"
echo ""

if [[ "${RELOAD_NEEDED:-false}" == "true" ]]; then
  echo -e "  Reload your terminal or run:"
  echo -e "  ${CYAN}  source ~/.zshrc${RESET}"
  echo ""
fi

echo -e "  ${BOLD}Commands:${RESET}"
echo -e "  ${DIM}  portctl --help               # show help${RESET}"
echo -e "  ${DIM}  portctl list                 # list all open ports${RESET}"
echo -e "  ${DIM}  portctl list -s listen       # filter: listen | established | close_wait${RESET}"
echo -e "  ${DIM}  portctl kill 3000            # close the process on port 3000${RESET}"
echo -e "  ${DIM}  portctl kill 3000 --force    # force close with SIGKILL${RESET}"
echo -e "  ${DIM}  portctl interactive          # interactive menu to select and close ports${RESET}"
echo ""

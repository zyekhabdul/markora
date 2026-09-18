#!/usr/bin/env bash
set -e

# Markora 1-Line Sovereign Installer
# Installs markora standalone binary to ~/.local/bin/

INSTALL_DIR="${HOME}/.local/bin"
REPO_URL="https://raw.githubusercontent.com/zyekhabdul/markora/main/bin/markora"
TARGET_FILE="${INSTALL_DIR}/markora"

echo "==> Installing Markora (Sovereign Markdown Notebook & Todo TUI)..."

mkdir -p "${INSTALL_DIR}"

if command -v curl >/dev/null 2>&1; then
    curl -fsSL "${REPO_URL}" -o "${TARGET_FILE}"
elif command -v wget >/dev/null 2>&1; then
    wget -qO "${TARGET_FILE}" "${REPO_URL}"
else
    echo "Error: curl or wget required for installation." >&2
    exit 1
fi

chmod +x "${TARGET_FILE}"
ln -sf "${TARGET_FILE}" "${INSTALL_DIR}/td"
rm -f "${INSTALL_DIR}/todo" "${INSTALL_DIR}/mo"

echo "==> Success! Markora installed to ${TARGET_FILE}"
echo ""
echo "Quick Start:"
echo "  markora        # Launch interactive 4-tab Curses TUI (default)"
echo "  td ls -p       # Quick list pending tasks"
echo "  td a 'Task'    # Quick add a task"
echo "  td qn 'Memo'   # Append to QuickNote"
echo ""
if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
    echo "Note: Make sure ${INSTALL_DIR} is in your PATH."
    echo "Add this to your ~/.bashrc or ~/.zshrc:"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
fi

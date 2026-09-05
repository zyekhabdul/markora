#!/usr/bin/env bash
set -euo pipefail

# Build and register Markora in a local/hosted Pacman repository
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_SRC="$(cd "$REPO_DIR/../aur" && pwd)"
DB_NAME="zyekh"

echo "==> Building Markora Arch package..."
cd "$PKG_SRC"
makepkg -s --nodeps --cleanbuild --force

echo "==> Copying package to repo directory..."
cp -f "$PKG_SRC"/markora-*.pkg.tar.zst "$REPO_DIR/"

echo "==> Updating pacman repo database ($DB_NAME.db.tar.zst)..."
cd "$REPO_DIR"
repo-add -n -R "$DB_NAME.db.tar.zst" markora-*.pkg.tar.zst

echo "==> Done! Pacman database created at $REPO_DIR/$DB_NAME.db.tar.zst"
echo ""
echo "To consume this repo locally or via web server:"
echo "Add to /etc/pacman.conf:"
echo "  [$DB_NAME]"
echo "  SigLevel = Optional TrustAll"
echo "  Server = file://$REPO_DIR"
echo "  # Or if hosted: Server = https://yourdomain.com/arch/\$arch"

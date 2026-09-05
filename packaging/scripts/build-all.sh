#!/usr/bin/env bash
set -euo pipefail

# Markora Multi-Platform Packaging Master Runner
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "=================================================="
echo "⚡ Markora Multi-Platform Packaging Orchestrator ⚡"
echo "=================================================="

# 1. Python Wheels & Sdist (PyPI)
echo ""
echo "[ 1/4 ] Building Python Wheel & Sdist (PyPI)..."
cd "$ROOT_DIR"
python3 -m build --wheel --sdist

# 2. Arch Linux Pacman Repo & AUR
echo ""
echo "[ 2/4 ] Building Arch Linux Package & Pacman DB..."
bash "$ROOT_DIR/packaging/pacman-repo/build-repo.sh"

# 3. Debian / Ubuntu .deb
echo ""
echo "[ 3/4 ] Building Debian (.deb) Package..."
bash "$ROOT_DIR/packaging/debian/build-deb.sh"

# 4. Summary of artifacts
echo ""
echo "=================================================="
echo "🎉 ALL PLATFORM PACKAGES SUCCESSFULLY BUILT:"
echo "=================================================="
ls -lh "$ROOT_DIR/dist"/*.whl "$ROOT_DIR/dist"/*.tar.gz
ls -lh "$ROOT_DIR/packaging/aur"/*.pkg.tar*
ls -lh "$ROOT_DIR/packaging/debian"/*.deb
ls -lh "$ROOT_DIR/packaging/pacman-repo"/zyekh.db*
echo "=================================================="

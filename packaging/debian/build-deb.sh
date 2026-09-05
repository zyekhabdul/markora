#!/usr/bin/env bash
set -euo pipefail

# Build .deb package using dpkg-deb
PKG_NAME="markora"
PKG_VER="1.0.0"
PKG_ARCH="all"
DIST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$DIST_DIR/build_deb/${PKG_NAME}_${PKG_VER}_${PKG_ARCH}"

echo "==> Building Debian (.deb) package for $PKG_NAME v$PKG_VER..."
rm -rf "$DIST_DIR/build_deb"
mkdir -p "$WORK_DIR/DEBIAN"
mkdir -p "$WORK_DIR/usr/bin"
mkdir -p "$WORK_DIR/usr/lib/python3/dist-packages"
mkdir -p "$WORK_DIR/usr/share/doc/$PKG_NAME"

cat << 'EOF' > "$WORK_DIR/DEBIAN/control"
Package: markora
Version: 1.0.0
Section: utils
Priority: optional
Architecture: all
Depends: python3 (>= 3.8)
Recommends: python3-gkeepapi, python3-playwright
Maintainer: zyekhabdul <zyekhabdulqadirjailani@gmail.com>
Description: Sovereign Markor-style Markdown Notebook, QuickNotes & Todo TUI
 Markora is an ultra-lightweight, zero-dependency Markdown notebook,
 task manager, and QuickNotes TUI designed for terminal power users.
 Includes aliases: td, todo, mo.
EOF

# Copy source module
PROJECT_ROOT="$(cd "$DIST_DIR/../.." && pwd)"
cp -r "$PROJECT_ROOT/src/markora" "$WORK_DIR/usr/lib/python3/dist-packages/"

# Create executable wrappers
cat << 'EOF' > "$WORK_DIR/usr/bin/markora"
#!/usr/bin/env python3
import sys
from markora.cli import main
if __name__ == '__main__':
    sys.exit(main())
EOF

chmod 755 "$WORK_DIR/usr/bin/markora"
ln -sf markora "$WORK_DIR/usr/bin/td"
ln -sf markora "$WORK_DIR/usr/bin/todo"
ln -sf markora "$WORK_DIR/usr/bin/mo"

# Docs & License
cp "$PROJECT_ROOT/README.md" "$WORK_DIR/usr/share/doc/$PKG_NAME/"
cp "$PROJECT_ROOT/LICENSE" "$WORK_DIR/usr/share/doc/$PKG_NAME/copyright"

dpkg-deb --build --root-owner-group "$WORK_DIR" "$DIST_DIR/${PKG_NAME}_${PKG_VER}_${PKG_ARCH}.deb"
rm -rf "$DIST_DIR/build_deb"

echo "==> Done! Created: $DIST_DIR/${PKG_NAME}_${PKG_VER}_${PKG_ARCH}.deb"

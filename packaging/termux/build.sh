# Termux package definition for markora
TERMUX_PKG_HOMEPAGE=https://github.com/zyekhabdul/markora
TERMUX_PKG_DESCRIPTION="Sovereign Markor-style Markdown Notebook, QuickNotes & Todo TUI"
TERMUX_PKG_LICENSE="MIT"
TERMUX_PKG_MAINTAINER="zyekhabdul <zyekhabdulqadirjailani@gmail.com>"
TERMUX_PKG_VERSION=1.0.0
TERMUX_PKG_SRCURL=https://github.com/zyekhabdul/markora/archive/refs/tags/v${TERMUX_PKG_VERSION}.tar.gz
TERMUX_PKG_SHA256=da1341d812e50abc080b86ce26e033b972543777904183acd2567edc7e1175e3
TERMUX_PKG_DEPENDS="python"
TERMUX_PKG_PLATFORM_INDEPENDENT=true
TERMUX_PKG_BUILD_IN_SRC=true

termux_step_make_install() {
    pip install . --prefix="$TERMUX_PREFIX" --no-deps
}

termux_step_post_massage() {
    ln -sf markora "$TERMUX_PREFIX/bin/td"
    ln -sf markora "$TERMUX_PREFIX/bin/todo"
    ln -sf markora "$TERMUX_PREFIX/bin/mo"
}

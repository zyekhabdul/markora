class Markora < Formula
  desc "Sovereign Markor-style Markdown Notebook, QuickNotes & Todo TUI"
  homepage "https://github.com/zyekhabdul/markora"
  url "https://github.com/zyekhabdul/markora/archive/refs/tags/v1.1.0.tar.gz"
  sha256 "f3c9859ff3b50bfd0326f801ef90456b997f50c99d5e12f9f77238f90d8bb86e"
  license "MIT"
  head "https://github.com/zyekhabdul/markora.git", branch: "main"

  depends_on "python@3.12" => :recommended

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"markora", "--help"
    system bin/"td", "--help"
  end
end

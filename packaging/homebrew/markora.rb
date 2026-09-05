class Markora < Formula
  desc "Sovereign Markor-style Markdown Notebook, QuickNotes & Todo TUI"
  homepage "https://github.com/zyekhabdul/markora"
  url "https://github.com/zyekhabdul/markora/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "da1341d812e50abc080b86ce26e033b972543777904183acd2567edc7e1175e3"
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

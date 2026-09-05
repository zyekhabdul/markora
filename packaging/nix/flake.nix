{
  description = "Sovereign Markor-style Markdown Notebook, QuickNotes & Todo TUI";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonPackages = pkgs.python3Packages;
      in
      {
        packages.default = pythonPackages.buildPythonApplication {
          pname = "markora";
          version = "1.0.0";
          src = ./.;

          format = "setuptools";

          propagatedBuildInputs = [
            # Optional Google Keep integration dependencies can be added here
          ];

          doCheck = false;

          meta = with pkgs.lib; {
            description = "Sovereign Markor-style Markdown Notebook, QuickNotes & Todo TUI";
            homepage = "https://github.com/zyekhabdul/markora";
            license = licenses.mit;
            maintainers = [ ];
            mainProgram = "markora";
          };
        };

        apps.default = flake-utils.lib.mkApp {
          drv = self.packages.${system}.default;
        };
      });
}

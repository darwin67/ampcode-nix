{
  description = "Up-to-date Nix package for the Amp coding agent";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
      pkgsFor =
        system:
        import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };
    in
    {
      packages = forAllSystems (
        system:
        let
          amp-cli = (pkgsFor system).callPackage ./package.nix { };
        in
        {
          inherit amp-cli;
          default = amp-cli;
        }
      );

      overlays.default = final: _prev: {
        amp-cli = final.callPackage ./package.nix { };
      };

      formatter = forAllSystems (system: (pkgsFor system).nixfmt-tree);
    };
}

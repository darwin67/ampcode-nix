# ampcode-nix

An automatically updated Nix package for [Amp](https://ampcode.com/). The
version, artifact URLs, and SHA-256 hashes are read from Amp's
[official Homebrew tap](https://github.com/ampcode/homebrew-tap) every hour.

## Run directly

```console
nix run github:darwin67/ampcode-nix
```

Amp is distributed as an unfree binary, but this flake enables the package for
direct use. The wrapped executable disables Amp's self-update check and adds
`ripgrep` to its `PATH`, matching the nixpkgs package behavior.

## Use as a flake input

```nix
{
  inputs.ampcode.url = "github:darwin67/ampcode-nix";

  outputs = { self, nixpkgs, ampcode, ... }: {
    nixosConfigurations.my-host = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ({ pkgs, ... }: {
          environment.systemPackages = [ ampcode.packages.${pkgs.system}.default ];
        })
      ];
    };
  };
}
```

Or consume the overlay and use `pkgs.amp-cli`:

```nix
nixpkgs.overlays = [ ampcode.overlays.default ];
nixpkgs.config.allowUnfree = true;
environment.systemPackages = [ pkgs.amp-cli ];
```

Flake packages are exposed for `x86_64-linux`, `aarch64-linux`, and
`aarch64-darwin`. The updater also retains the tap's `x86_64-darwin` source for
overlay consumers using an older nixpkgs that still supports Intel macOS.
Current nixpkgs unstable has dropped that platform. The official tap's
`linux-x64` binary may require AVX2; unlike nixpkgs, the tap does not publish
its baseline build in the formula.

## Updating

The hourly workflow runs `update.py`, validates and builds the flake, and
commits a changed `sources.json` back to the default branch. Updates can also
be run locally:

```console
python3 update.py
nix flake check
```

The repository's GitHub Actions settings must allow workflows to write to the
repository. Branch protection must either permit the GitHub Actions bot to push
or be adjusted to use pull requests instead.

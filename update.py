#!/usr/bin/env python3
"""Update sources.json from ampcode/homebrew-tap's Amp formula."""

import base64
import json
import re
import sys
import urllib.request
from pathlib import Path

FORMULA_URL = "https://raw.githubusercontent.com/ampcode/homebrew-tap/main/Formula/ampcode.rb"
PLATFORMS = {
    "darwin-arm64": "aarch64-darwin",
    "darwin-x64": "x86_64-darwin",
    "linux-arm64": "aarch64-linux",
    "linux-x64": "x86_64-linux",
}


def sri_hash(hex_hash: str) -> str:
    return "sha256-" + base64.b64encode(bytes.fromhex(hex_hash)).decode()


def main() -> int:
    request = urllib.request.Request(FORMULA_URL, headers={"User-Agent": "ampcode-nix-updater"})
    with urllib.request.urlopen(request) as response:
        formula = response.read().decode()

    version_matches = re.findall(r'^\s*version "([^"]+)"$', formula, re.MULTILINE)
    if len(version_matches) != 1:
        raise RuntimeError(f"expected one formula version, found {len(version_matches)}")
    version = version_matches[0]

    pairs = re.findall(
        r'^\s*url "([^"]+/amp-([^"]+))"\s*\n\s*sha256 "([0-9a-f]{64})"$',
        formula,
        re.MULTILINE,
    )
    if len(pairs) != len(PLATFORMS):
        raise RuntimeError(f"expected {len(PLATFORMS)} formula sources, found {len(pairs)}")

    sources = {}
    for url, platform, hex_hash in pairs:
        if platform not in PLATFORMS:
            raise RuntimeError(f"unsupported platform in formula: {platform}")
        if f"/{version}/" not in url:
            raise RuntimeError(f"URL does not contain formula version: {url}")
        system = PLATFORMS[platform]
        if system in sources:
            raise RuntimeError(f"duplicate platform in formula: {platform}")
        sources[system] = {"url": url, "hash": sri_hash(hex_hash)}

    if set(sources) != set(PLATFORMS.values()):
        missing = set(PLATFORMS.values()) - set(sources)
        raise RuntimeError(f"formula did not contain the expected platforms; missing: {sorted(missing)}")

    output = {"version": version, "sources": sources}
    destination = Path(__file__).with_name("sources.json")
    rendered = json.dumps(output, indent=2) + "\n"
    if destination.read_text() == rendered:
        print(f"amp-cli is already up to date ({version})")
        return 0

    destination.write_text(rendered)
    print(f"updated amp-cli to {version}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"update failed: {error}", file=sys.stderr)
        sys.exit(1)

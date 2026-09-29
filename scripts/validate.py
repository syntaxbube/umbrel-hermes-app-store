#!/usr/bin/env python3
"""Basic structural validation for this Umbrel community app store."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "umbrel-app-store.yml"
APP_DIR = ROOT / "hermes-lab-hermes-agent"
APP = APP_DIR / "umbrel-app.yml"
COMPOSE = APP_DIR / "docker-compose.yml"


def read(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"required file is missing: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    try:
        store, app, compose = map(read, (STORE, APP, COMPOSE))
        checks = {
            "store ID is valid": bool(re.search(r'^id:\s*[\"\']?hermes-lab[\"\']?\s*$', store, re.M)),
            "store has a name": bool(re.search(r'^name:\s*[\"\']?.+?[\"\']?\s*$', store, re.M)),
            "app manifest ID is store-prefixed": bool(re.search(r'^id:\s*hermes-lab-[a-z0-9-]+\s*$', app, re.M)),
            "app manifest uses supported version": bool(re.search(r'^manifestVersion:\s*1\s*$', app, re.M)),
            "manifest routes app dashboard port 9119": bool(re.search(r'^port:\s*9119\s*$', app, re.M)),
            "compose uses official Hermes image": "image: nousresearch/hermes-agent:latest" in compose,
            "compose enables Hermes dashboard": bool(re.search(r'^\s+HERMES_DASHBOARD:\s*[\"\']?1[\"\']?\s*$', compose, re.M)),
            "dashboard Basic Auth uses generated Umbrel password": "HERMES_DASHBOARD_BASIC_AUTH_PASSWORD: ${APP_PASSWORD}" in compose,
            "dashboard session secret uses generated Umbrel seed": "HERMES_DASHBOARD_BASIC_AUTH_SECRET: ${APP_SEED}" in compose,
            "compose persists Hermes data": "${APP_DATA_DIR}/data:/opt/data" in compose,
            "compose allocates Chromium shared memory": bool(re.search(r'^\s+shm_size:\s*[\"\']?1gb[\"\']?\s*$', compose, re.M)),
            "compose proxies dashboard port": bool(re.search(r'^\s+APP_PORT:\s*9119\s*$', compose, re.M)),
        }
        for description, passed in checks.items():
            print(f"{'PASS' if passed else 'FAIL'} {description}")
        return 0 if all(checks.values()) else 1
    except (OSError, ValueError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

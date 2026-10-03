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
OPENCLAW_DIR = ROOT / "hermes-lab-openclaw-umbrel"
OPENCLAW_APP = OPENCLAW_DIR / "umbrel-app.yml"
OPENCLAW_COMPOSE = OPENCLAW_DIR / "docker-compose.yml"
OPENCLAW_IMAGE = "ghcr.io/syntaxbube/openclaw-umbrel:2026.9.8@sha256:2754e604a9d4a523dec67d5b1d821fde3c24bf708ca62def144c1440e622e3b6"


def read(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"required file is missing: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def service_block(compose: str, name: str) -> str:
    match = re.search(
        rf"(?ms)^  {re.escape(name)}:\n(?P<body>.*?)(?=^  [a-zA-Z0-9_-]+:\n|\Z)",
        compose,
    )
    return match.group("body") if match else ""


def main() -> int:
    try:
        store, app, compose, openclaw_app, openclaw_compose = map(
            read, (STORE, APP, COMPOSE, OPENCLAW_APP, OPENCLAW_COMPOSE)
        )
        openclaw_init = service_block(openclaw_compose, "init_perms")
        openclaw_server = service_block(openclaw_compose, "server")
        checks = {
            "store ID is valid": bool(re.search(r'^id:\s*[\"\']?hermes-lab[\"\']?\s*$', store, re.M)),
            "store has a name": bool(re.search(r'^name:\s*[\"\']?.+?[\"\']?\s*$', store, re.M)),
            "Hermes app manifest ID is store-prefixed": bool(re.search(r'^id:\s*hermes-lab-[a-z0-9-]+\s*$', app, re.M)),
            "Hermes manifest uses supported version": bool(re.search(r'^manifestVersion:\s*1\s*$', app, re.M)),
            "Hermes manifest routes dashboard port 9119": bool(re.search(r'^port:\s*9119\s*$', app, re.M)),
            "Hermes manifest version is 1.0.2": bool(re.search(r'^version:\s*[\"\']1\.0\.2[\"\']\s*$', app, re.M)),
            "Hermes username appears in Umbrel credentials popup": bool(re.search(r'^defaultUsername:\s*hermes\s*$', app, re.M)),
            "Hermes manifest exposes deterministic app password": bool(re.search(r'^deterministicPassword:\s*true\s*$', app, re.M)),
            "Hermes compose uses official image": "image: nousresearch/hermes-agent:latest" in compose,
            "Hermes compose enables dashboard": bool(re.search(r'^\s+HERMES_DASHBOARD:\s*[\"\']?1[\"\']?\s*$', compose, re.M)),
            "Hermes compose preserves s6 as PID 1": not bool(re.search(r'^\s+init:\s*true\s*$', compose, re.M)),
            "Hermes dashboard Basic Auth uses generated password": "HERMES_DASHBOARD_BASIC_AUTH_PASSWORD: ${APP_PASSWORD}" in compose,
            "Hermes dashboard signing key uses generated seed": "HERMES_DASHBOARD_BASIC_AUTH_SECRET: ${APP_SEED}" in compose,
            "Hermes data is persisted": "${APP_DATA_DIR}/data:/opt/data" in compose,
            "Hermes allocates Chromium shared memory": bool(re.search(r'^\s+shm_size:\s*[\"\']?1gb[\"\']?\s*$', compose, re.M)),
            "Hermes proxy target is dashboard port 9119": bool(re.search(r'^\s+APP_PORT:\s*9119\s*$', compose, re.M)),
            "OpenClaw app ID is store-prefixed and distinct from retired app": bool(re.search(r'^id:\s*hermes-lab-openclaw-umbrel\s*$', openclaw_app, re.M)),
            "OpenClaw manifest uses supported version": bool(re.search(r'^manifestVersion:\s*1\s*$', openclaw_app, re.M)),
            "OpenClaw Umbrel package version is 2026.9.8": bool(re.search(r'^version:\s*[\"\']2026\.9\.8[\"\']\s*$', openclaw_app, re.M)),
            "OpenClaw manifest uses unique host-facing tile port 18887": bool(re.search(r'^port:\s*18887\s*$', openclaw_app, re.M)),
            "OpenClaw no longer advertises retired shared-token credentials": "defaultUsername:" not in openclaw_app and "deterministicPassword:" not in openclaw_app,
            "OpenClaw manifest matches pinned upstream release 2026.9.8": "OpenClaw 2026.9.8" in openclaw_app and "2026.9.8@sha256:" in openclaw_compose,
            "OpenClaw uses the verified native multi-arch digest-pinned image": openclaw_compose.count(OPENCLAW_IMAGE) == 2,
            "OpenClaw setup uses mandatory generated Umbrel seed": "APP_SEED: ${APP_SEED:?Umbrel APP_SEED is required}" in openclaw_server,
            "OpenClaw app proxy targets internal Gateway port 18789": bool(re.search(r'^\s+APP_PORT:\s*18789\s*$', openclaw_compose, re.M)),
            "OpenClaw state and workspace are persisted": "${APP_DATA_DIR}/data:/data" in openclaw_compose and "${APP_DATA_DIR}/data/linuxbrew:/home/linuxbrew" in openclaw_server,
            "OpenClaw storage is initialized for non-root UID 1000": 'chown 1000:1000 /data /data/linuxbrew' in openclaw_init and 'user: "1000:1000"' in openclaw_server,
            "OpenClaw gateway waits for storage initialization": "condition: service_completed_successfully" in openclaw_compose,
            "OpenClaw does not publish a raw Gateway port": not bool(re.search(r'^\s*ports:\s*$', openclaw_compose, re.M)),
            "Umbrel app-proxy authentication remains enabled": "PROXY_AUTH_ADD" not in openclaw_compose,
            "OpenClaw proxy target matches new app container": "APP_HOST: hermes-lab-openclaw-umbrel_server_1" in openclaw_compose,
            "OpenClaw preserves image wrapper command": "command:" not in openclaw_server and "entrypoint:" not in openclaw_server,
            "OpenClaw lifecycle is container-owned": "OPENCLAW_SUPERVISOR_MODE: external" in openclaw_server and "OPENCLAW_NO_RESPAWN:" in openclaw_server,
            "OpenClaw shared Gateway token is not injected": "OPENCLAW_GATEWAY_TOKEN" not in openclaw_compose,
            "OpenClaw retired app manifests are absent": not (ROOT / "hermes-lab-openclaw" / "umbrel-app.yml").exists() and not (ROOT / "hermes-lab-openclaw" / "docker-compose.yml").exists(),
            "OpenClaw allocates Chromium shared memory": bool(re.search(r'^\s+shm_size:\s*[\"\']?1gb[\"\']?\s*$', openclaw_compose, re.M)),
        }
        for description, passed in checks.items():
            print(f"{'PASS' if passed else 'FAIL'} {description}")
        return 0 if all(checks.values()) else 1
    except (OSError, ValueError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

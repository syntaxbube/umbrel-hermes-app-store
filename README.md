# Hermes Lab Umbrel Community App Store

A community app store containing Hermes Agent and OpenClaw.

## Install on umbrelOS

1. In umbrelOS, open **App Store → Add a community app store** and enter `https://github.com/syntaxbube/umbrel-hermes-app-store`.
2. Install **Hermes Agent** and/or **OpenClaw** from the Hermes Lab store.
3. Open Hermes and complete setup in its dashboard. OpenClaw's Gateway token is shown in Umbrel's credentials popup; paste it into the Control UI's **Gateway secret** field, then configure a model/provider. A first OpenClaw browser may need one-time pairing approval; see below.

The store ID is `hermes-lab`; Umbrel requires this prefix on each app ID.

## Container and browser

The app uses Nous Research's official `nousresearch/hermes-agent:latest` multi-architecture image. Its official Docker documentation states the image ships with full Chromium for Playwright/browser automation. `shm_size: 1gb` is set because Chromium needs shared memory. Hermes configuration and user data persist in the app data directory mounted at `/opt/data`.

The Umbrel app proxy routes the browser UI to the Hermes dashboard on container port `9119`. Open Hermes from its app tile in umbrelOS; this internal port is the proxy target and is not published as `umbrel.local:9119`. Keep Hermes as PID 1: its image entrypoint starts s6-overlay, which supervises the gateway and dashboard. Do not add Compose `init: true`, because that inserts another PID 1 and disables Hermes service supervision.

The dashboard has built-in Basic Auth enabled. The login name is `hermes`; the password is Umbrel's generated per-app `APP_PASSWORD`, with `defaultUsername: hermes` and `deterministicPassword: true` exposing those generated credentials in umbrelOS's default-credentials popup. The stable session-signing key uses Umbrel's per-app `APP_SEED`; no reusable password or signing key is committed to this repository. The API port `8642` is intentionally not published through the app proxy; expose it separately only if you understand the network/security implications and have a specific API client.

## OpenClaw

The OpenClaw app uses the official `ghcr.io/openclaw/openclaw:2026.9.7-browser` multi-architecture image, pinned in Compose by its verified OCI index digest for `linux/amd64` and `linux/arm64`. The `-browser` variant bundles Chromium. The app enables OpenClaw's browser plugin and headless browser profile, allocates 1 GiB of shared memory, and persists gateway state, configuration, and workspace data under `${APP_DATA_DIR}/data`.

The Gateway listens internally on port `18789`; Umbrel's app proxy routes the tile to that service. Manifest port `18887` is the host-facing app-tile port, not a direct container port. The raw Gateway port is not published. Open the app from the Umbrel tile. Umbrel's app-proxy authentication is intentionally left enabled. The Gateway token is Umbrel's generated `APP_PASSWORD`, exposed in the credentials popup under the label **OpenClaw Gateway token**; OpenClaw has no separate dashboard username, so paste the popup's password value into **Gateway secret**.

**Security note:** OpenClaw's Control UI is an administrator interface. OpenClaw v2026.9.7 supports browser identity and normal pairing over HTTP using pure-JavaScript Ed25519, so this package keeps device pairing enabled and does not use the retired `dangerouslyDisableDeviceAuth` setting. A first browser connection through Umbrel's proxy may require one-time approval. If the UI says `pairing required`, keep it open and, over SSH to Umbrel, run `sudo docker exec -it hermes-lab-openclaw_server_1 openclaw devices list`, then approve the exact request with `sudo docker exec -it hermes-lab-openclaw_server_1 openclaw devices approve <requestId>`. The Gateway token and Umbrel app-proxy login remain required. Plain HTTP is still unencrypted, so an on-path attacker could capture the token or modify the UI; keep this LAN-only, retain proxy authentication, and never publish the raw Gateway port. Prefer HTTPS when available.

A one-shot Compose service seeds the initial config before OpenClaw starts and preserves later edits; the Gateway container keeps the official entrypoint so its non-interactive Doctor repair runs on startup and image upgrades. To update OpenClaw, verify a newer official multi-architecture image digest, update the pinned image reference, and bump the app's manifest version so Umbrel offers an app update; do not rely on `openclaw update` inside the container, because the image is replaced when Umbrel recreates it.

## Research and references

- [Umbrel Community App Store template and format](https://github.com/getumbrel/umbrel-community-app-store)
- [Official Umbrel app packages and app standards](https://github.com/getumbrel/umbrel-apps)
- [Hermes Agent Docker setup](https://hermes-agent.nousresearch.com/docs/user-guide/docker)
- [OpenClaw releases](https://github.com/openclaw/openclaw/releases/latest)
- [OpenClaw Docker setup and browser image](https://docs.openclaw.ai/install/docker)
- [OpenClaw Control UI security and pairing](https://docs.openclaw.ai/web/control-ui/connect-and-pair)
- [OpenClaw Control UI over HTTP](https://docs.openclaw.ai/gateway/security/network-exposure#control-ui-over-http)

Umbrel's community-store convention is a root `umbrel-app-store.yml` plus one directory per app containing `umbrel-app.yml` and `docker-compose.yml`. The app directory and manifest ID share the app-store ID prefix. The compose package exposes the app through the standard `app_proxy` service.

## Validation

Run from this repository:

```sh
python3 scripts/validate.py
```

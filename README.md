# Hermes Lab Umbrel Community App Store

A community app store containing Hermes Agent and OpenClaw.

## Install on umbrelOS

1. In umbrelOS, open **App Store → Add a community app store** and enter `https://github.com/syntaxbube/umbrel-hermes-app-store`.
2. Install **Hermes Agent** and/or **OpenClaw Umbrel** from the Hermes Lab store.
3. Open the app and complete its dashboard setup. OpenClaw Umbrel provides a browser onboarding wizard and uses Umbrel login rather than a shared Gateway token.

The store ID is `hermes-lab`; Umbrel requires this prefix on each app ID.

## Container and browser

The app uses Nous Research's official `nousresearch/hermes-agent:latest` multi-architecture image. Its official Docker documentation states the image ships with full Chromium for Playwright/browser automation. `shm_size: 1gb` is set because Chromium needs shared memory. Hermes configuration and user data persist in the app data directory mounted at `/opt/data`.

The Umbrel app proxy routes the browser UI to the Hermes dashboard on container port `9119`. Open Hermes from its app tile in umbrelOS; this internal port is the proxy target and is not published as `umbrel.local:9119`. Keep Hermes as PID 1: its image entrypoint starts s6-overlay, which supervises the gateway and dashboard. Do not add Compose `init: true`, because that inserts another PID 1 and disables Hermes service supervision.

The dashboard has built-in Basic Auth enabled. The login name is `hermes`; the password is Umbrel's generated per-app `APP_PASSWORD`, with `defaultUsername: hermes` and `deterministicPassword: true` exposing those generated credentials in umbrelOS's default-credentials popup. The stable session-signing key uses Umbrel's per-app `APP_SEED`; no reusable password or signing key is committed to this repository. The API port `8642` is intentionally not published through the app proxy; expose it separately only if you understand the network/security implications and have a specific API client.

## OpenClaw

The new app ID is `hermes-lab-openclaw-umbrel`, display name **OpenClaw Umbrel**, version **2026.9.8**. It packages the reviewed [Umbrel integration](https://github.com/getumbrel/openclaw-umbrel/pull/98) with OpenClaw 2026.9.8. Source and the upstream MIT license are preserved in `build/openclaw-umbrel`. Our GitHub Actions workflow builds and tests native `linux/amd64` and `linux/arm64` images, then publishes the index to `ghcr.io/syntaxbube/openclaw-umbrel:2026.9.8`. Compose pins its verified index digest `sha256:2754e604a9d4a523dec67d5b1d821fde3c24bf708ca62def144c1440e622e3b6`. The image is anonymously pullable and includes Chromium and persistent Homebrew tooling.

Umbrel's authenticated app proxy routes to the setup/wrapper service on port `18789`. The underlying Gateway listens only on loopback port `18790`. Neither port is published by Compose; manifest port `18887` is the host-facing tile port. Configuration, workspace, npm tools and Homebrew files persist under `${APP_DATA_DIR}/data`, with the Homebrew subdirectory also mounted at `/home/linuxbrew`. A one-shot service initializes directory ownership for UID 1000. The image's wrapper initializes the home skeleton and supervises the Gateway.

**Security note:** The setup UI and Control UI are administrator interfaces. The wrapper asserts the authenticated Umbrel owner, strips spoofed identity/forwarding headers, checks browser origin, and automatically enrolls browser devices using trusted-proxy authentication. Internal CLI clients use a separately generated persistent password. `APP_SEED` is required for setup-terminal protection; no credentials are committed. Never disable Umbrel proxy authentication or publish the wrapper/Gateway directly. The upstream image intentionally allows passwordless sudo inside the container for tooling; do not mount Docker sockets, host directories or other apps' data. This container boundary is not a hardened sandbox against hostile agents. Prefer HTTPS and keep access private.

**Replacement scope:** Only the old `hermes-lab-openclaw` store entry is removed. This is a separate app, not an automatic update or data migration. Existing installed app data is untouched. Both entries use tile port `18887`; do not run both simultaneously. Preserve/back up existing data before any operator-managed migration. No deployment, reboot or timer changes are part of this publication.

For updates, edit the preserved build source, run the publication and runtime-verification workflows, verify anonymous image access and both architectures, then update the pinned digest and app version. Do not rely on self-updates inside the container.

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

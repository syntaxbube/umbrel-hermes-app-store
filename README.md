# Hermes Lab Umbrel Community App Store

A minimal Umbrel Community App Store containing Hermes Agent.

## Install on umbrelOS

1. In umbrelOS, open **App Store → Add a community app store** and enter `https://github.com/syntaxbube/umbrel-hermes-app-store`.
2. Install **Hermes Agent** from the Hermes Lab store.
3. Open the app and complete Hermes setup in its dashboard (select a provider/model and configure credentials there).

The store ID is `hermes-lab`; Umbrel requires this prefix on each app ID.

## Container and browser

The app uses Nous Research's official `nousresearch/hermes-agent:latest` multi-architecture image. Its official Docker documentation states the image ships with full Chromium for Playwright/browser automation. `shm_size: 1gb` is set because Chromium needs shared memory. Hermes configuration and user data persist in the app data directory mounted at `/opt/data`.

The Umbrel app proxy routes the browser UI to the Hermes dashboard on container port `9119`. The dashboard has built-in Basic Auth enabled: the login name is `hermes`, and its password is Umbrel's generated per-app `APP_PASSWORD`, shown by Umbrel in the app UI. The stable session-signing key uses Umbrel's per-app `APP_SEED`; no reusable password or signing key is committed to this repository. The API port `8642` is intentionally not published through the app proxy; expose it separately only if you understand the network/security implications and have a specific API client.

## Research and references

- [Umbrel Community App Store template and format](https://github.com/getumbrel/umbrel-community-app-store)
- [Official Umbrel app packages and app standards](https://github.com/getumbrel/umbrel-apps)
- [Hermes Agent Docker setup](https://hermes-agent.nousresearch.com/docs/user-guide/docker)

Umbrel's community-store convention is a root `umbrel-app-store.yml` plus one directory per app containing `umbrel-app.yml` and `docker-compose.yml`. The app directory and manifest ID share the app-store ID prefix. The compose package exposes the app through the standard `app_proxy` service.

## Validation

Run from this repository:

```sh
python3 scripts/validate.py
```

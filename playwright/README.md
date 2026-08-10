# Docs UI screenshots

Playwright harness that captures the third-party UIs our guides walk readers through, so those
images are **generated and version-controlled** rather than hand-captured.

Today that is the **Keycloak admin console**, used by
[the OAuth2 with Keycloak guide](../assets/kgw-docs/pages/security/oauth2-keycloak.md).

Every capture does two jobs at once:

- **Docs asset.** `npm run sync-docs` copies the baseline into `assets/img/`, where the guide embeds it.
- **Regression check.** `toHaveScreenshot()` diffs against the committed baseline, so a Keycloak
  release that renames a button turns into a reviewable image diff instead of a guide that quietly
  no longer matches the console.

The second job is the reason this exists. Every hand-captured image in this guide had drifted:
three showed the step *after* the one they illustrated, one showed a wildcard redirect URI that
contradicted the prose, and the guide told readers to click **Add realm** in a console whose
button says **Create realm**. Nothing catches that class of error except re-capturing.

## Quick start

Requires Docker and Node 18+ (this repo's `.nvmrc`-less default of Node 16 is too old for
Playwright 1.49; use `nvm use 22` or similar).

```sh
cd playwright
npm install
npx playwright install chromium

npm run test:keycloak     # capture and diff against committed baselines
npm run update:keycloak   # regenerate baselines after an intentional UI change
npm run sync-docs         # copy baselines into assets/img/
npm run report            # open the HTML report, including image diffs
```

The launcher starts Keycloak, seeds it, captures, and removes the container on exit. You do not
need a cluster, and you do not need the kgateway install from the guide — see below.

## How it works

```
npm run test:keycloak
  └─ playwright.config.ts resolves the Keycloak version from the docs
       assets/kgw-docs/versions/keycloak-version.md  →  quay.io/keycloak/keycloak:<version>
  └─ webServer runs scripts/serve-keycloak.sh
       docker run keycloak start-dev            (plain HTTP on :18080)
       kcadm: set master realm sslRequired=NONE (see "Gotchas")
       node scripts/seed-keycloak.mjs           (realm + client + user)
       waits for BOTH /realms/master AND /admin/master/console/
  └─ tests/keycloak.spec.ts drives the console and captures
  └─ __screenshots__/  ← baselines, the regression target
  └─ npm run sync-docs → assets/img/keycloak/  ← what the guide embeds
```

### Why the harness does not reproduce the guide's setup

The guide runs Keycloak **in a cluster, over HTTPS, with a self-signed certificate**, because
kgateway has to reach it over TLS. The harness runs it as **one container over plain HTTP**.

That divergence is deliberate. Nothing in these screenshots depends on how Keycloak is exposed —
the admin console renders identically either way — and dropping TLS removes a certificate
interstitial that a headless browser would otherwise have to click through. The harness captures
the *console*, not the *integration*. The integration is verified by running the guide.

If a future capture ever needs to show kgateway and Keycloak actually talking to each other, that
capture needs a cluster and belongs in a separate mode, not in this one.

### Why `provision`, and why no cron

This is the `provision` model from the docs skills: the harness runs the UI itself. That is
possible only because Keycloak is a single container with no control plane. If a UI we need later
requires a cluster and a licensed install, it belongs in an `attach`-style harness instead.

**There is deliberately no nightly cron.** The agentgateway harness crons because it installs
floating chart tags, so the same tag pulls a changing image and drift can appear with no git
event. Here the Keycloak version is pinned to an exact tag that the docs themselves declare, so
the pixels cannot change unless somebody edits a file in this repo. The workflow therefore
triggers on changes to the harness, the spec, or the version snippet — a cron would burn CI
minutes to re-prove the same bytes.

That is also why `@playwright/test` is pinned **exactly** (`1.49.0`, no caret). Nothing re-captures
on a schedule, so a caret that quietly pulled a new Chromium would leave the baselines stale with
no signal. Bump it deliberately and review the resulting diff.

## Baselines and platforms

Font anti-aliasing differs between macOS and Linux, so **CI on Linux owns the canonical
baselines.** Capture locally to iterate; let the workflow produce the set that gets merged. If you
regenerate on a Mac and commit, expect CI to show a whole-image diff that is not a real change.

Baseline filenames are platform-neutral (`snapshotPathTemplate` drops the `-darwin`/`-linux`
segment) so one committed set serves both.

## Projects are keyed by version, not theme

The agentgateway harness runs every spec twice, once per theme, because its UI has a theme
control. **The Keycloak 22 admin console has no dark theme** — verified against the
`keycloak-admin-ui` message bundle, which has no dark-mode string, and the shipped PatternFly
assets, whose only `pf-theme-dark` references are library internals with no user-facing control.
A dark project would capture identical pixels twice.

So the project is `keycloak-<docs-version>`, `docs-image-map.json` maps each image to a **single**
destination, and guides point both image shortcodes at the one asset:

```md
{{< reuse-image src="img/keycloak/realm-creation.png" >}}
{{< reuse-image-dark srcDark="img/keycloak/realm-creation.png" >}}
```

If a future Keycloak gains a dark console, add the theme dimension to `playwright.config.ts` and
widen the image map to the `{"light": …, "dark": …}` schema in the same change.

## Task: add a capture to the Keycloak guide

1. Add a `test(...)` to `tests/keycloak.spec.ts` that navigates to the screen and captures it.
   Reuse `login()`, `gotoConsole()`, and `settle()` from `fixtures/test.ts` rather than
   re-implementing the waiting.
2. If the screen needs an object to exist, seed it in `scripts/seed-keycloak.mjs`. If the screen
   *is* an object being created, fill the form and do not submit — that is how the existing
   create-realm, create-client, and create-user captures work.
3. Add the image to `docs-image-map.json`.
4. Reference it in the guide with the shortcode pair above.
5. `npm run update:keycloak && npm run sync-docs`, then review the image before committing.
6. Commit the spec, any seed change, the map entry, the baseline, the published image, and the
   guide change together.

## Task: bump the Keycloak version

1. Edit `assets/kgw-docs/versions/keycloak-version.md`. This harness reads that file, and the
   guide's YAML renders the same snippet, so the two cannot disagree.

   > The guide-side half of that wiring ships with the Keycloak guide corrections, not with this
   > harness. Until it lands, the guide hardcodes `quay.io/keycloak/keycloak:22.0` and you must
   > keep the two in step by hand.
2. `npm run update:keycloak && npm run sync-docs`.
3. **Review every image diff.** A diff means the console changed, which usually means the guide's
   click-path prose is now wrong too. Fixing the prose is the point of the review; regenerating
   the pixels is the easy half.
4. `assets/img/` is one flat, unversioned tree that every docs version references by filename. If
   older docs versions still document the old Keycloak, freeze the outgoing images into a dated
   bucket and repoint those versions **before** overwriting the bare files.

## Adding another third-party UI

1. Write `scripts/serve-<name>.sh` — start the UI, seed it, wait for health, clean up in a `trap`.
2. Register it in `SCRIPT_FOR` in `playwright.config.ts`.
3. Add `test:<name>` and `update:<name>` to `package.json`, and add both to `capture:all` and
   `update:all`, each preceded by `npm run clean`.

The `clean` between modes is not optional: launchers bind a fixed host port, so a leftover
container makes the next mode fail or, worse, capture the wrong UI.

## Gotchas

- **`sslRequired` blocks HTTP admin access.** Keycloak's master realm defaults to
  `sslRequired=external`, and Docker's port proxy rewrites the source address, so requests from
  the host do not qualify as loopback and get `HTTPS required` — for both the admin REST API and
  an admin-console login. The launcher relaxes it with `kcadm` *inside* the container, where the
  connection genuinely is loopback. This only ever touches the throwaway capture instance.
- **`/realms/master` answering 200 does not mean the console is up.** The console is a separate
  SPA. Gating only on the REST endpoint produced a cold-start capture with no sign-in button, so
  the launcher waits for `/admin/master/console/` too, and `settle()` waits for `document.fonts`.
- **The client secret is regenerated per install.** It is masked in `client-secret.png`. The seed
  also sets a fixed-length secret so the field's width does not shift between runs.
- **The test user is seeded without a password on purpose.** The Credentials tab offers
  **Set password** only while the user has none; once a credential exists the button becomes
  **Reset password** and the capture stops matching the guide's instruction.
- **PatternFly generates ids for some controls.** The Temporary toggle's id changes on every
  render, so the spec selects it by `aria-label`. Do not switch to an id-based selector.
- **Client authentication is on the wizard's second page**, not the first. Page 1 is General
  settings (Client ID), page 2 is Capability config (Client authentication, Standard flow, Direct
  access grants), page 3 is Login settings (Valid redirect URIs) and ends with **Save**, not
  **Next**. The guide got this wrong before the harness made the pages visible.

## Files

| Path | What it is |
| ---- | ---------- |
| `playwright.config.ts` | Version resolution, launcher selection, pinned viewport, project keying |
| `fixtures/test.ts` | `login()`, `gotoConsole()`, `settle()`, `maskClientSecret()` |
| `tests/keycloak.spec.ts` | The Keycloak admin console captures |
| `scripts/serve-keycloak.sh` | Launcher: run, relax `sslRequired`, seed, wait, clean up |
| `scripts/seed-keycloak.mjs` | Deterministic realm, client, audience mapper, and user |
| `scripts/resolve-version.mjs` | Reads the Keycloak version from the docs' version snippet |
| `scripts/sync-docs-images.mjs` | Publishes baselines into `assets/img/`; `--check` for CI |
| `docs-image-map.json` | Capture name → destination under `assets/img/` |
| `__screenshots__/` | Committed baselines. Never edit by hand. |

## npm scripts

| Script | What it does |
| ------ | ------------ |
| `test:keycloak` | Capture and diff against baselines |
| `update:keycloak` | Regenerate baselines |
| `capture:all` / `update:all` | Same, across every mode, with `clean` between |
| `clean` | Remove a leftover capture container holding the port |
| `sync-docs` | Copy baselines into `assets/img/` (`--check` to verify only) |
| `report` | Open the HTML report, including image diffs |

## Environment variables

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `KEYCLOAK_VERSION` | from the docs snippet | Image tag to capture against |
| `KEYCLOAK_IMAGE` | derived | Full image reference, overriding repo and tag |
| `UI_HOST_PORT` | `18080` | Host port, chosen to avoid a local Keycloak on 8080 |
| `UI_BASE_URL` | `http://localhost:$UI_HOST_PORT` | Point at a Keycloak you started yourself |
| `DOC_VERSION` | `latest` | Which docs version line the baselines belong to |
| `CAPTURE_MODE` | `keycloak` | Which UI to bring up |

`webServer.reuseExistingServer` is on, so you can run `bash scripts/serve-keycloak.sh` in one
terminal and iterate on a spec in another without paying container startup each time.

## Known limitations

- **Only the admin console is captured.** The guide's kgateway resources are verified by running
  the guide against a cluster, not here.
- **No cluster-based captures.** Any future capture showing kgateway and Keycloak interacting
  needs a different mode with a real cluster.
- **Node 16 cannot run this.** Playwright 1.49 needs Node 18+.

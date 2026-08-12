import { defineConfig, devices } from '@playwright/test';
import { resolveKeycloakVersion } from './scripts/resolve-version.mjs';

/**
 * Screenshot harness for the third-party UIs that kgateway guides walk the reader through.
 *
 * Today that means the Keycloak admin console, used by the OAuth2 with Keycloak guide. The
 * model is `provision`: the harness runs the UI itself via Playwright's `webServer`, seeds it
 * to a known state, captures, and tears it down. Keycloak runs as a single container with
 * `start-dev`, so no cluster and no control plane are involved — that property is what makes
 * this model possible. See README.md § "Why provision, and why no cron".
 *
 * Each capture serves two purposes:
 *   - docs assets:  `npm run sync-docs` copies baselines into assets/img/ via docs-image-map.json
 *   - regression:   toHaveScreenshot() diffs against the committed baseline, so a Keycloak
 *                   version bump that renames a button surfaces as a reviewable image diff
 *                   rather than as a guide that silently no longer matches the console
 *
 * Env knobs:
 *   KEYCLOAK_VERSION  image tag to run. Defaults to the version the docs install, read from
 *                     assets/kgw-docs/versions/keycloak-version.md, so a capture always matches
 *                     what a reader gets. Override only for a one-off comparison.
 *   KEYCLOAK_IMAGE    full image reference, overriding both the default repo and the tag.
 *   UI_HOST_PORT      host port mapped to the container's 8080 (default 18080, chosen so it
 *                     does not collide with a Keycloak a developer is running on 8080)
 *   UI_BASE_URL       full base URL; defaults to http://localhost:${UI_HOST_PORT}
 *   DOC_VERSION       which docs version line the baselines belong to (default `latest`)
 *   CAPTURE_MODE      which UI the webServer brings up. Only `keycloak` exists today; the map
 *                     below is the extension point for the next third-party UI.
 */

// Which docs version line we are capturing for. Part of the project name, so two docs
// versions that document different Keycloak releases keep independent baselines.
const VERSION = process.env.DOC_VERSION || 'latest';
const HOST_PORT = process.env.UI_HOST_PORT || '18080';
const BASE_URL = process.env.UI_BASE_URL || `http://localhost:${HOST_PORT}`;
const MODE = process.env.CAPTURE_MODE || 'keycloak';

// KEYCLOAK_IMAGE wins outright; otherwise the tag comes from the docs' version snippet so the
// screenshots and the guide's YAML can never drift apart.
const KEYCLOAK_VERSION = process.env.KEYCLOAK_VERSION || resolveKeycloakVersion();

// Each mode is a launcher that starts its UI, seeds it, waits for health, and cleans up in a
// trap. Adding a third-party UI means adding a launcher and an entry here.
const SCRIPT_FOR: Record<string, string> = {
  keycloak: 'serve-keycloak.sh',
};

const script = SCRIPT_FOR[MODE];
if (!script) {
  throw new Error(
    `Unknown CAPTURE_MODE "${MODE}". Known modes: ${Object.keys(SCRIPT_FOR).join(', ')}`,
  );
}

export default defineConfig({
  testDir: './tests',
  snapshotDir: './__screenshots__',
  // Platform-neutral baseline names (no -darwin/-linux suffix). CI on Linux produces the
  // canonical baselines; dropping the platform segment means one committed set serves both CI
  // and local preview, and sync-docs is never ambiguous about which file to publish.
  snapshotPathTemplate:
    '{snapshotDir}/{testFileDir}/{testFileName}-snapshots/{arg}{-projectName}{ext}',
  fullyParallel: false,
  // One worker. The specs drive a single shared Keycloak instance and mutate its state (they
  // create a realm, a client, and a user), so running them concurrently would race.
  workers: 1,
  forbidOnly: !!process.env.CI,
  reporter: [['html', { open: 'never' }], ['list']],

  webServer: {
    command: `bash ./scripts/${script}`,
    // Gate on the SEEDED realm's discovery document, not on /realms/master.
    //
    // /realms/master answers as soon as Keycloak boots, which is before the launcher has relaxed
    // sslRequired and seeded the realm. Playwright would then start the first test into a console
    // still returning `HTTPS required`, with no sign-in form — a failure that looked like a cold
    // start problem but was really a race against our own setup. This URL 404s until
    // seed-keycloak.mjs has created `myrealm`, so readiness now means "seeded and ready to
    // photograph". Keep it in step with the realm name in scripts/seed-keycloak.mjs.
    url: `${BASE_URL}/realms/myrealm/.well-known/openid-configuration`,
    // Attach to an already-running UI, so you can start the launcher yourself and iterate on a
    // spec without paying container startup on every run.
    reuseExistingServer: true,
    timeout: 240_000, // Keycloak boots the built-in dev database on first start
    stdout: 'pipe',
    stderr: 'pipe',
    env: {
      KEYCLOAK_VERSION,
      UI_HOST_PORT: HOST_PORT,
      ...(process.env.KEYCLOAK_IMAGE ? { KEYCLOAK_IMAGE: process.env.KEYCLOAK_IMAGE } : {}),
    },
  },

  use: {
    baseURL: BASE_URL,
    // Pin everything that affects pixels, so baselines stay stable across runs and machines.
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
    // The admin console is English-only in these guides; pinning the locale keeps button
    // labels stable regardless of the CI runner's environment.
    locale: 'en-US',
    timezoneId: 'UTC',
  },

  expect: {
    toHaveScreenshot: {
      maxDiffPixelRatio: 0.01,
      animations: 'disabled',
    },
  },

  // Projects are keyed by UI and docs version — `keycloak-latest` — and NOT by theme. The
  // Keycloak 22 admin console has no theme control and no dark stylesheet (verified against
  // the keycloak-admin-ui message bundle and the shipped PatternFly assets), so a dark project
  // would capture the same pixels twice. Guides therefore point both reuse-image shortcodes at
  // the one asset. If a future Keycloak gains a dark console, add the theme dimension here and
  // widen docs-image-map.json to the light/dark schema at the same time.
  projects: [{ name: `${MODE}-${VERSION}`, use: { ...devices['Desktop Chrome'] } }],
});

import { test, expect, login, gotoConsole, settle, maskClientSecret } from '../fixtures/test';

/**
 * Captures for the OAuth2 with Keycloak guide —
 * assets/kgw-docs/pages/security/oauth2-keycloak.md § "Configure Keycloak".
 *
 * Run with `npm run test:keycloak`, or `npm run update:keycloak` to regenerate baselines. The
 * webServer launcher (scripts/serve-keycloak.sh) starts Keycloak and seeds the realm, the
 * confidential client, and the test user before any spec runs.
 *
 * Each capture shows the screen the guide's corresponding step describes. Steps that CREATE an
 * object are captured by filling the form and never submitting it, which is why the seeded realm
 * does not make them unreachable. Steps that inspect an EXISTING object rely on the seed.
 *
 * Images (light only — the Keycloak 22 console has no dark theme; see playwright.config.ts):
 *   keycloak-login.png              — the admin console sign-in page
 *   realm-creation.png              — Create realm, name filled
 *   client-creation.png             — Create client page 1, General settings, Client ID filled
 *   client-capability-config.png    — Create client page 2, Client authentication enabled
 *   client-redirect-uri.png         — Create client page 3, Login settings, redirect URI filled
 *   client-secret.png               — the client's Credentials tab (secret masked)
 *   user-created.png                — Create user, username filled
 *   user-password.png               — Set password dialog, Temporary off
 */

const REALM = 'myrealm';
const CLIENT_ID = 'kgateway-client';
const USERNAME = 'testuser';
// The exact value the guide tells the reader to register. Keeping it identical here means the
// screenshot cannot disagree with the prose.
const REDIRECT_URI = 'https://www.example.com/oauth2/redirect';

test('the admin console sign-in page', async ({ page }) => {
  await page.goto('/admin/master/console/');
  await settle(page);
  // Generous timeout: on a cold container this is the first request the console ever serves.
  await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible({ timeout: 60_000 });
  await expect(page).toHaveScreenshot('keycloak-login.png', { fullPage: true });
});

test('creating a realm', async ({ page }) => {
  await login(page);
  await gotoConsole(page, '/master/add-realm');
  const name = page.getByLabel(/realm name/i);
  await expect(name).toBeVisible();
  await name.fill(REALM);
  await expect(page).toHaveScreenshot('realm-creation.png', { fullPage: true });
});

test('creating a client: general settings', async ({ page }) => {
  await login(page);
  await gotoConsole(page, `/${REALM}/clients/add-client`);
  const clientId = page.getByLabel(/client id/i).first();
  await expect(clientId).toBeVisible();
  await clientId.fill(CLIENT_ID);
  await expect(page).toHaveScreenshot('client-creation.png', { fullPage: true });
});

test('creating a client: capability config', async ({ page }) => {
  await login(page);
  await gotoConsole(page, `/${REALM}/clients/add-client`);
  await page.getByLabel(/client id/i).first().fill(CLIENT_ID);
  await page.getByRole('button', { name: /^next$/i }).click();

  // Client authentication lives on this page, not on General settings. Turning it on is what
  // makes the client confidential and gives it the secret the guide later copies.
  const clientAuth = page.locator('#kc-authentication-switch, [name="publicClient"]').first();
  await expect(clientAuth).toBeVisible();
  if (!(await clientAuth.isChecked())) {
    await clientAuth.click({ force: true });
  }
  await expect(page.getByText(/standard flow/i)).toBeVisible();
  await expect(page).toHaveScreenshot('client-capability-config.png', { fullPage: true });
});

test('creating a client: login settings with the redirect URI', async ({ page }) => {
  await login(page);
  await gotoConsole(page, `/${REALM}/clients/add-client`);
  await page.getByLabel(/client id/i).first().fill(CLIENT_ID);
  await page.getByRole('button', { name: /^next$/i }).click();
  await page.getByRole('button', { name: /^next$/i }).click();

  const redirect = page.getByLabel(/valid redirect uris/i).first();
  await expect(redirect).toBeVisible();
  await redirect.fill(REDIRECT_URI);
  await expect(page).toHaveScreenshot('client-redirect-uri.png', { fullPage: true });
});

test('the client credentials tab', async ({ page }) => {
  await login(page);
  await gotoConsole(page, `/${REALM}/clients`);
  await page.getByRole('link', { name: CLIENT_ID }).click();
  await page.getByRole('tab', { name: /credentials/i }).click();
  await page.waitForLoadState('networkidle');
  await expect(page.getByText(/client authenticator/i)).toBeVisible();
  await expect(page).toHaveScreenshot('client-secret.png', {
    fullPage: true,
    ...maskClientSecret(page),
  });
});

test('creating a user', async ({ page }) => {
  await login(page);
  await gotoConsole(page, `/${REALM}/users/add-user`);
  const username = page.getByLabel(/^username/i).first();
  await expect(username).toBeVisible();
  await username.fill(USERNAME);
  await expect(page).toHaveScreenshot('user-created.png', { fullPage: true });
});

test('setting the user password', async ({ page }) => {
  await login(page);
  await gotoConsole(page, `/${REALM}/users`);
  await page.getByRole('link', { name: USERNAME }).click();
  await page.getByRole('tab', { name: /credentials/i }).click();
  await page.waitForLoadState('networkidle');

  // The seed leaves the user without a credential, so this control reads "Set password" and
  // matches the guide. If it ever reads "Reset password", the seed set one by mistake.
  await page.getByRole('button', { name: /set password/i }).first().click();
  const dialog = page.getByRole('dialog');
  await expect(dialog).toBeVisible();

  // Target the inputs by id rather than by label. Both fields' accessible names begin with
  // "Password" and carry the required marker, so a label regex either matches both or neither.
  await dialog.locator('input#password').fill('password');
  await dialog.locator('input#passwordConfirmation').fill('password');

  // The guide tells the reader to turn Temporary off, so capture it off. PatternFly gives this
  // checkbox a generated id that changes on every render, so select it by its aria-label; the id
  // is not stable enough to rely on and never appears in the capture.
  const temporary = dialog.locator('input[type="checkbox"][aria-label="Temporary"]');
  await expect(temporary).toBeVisible();
  if (await temporary.isChecked()) {
    await temporary.click({ force: true });
  }
  await expect(temporary).not.toBeChecked();

  await expect(page).toHaveScreenshot('user-password.png', { fullPage: true });
});

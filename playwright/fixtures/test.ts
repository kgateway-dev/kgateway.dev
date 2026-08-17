import { test as base, expect, type Page } from '@playwright/test';

export { expect };
export const test = base;

const ADMIN_USER = 'admin';
const ADMIN_PASSWORD = 'admin';

/**
 * Wait until the page is safe to photograph.
 *
 * A cold Keycloak serves the console shell before its stylesheets and webfonts finish loading, so
 * a capture taken immediately after `goto` can show unstyled or fallback-font text. CI always
 * starts cold, which is exactly where that bites. Settling on both the network and
 * `document.fonts` removes the whole class of first-run diff.
 */
export async function settle(page: Page): Promise<void> {
  await page.waitForLoadState('networkidle');
  await page.evaluate(() => document.fonts.ready.then(() => undefined));
}

/**
 * Log in to the Keycloak admin console and wait for it to settle.
 *
 * The console is a single-page app, so `networkidle` alone is not enough — the shell renders
 * before the realm list resolves, and a capture taken too early catches a spinner. Waiting for
 * the realm selector proves the app is interactive.
 */
export async function login(page: Page): Promise<void> {
  await page.goto('/admin/master/console/');
  await settle(page);
  await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible({ timeout: 60_000 });
  await page.getByLabel(/username/i).fill(ADMIN_USER);
  await page.getByLabel(/password/i).fill(ADMIN_PASSWORD);
  await page.getByRole('button', { name: /sign in/i }).click();
  await settle(page);
  await expect(page.getByTestId('realmSelector')).toBeVisible({ timeout: 30_000 });
}

/**
 * Navigate to a console route and wait for the SPA to finish rendering it.
 *
 * The admin console routes on the URL fragment, so `page.goto` to a new fragment does not always
 * remount the view. Loading the route directly and then waiting on a settled network keeps each
 * capture independent of whatever the previous test left on screen.
 */
export async function gotoConsole(page: Page, fragment: string): Promise<void> {
  await page.goto(`/admin/master/console/#${fragment}`);
  await settle(page);
  // PatternFly animates form and modal entry; without this the first capture of a route can
  // catch a partially transitioned card.
  await page.waitForTimeout(1_000);
}

/**
 * Mask the generated client secret.
 *
 * Keycloak regenerates the secret on every install, so the Credentials tab is the one screen in
 * this set whose pixels are not reproducible. The field renders as dots, but the value is
 * present in the DOM and a future Keycloak could reveal it by default, so mask the input rather
 * than trusting the obfuscation. Spread into toHaveScreenshot().
 */
export function maskClientSecret(page: Page) {
  return {
    mask: [page.locator('input#kc-client-secret, input[name="secret"]')],
  };
}

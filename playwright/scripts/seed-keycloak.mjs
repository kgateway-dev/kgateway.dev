/**
 * Seed Keycloak with the objects the OAuth2 with Keycloak guide creates, so the captures that
 * show an *existing* object (the client Credentials tab, the user Credentials tab) have
 * something to show.
 *
 * The captures that show an object being *created* — the Create realm page, the Create client
 * wizard, the Create user form — are taken by filling the form and not submitting it. That is
 * why this script seeds a realm and still leaves those screens reachable: the spec navigates to
 * the create screen, fills it, captures, and never clicks Save. Nothing here duplicates what a
 * spec is meant to demonstrate.
 *
 * Everything is idempotent, so re-running against a warm container is safe.
 */

const BASE = process.env.KEYCLOAK_BASE_URL || 'http://localhost:18080';
const REALM = 'myrealm';
const CLIENT_ID = 'kgateway-client';
const USERNAME = 'testuser';

// Fixed so the Credentials tab renders a stable width. The value is masked in the capture
// anyway, but a fixed length keeps the layout from shifting between runs.
const CLIENT_SECRET = 'kgateway-docs-fixed-client-secret';

async function token() {
  const res = await fetch(`${BASE}/realms/master/protocol/openid-connect/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: 'admin-cli',
      username: 'admin',
      password: 'admin',
      grant_type: 'password',
    }),
  });
  if (!res.ok) {
    throw new Error(`admin login failed: ${res.status} ${await res.text()}`);
  }
  return (await res.json()).access_token;
}

async function api(tok, path, { method = 'GET', body } = {}) {
  const res = await fetch(`${BASE}/admin${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${tok}`,
      ...(body ? { 'Content-Type': 'application/json' } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  // 409 means the object already exists, which is the normal path on a re-run.
  if (!res.ok && res.status !== 409) {
    throw new Error(`${method} ${path} failed: ${res.status} ${await res.text()}`);
  }
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

const tok = await token();

// The realm the guide creates. Client and user screens live inside it.
await api(tok, '/realms', { method: 'POST', body: { realm: REALM, enabled: true } });

// The confidential client, with the exact redirect URI the guide tells the reader to register.
// `standardFlowEnabled` drives the authorization code flow; `directAccessGrantsEnabled` is the
// password grant the access token steps use.
await api(tok, `/realms/${REALM}/clients`, {
  method: 'POST',
  body: {
    clientId: CLIENT_ID,
    enabled: true,
    publicClient: false,
    standardFlowEnabled: true,
    directAccessGrantsEnabled: true,
    secret: CLIENT_SECRET,
    redirectUris: ['https://www.example.com/oauth2/redirect'],
  },
});

// The audience mapper the guide adds so tokens carry the client ID in `aud`.
const clients = await api(tok, `/realms/${REALM}/clients?clientId=${CLIENT_ID}`);
const cid = clients?.[0]?.id;
if (cid) {
  await api(tok, `/realms/${REALM}/clients/${cid}/protocol-mappers/models`, {
    method: 'POST',
    body: {
      name: 'kgateway-audience',
      protocol: 'openid-connect',
      protocolMapper: 'oidc-audience-mapper',
      config: { 'included.client.audience': CLIENT_ID, 'access.token.claim': 'true' },
    },
  });
}

// The test user, deliberately WITHOUT a password. The guide's next step is to set one, and the
// Credentials tab offers "Set password" only while the user has none — once a credential exists
// the control becomes "Reset password" and the capture would no longer match the instruction.
await api(tok, `/realms/${REALM}/users`, {
  method: 'POST',
  body: { username: USERNAME, enabled: true },
});

console.log(`seeded realm ${REALM}, client ${CLIENT_ID}, user ${USERNAME} (no credential)`);

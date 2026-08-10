#!/usr/bin/env bash
# Start the Keycloak admin console for screenshot capture, seed it to the state the OAuth2 with
# Keycloak guide describes, and hold the foreground until Playwright tears the webServer down.
#
# Keycloak runs over plain HTTP here, unlike the guide, which serves it over HTTPS with a
# self-signed certificate inside the cluster. That difference is deliberate and does not show in
# the captures: the admin console renders identically either way, and dropping TLS removes a
# certificate warning that a headless browser would otherwise have to click through. Nothing in
# these screenshots depends on how Keycloak is exposed.
set -euo pipefail

CONTAINER=kgw-docs-keycloak
HOST_PORT="${UI_HOST_PORT:-18080}"
VERSION="${KEYCLOAK_VERSION:?KEYCLOAK_VERSION must be set; playwright.config.ts resolves it from the docs}"
IMAGE="${KEYCLOAK_IMAGE:-quay.io/keycloak/keycloak:${VERSION}}"
BASE_URL="http://localhost:${HOST_PORT}"

cleanup() {
  docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

# A leftover container from a previous run holds the port and would otherwise make this run
# either fail to bind or, worse, capture the previous version's UI.
cleanup

echo "==> starting ${IMAGE} on ${BASE_URL}"
docker run -d --rm --name "$CONTAINER" \
  -p "${HOST_PORT}:8080" \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  "$IMAGE" start-dev >/dev/null

echo "==> waiting for Keycloak to answer on ${BASE_URL}"
for i in $(seq 1 80); do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 "${BASE_URL}/realms/master" 2>/dev/null || true)
  if [ "$code" = "200" ]; then
    echo "==> Keycloak ready after ${i} attempt(s)"
    break
  fi
  if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
    echo "!! the Keycloak container exited during startup; logs follow" >&2
    docker logs "$CONTAINER" 2>&1 | tail -40 >&2 || true
    exit 1
  fi
  sleep 3
done

if [ "${code:-}" != "200" ]; then
  echo "!! Keycloak did not become ready at ${BASE_URL}" >&2
  docker logs "$CONTAINER" 2>&1 | tail -40 >&2 || true
  exit 1
fi

# /realms/master answers as soon as the REST layer is up, which is earlier than the admin console
# being served — the console is a separate single-page app with its own resources. Capturing
# against that window produced an empty page with no sign-in button. Gate on the console itself.
echo "==> waiting for the admin console to be served"
for i in $(seq 1 40); do
  console=$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 "${BASE_URL}/admin/master/console/" 2>/dev/null || true)
  if [ "$console" = "200" ]; then
    echo "==> admin console ready after ${i} attempt(s)"
    break
  fi
  sleep 2
done
if [ "${console:-}" != "200" ]; then
  echo "!! the admin console did not become ready at ${BASE_URL}/admin/master/console/" >&2
  exit 1
fi

# Keycloak's master realm defaults to sslRequired=external, which rejects both the admin REST
# API and an admin-console login arriving over HTTP. Docker's port proxy rewrites the source
# address, so requests from the host do not qualify as loopback and the default blocks them with
# `HTTPS required`. Relax it from inside the container, where the connection genuinely is
# loopback and therefore permitted. This only ever applies to this throwaway capture instance.
echo "==> relaxing sslRequired on the master realm for HTTP capture"
docker exec "$CONTAINER" /opt/keycloak/bin/kcadm.sh config credentials \
  --server http://localhost:8080 --realm master --user admin --password admin >/dev/null
docker exec "$CONTAINER" /opt/keycloak/bin/kcadm.sh update realms/master -s sslRequired=NONE >/dev/null

echo "==> seeding the realm, client, and user the guide creates"
KEYCLOAK_BASE_URL="$BASE_URL" node "$(dirname "$0")/seed-keycloak.mjs"

echo "==> ready for capture; holding the container in the foreground"
# Playwright kills this process group when the run finishes, and the trap removes the container.
docker logs -f "$CONTAINER" >/dev/null 2>&1 || sleep infinity

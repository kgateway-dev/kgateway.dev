import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));

/**
 * The Keycloak version the docs install, read from the same snippet the guide's YAML renders.
 *
 * This is deliberately not a constant in this repo's JavaScript. The guide tells the reader to
 * deploy `quay.io/keycloak/keycloak:<version>` by reusing this snippet, so reading it here is
 * what guarantees the screenshots show the console the reader actually sees. Bumping the
 * snippet bumps both at once, and the resulting image diff is the review.
 */
export function resolveKeycloakVersion() {
  const path = resolve(HERE, '../../assets/kgw-docs/versions/keycloak-version.md');
  let raw;
  try {
    raw = readFileSync(path, 'utf8');
  } catch (err) {
    throw new Error(
      `Could not read the Keycloak version snippet at ${path}. The harness reads the version ` +
        `from the docs rather than hardcoding it, so this file must exist. Original error: ${err.message}`,
    );
  }

  const version = raw.trim();

  // The snippet is plain text on purpose. Version snippets elsewhere in this repo wrap values in
  // {{< version include-if="..." >}} shortcodes for per-docs-version values; if this one ever
  // grows one, the harness must learn to evaluate it rather than silently pass a shortcode to
  // `docker run`.
  if (!/^[\w][\w.-]*$/.test(version)) {
    throw new Error(
      `The Keycloak version snippet at ${path} is not a bare version string (got ${JSON.stringify(
        version,
      )}). If it now uses a Hugo shortcode, teach resolveKeycloakVersion() to resolve it for ` +
        `the DOC_VERSION being captured.`,
    );
  }

  return version;
}

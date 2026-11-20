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

  // The snippet can hold per-docs-version values in {{% version include-if="..." %}} or
  // exclude-if blocks, for example when older docs versions keep an older Keycloak. Evaluate
  // them for the DOC_VERSION being captured, the way the site's version shortcode would.
  const docVersion = process.env.DOC_VERSION || 'latest';
  const version = evaluateVersionBlocks(raw, versionTokens(docVersion)).trim();

  // Anything left that is not a bare version means a shortcode form this resolver does not
  // understand. Fail rather than silently pass a shortcode to `docker run`.
  if (!/^[\w][\w.-]*$/.test(version)) {
    throw new Error(
      `The Keycloak version snippet at ${path} did not resolve to a bare version string for ` +
        `DOC_VERSION=${docVersion} (got ${JSON.stringify(version)}). Only include-if and ` +
        `exclude-if version blocks are understood.`,
    );
  }

  return version;
}

const BLOCK_RE =
  /\{\{[%<]\s*version\s+(include-if|exclude-if)="([^"]*)"\s*[%>]\}\}([\s\S]*?)\{\{[%<]\s*\/version\s*[%>]\}\}/g;

/** Keep each version block's content when its condition holds for `tokens`, else drop it. */
export function evaluateVersionBlocks(text, tokens) {
  return text.replace(BLOCK_RE, (_, kind, list, inner) => {
    const listed = list.split(',').map((s) => s.trim()).some((v) => tokens.includes(v));
    return (kind === 'include-if') === listed ? inner : '';
  });
}

/**
 * The names a docs version line answers to in a version block: the DOC_VERSION itself and its
 * `version`/`linkVersion` pair from hugo.yaml, so `latest` also matches `2.5.x`.
 */
export function versionTokens(docVersion, hugoYaml = readHugoYaml()) {
  const tokens = new Set([docVersion]);
  let entry = null;
  const flush = () => {
    if (entry && (entry.version === docVersion || entry.link === docVersion)) {
      if (entry.version) tokens.add(entry.version);
      if (entry.link) tokens.add(entry.link);
    }
  };
  for (const line of hugoYaml.split('\n')) {
    const v = line.match(/^\s*-\s*version:\s*"?([^"#\s]+)"?/);
    if (v) {
      flush();
      entry = { version: v[1], link: null };
      continue;
    }
    const l = line.match(/^\s*linkVersion:\s*"?([^"#\s]+)"?/);
    if (l && entry) entry.link = l[1];
  }
  flush();
  return [...tokens];
}

function readHugoYaml() {
  try {
    return readFileSync(resolve(HERE, '../../hugo.yaml'), 'utf8');
  } catch {
    return '';
  }
}

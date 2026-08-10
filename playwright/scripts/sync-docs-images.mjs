/**
 * Copy captured baselines into the docs image tree, per docs-image-map.json.
 *
 * Baselines under __screenshots__/ are the source of truth and the regression target; the copies
 * under assets/img/ are what the guides embed. Never edit either by hand — change the spec and
 * re-capture. Run after a capture:
 *
 *   npm run test:keycloak && npm run sync-docs
 *
 * Pass --check to verify the published copies match the baselines without writing anything,
 * which is what CI uses to decide whether the images drifted.
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync } from 'node:fs';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const HARNESS = resolve(HERE, '..');
const REPO = resolve(HARNESS, '..');
const CHECK = process.argv.includes('--check');

const map = JSON.parse(readFileSync(join(HARNESS, 'docs-image-map.json'), 'utf8'));
const project = map.project;
if (!project) {
  throw new Error('docs-image-map.json must name the Playwright `project` whose baselines publish.');
}

/**
 * Find a baseline by name. Playwright nests baselines under a per-spec directory and suffixes the
 * file with the project name, so resolve by walking rather than by assuming one layout — that way
 * adding a second spec file does not silently stop publishing.
 */
function findBaseline(imageName) {
  const stem = imageName.replace(/\.png$/, '');
  const wanted = `${stem}-${project}.png`;
  const root = join(HARNESS, '__screenshots__');
  const stack = [root];
  while (stack.length) {
    const dir = stack.pop();
    if (!existsSync(dir)) continue;
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const full = join(dir, entry.name);
      if (entry.isDirectory()) stack.push(full);
      else if (entry.name === wanted) return full;
    }
  }
  return null;
}

let copied = 0;
const missing = [];
const drifted = [];

for (const [imageName, destRel] of Object.entries(map.images)) {
  const src = findBaseline(imageName);
  if (!src) {
    missing.push(imageName);
    continue;
  }
  const dest = join(REPO, destRel);
  const bytes = readFileSync(src);

  if (CHECK) {
    if (!existsSync(dest) || !readFileSync(dest).equals(bytes)) drifted.push(destRel);
    continue;
  }

  mkdirSync(dirname(dest), { recursive: true });
  writeFileSync(dest, bytes);
  copied += 1;
  console.log(`  ${imageName} -> ${destRel}`);
}

if (missing.length) {
  console.error(
    `\n!! no baseline found for: ${missing.join(', ')}\n` +
      `   Expected files named <image>-${project}.png under __screenshots__/.\n` +
      `   Run the capture for the matching mode first, or fix "project" in docs-image-map.json.`,
  );
  process.exitCode = 1;
}

if (CHECK) {
  if (drifted.length) {
    console.error(`\n!! published images differ from the baselines:\n   ${drifted.join('\n   ')}`);
    process.exitCode = 1;
  } else if (!missing.length) {
    console.log('published images are up to date with the baselines');
  }
} else {
  console.log(`\ncopied ${copied} image(s) into assets/img/`);
}

---
name: fix-broken-links
description: Review a Lychee link checker report from a GitHub issue or CI run and propose fixes for errors, warnings (broken anchors), and redirects in the kgateway.dev Hugo docs repo. Use when the user asks to "fix broken links", "review the link report", "triage link checker issues", or points at a link checker CI run or issue (for example kgateway-dev/kgateway.dev#123 or a GitHub Actions run URL).
version: 1.0.0
---

# Fix broken links skill

Use this skill when the user provides a Lychee link checker report (usually from a GitHub Actions run or issue) and asks to triage or fix the findings in the kgateway.dev Hugo docs repo.

The report has three sections: **Errors**, **Warnings (broken anchors)**, and **Redirects**. Each bullet contains the link, followed by `Found on:` with one or more source HTML paths under `public/`.

---

## Input

The user will give you a link to a GitHub Actions run or issue, or paste the report body.

If given a CI run URL, download the report artifact:

```sh
gh run download <run-id> --repo kgateway-dev/kgateway.dev --name link-checker-assets --dir /tmp/kgw-links
cat /tmp/kgw-links/kgateway-oss-links.md
```

If given an issue URL:

```sh
gh issue view <N> --repo kgateway-dev/kgateway.dev --json body -q .body
```

---

## Repo structure

### Content layout

The site has two doc sections under `content/docs/`:

- **`envoy/`** — Kgateway with Envoy proxy docs (primary). Contains versioned subdirectories like `main/`, `latest/`, plus older version directories.
- **`agentgateway/`** — Agentgateway API reference subset. Contains versioned subdirectories.
- **`blog/`**, **`resources/`**, **`learn/`** — Non-versioned sections

To see which versions currently exist:

```sh
ls content/docs/envoy/
cat versions.json
```

### Shared content

Shared content lives in `assets/docs/`:

- **`assets/docs/pages/`** — Full page bodies reused across versions via `{{</* reuse "docs/pages/..." */>}}`
- **`assets/docs/snippets/`** — Smaller fragments reused via `{{</* reuse "docs/snippets/..." */>}}`

**Always edit the shared file, not the thin content wrapper.** Editing the shared file fixes all versions that reuse it.

### Enterprise docs sharing

This repo is imported as a Hugo module by `solo-io/docs` (the enterprise kgateway docs). Shared assets under `assets/docs/` are consumed by both sites. When fixing links in shared assets, verify that:

- The target page exists on both OSS (kgateway.dev) and enterprise (docs.solo.io/kgateway)
- If the page only exists on one site, use version or conditional-text shortcodes to gate the link
- The enterprise site uses `simple/` and `staged/` subdirectories under `transformations/`, while OSS has a flat structure. Hugo aliases on the OSS pages redirect `simple/X` to `X`. Do not change the shared asset paths.

---

## Version system — critical details

### Version mapping

The `version` shortcode resolves versions from the URL path and matches against **TOML `version` values**, NOT `linkVersion` values. Read the current mapping from `versions.json` at the repo root:

```sh
cat versions.json
```

Each entry has a `version` (TOML value like `2.3.x`) and a `linkVersion` (URL path segment like `main` or `latest`).

**Always use TOML `version` values in `include-if` and `exclude-if` shortcode parameters.** Using `linkVersion` values like `latest` or `main` will NOT match and the conditional will silently fail.

For example, if `versions.json` maps `latest` to TOML version `2.2.x`:

Correct: `{{</* version exclude-if="2.0.x,2.1.x" */>}}`
Wrong: `{{</* version exclude-if="2.0.x,latest" */>}}`

Always check `versions.json` for the current mapping before writing version conditionals.

### Version-conditional links

When a shared asset links to a page that exists on some versions but not others, or that moved paths between versions, wrap the link in version conditionals using TOML version values:

```
{{</* version include-if="<toml-versions-where-path-A-exists>" */>}}[Link]({{</* link-hextra path="/path/A" */>}}){{</* /version */>}}{{</* version exclude-if="<same-versions>" */>}}[Link]({{</* link-hextra path="/path/B" */>}}){{</* /version */>}}
```

Do NOT use Hugo aliases to paper over path differences between versions. Use version conditionals instead so the intent is explicit.

### Checking for cross-version path differences

Content restructuring between versions is common and is the primary source of broken links from shared assets. Before fixing a broken link, check if the target page exists at a different path on the affected version:

```sh
# Check where a page lives across all versions
find content/docs/envoy -name "selfmanaged*" -type f
```

### Checking for missing features on older versions

When a shared asset references a page that doesn't exist on an older version, the feature likely didn't exist in that release. Wrap the link in a `version exclude-if` conditional listing the older TOML versions where the page is missing. To confirm:

```sh
# Check if a page exists on a specific version
ls content/docs/envoy/2.0.x/traffic-management/weighted-routes* 2>/dev/null
```

### Deprecated content

AI Gateway for Envoy proxies was deprecated and removed from newer versions. The `ai/` directory only has content on older versions. Links to AI docs from newer versions should point to `https://agentgateway.dev/docs/kubernetes/latest/` instead. Check which versions still have `ai/` content:

```sh
find content/docs/envoy -path "*/ai/_index.md" -type f
```

---

## Link shortcodes

### `link-hextra`

Resolves version-aware links within docs. Extracts the version from the current page's URL path and prepends it:

```
{{</* link-hextra path="/quickstart/" */>}}
```

On a page at `/docs/envoy/latest/security/cors/`, this resolves to `/docs/envoy/latest/quickstart/`.

**Do NOT use `link-hextra` in blog posts.** Blog URLs don't contain a version segment, so `link-hextra` can't resolve the version. Use direct absolute links instead:

```markdown
[Get started](/docs/envoy/latest/quickstart/)
```

Or for external links:

```markdown
[Get started](https://kgateway.dev/docs/envoy/latest/quickstart/)
```

### `card` shortcode with `path=`

The custom `card.html` shortcode supports a `path=` parameter for version-aware card links (similar to `link-hextra` but for cards):

```
{{</* card path="/setup/listeners/https/" title="HTTPS listener" icon="bookmark" */>}}
```

Use `path=` for cross-section card links. Use `link=` (relative) for same-section card links.

---

## Scope — auto-generated content

### Reference docs

Any source path under `reference/` (API reference, Helm reference) is generated by the `update-api-docs.yml` workflow from the upstream `kgateway-dev/kgateway` repo. **Do not hand-edit the generated content.**

#### Generation pipeline

The `scripts/generate-ref-docs.py` script:
1. Runs `crd-ref-docs` to generate CRD API reference from Go types in `kgateway-dev/kgateway`
2. Runs `helm-docs` to generate Helm values reference from `values.yaml`
3. Runs `scripts/generate-shared-types.py` to append shared type definitions

Configuration: `scripts/crd-ref-docs-config.yaml`

#### Generated file locations

| Generated file | Upstream source | Generator |
|---|---|---|
| `content/docs/envoy/{version}/reference/api.md` (inline) | `kgateway-dev/kgateway` `api/v1alpha1/kgateway/` | `crd-ref-docs` + `generate-shared-types.py` |
| `assets/docs/pages/reference/helm/{version}/kgateway.md` | `kgateway-dev/kgateway` `install/helm/kgateway/values.yaml` | `helm-docs` |

#### How to fix broken links in reference content

1. **URLs in Go doc comments** (API reference): Fix in `kgateway-dev/kgateway` under `api/v1alpha1/kgateway/`. If the user has a local clone (e.g. at `kgateway-product/`), fix there.
2. **URLs in Helm chart values** (Helm reference): Fix in `kgateway-dev/kgateway` under `install/helm/kgateway/values.yaml`.
3. **Type links from `crd-ref-docs`**: Fix by adding `knownTypes` entries in `scripts/crd-ref-docs-config.yaml`.
4. **Broken anchors from `generate-shared-types.py`**: The script checks `documented_types` before creating anchor links. If types are still producing broken anchors, they may need to be added to the `crd-ref-docs-config.yaml` `knownTypes` list or the types need to be documented in the shared types section.

---

## Triage workflow

Work through the report top-down: Errors first, then Warnings, then Redirects.

### Common error patterns

Before diving into individual fixes, check for these patterns that explain many errors at once:

1. **Version-switcher false positives** (paths like `public/docs/{blog-slug}/{version}`): The Hextra navbar version dropdown on non-doc pages. The `navbar.html` guard (`if and $versions $version`) prevents this on blog/resource pages. The `navbar-version.html` `GetPage` check prevents it on doc pages where the target version doesn't have the page. If you see these, the guards may need updating.

2. **Shared asset cross-version breakage** (same path broken on one version but working on others): A shared asset uses a path that only exists on some versions. Fix with `version` shortcode conditionals (using TOML version values), NOT aliases.

3. **Blog post `link-hextra` failures** (paths like `public/blog/{slug}/{version}/...`): Blog posts using `link-hextra` which can't resolve versions from blog URLs. Replace with direct absolute links.

4. **Lychee remap gaps** (paths like `public/docs/{section}/` without `envoy/{version}/`): The lychee workflow remaps version-less doc paths to `envoy/latest/`. If a new top-level section is added, add a corresponding remap to `.github/workflows/links.yml`.

5. **Agentgateway section links**: The agentgateway section on kgateway.dev only hosts API reference pages, not full docs. Breadcrumb and navigation links to the agentgateway section root should point to `https://agentgateway.dev/docs/kubernetes/latest/` instead.

### For each entry

1. Skip if the source is under `reference/` (see auto-generated content above).
2. Identify the source file(s) to edit using the mapping rules.
3. Apply the rules for that category.
4. Record the finding in a summary.

**Do NOT open a PR or push commits.** Make local edits only. The user will review.

### Errors

1. **Check for false positives first.** Hugo processes images (PNG to WebP with hashes), so raw image paths in HTML may not match built files. The custom `card.html` shortcode processes images through `resources.Get` to handle this.
2. **Try to find the new location.** Check if the page exists at a different path on the target version.
3. **Apply the fix** in the shared file if the content wrapper is a reuse, otherwise in the content file.

### Warnings — broken anchors

1. Fetch the target page and check current anchor IDs.
2. Map old anchors to current ones.
3. For API reference anchors: these are generated by `crd-ref-docs` and `generate-shared-types.py`. Regenerating API docs should fix most anchor warnings.
4. For `#supported-versions`: This anchor is on the `versions` page via an empty heading `# {#supported-versions}`. If it's not resolving, check the heading exists in the content file.

### Redirects

1. Skip auth/login redirects.
2. Skip canonical short-form URLs (add to lychee excludes instead).
3. Otherwise update the source to the final URL.

---

## Making edits

- Edit **shared files** (`assets/docs/pages/` or `assets/docs/snippets/`) when the content wrapper is a reuse.
- Edit **content files** only when version-specific.
- Use `version` shortcode conditionals for cross-version path differences. Always use TOML version values from `versions.json`, never `linkVersion` values like `latest` or `main`.
- For blog posts, use direct absolute links (`/docs/envoy/latest/...`), never `link-hextra`.
- For cross-section card links, use the `path=` parameter.
- For agentgateway links that point to full docs (not just API reference), use `https://agentgateway.dev/docs/kubernetes/latest/` instead of local paths.

---

## Reporting back

After processing, give a structured summary grouped by outcome:

```
## Fixed
- <count> errors fixed across <count> files

## Generated reference content — upstream fixes needed
- <link> — fix in <upstream file:line>

## Needs human review
- <link> in <file> — <why>

## False positives
- <link> — <why> (suggest lychee exclude if systematic)
```

---

## Don't

- Don't open a PR or push. Local edits only.
- Don't edit files under `public/` — those are build output.
- Don't hand-edit generated reference content — fix upstream.
- Don't guess new URLs. If you can't verify, flag for review.
- Don't edit the thin content wrapper when the body is a reuse — edit the shared file.
- Don't use Hugo aliases to bridge cross-version path differences — use version conditionals.
- Don't use `linkVersion` values (`latest`, `main`) in `version` shortcode `include-if`/`exclude-if` — always read the TOML `version` values from `versions.json`.
- Don't use `link-hextra` in blog posts — use direct absolute links.
- Don't remove links to enterprise-only paths (like `transformations/simple/`) from shared assets — those paths work on the enterprise site via Hugo aliases on the OSS site.

# Scripts

This directory contains scripts and tools that help build the kgateway website and documentation.

## Link fix-ups

`generate-ref-docs.py` regenerates the API, Helm, and metrics reference docs from the kgateway repository. Some of those docs contain links that come straight from upstream source comments (Go doc comments and Helm `values.yaml`). When such a link breaks, the real fix belongs in the kgateway source, but the reference docs are also regenerated nightly from **released** kgateway tags, which are immutable. That means a broken URL keeps reappearing for already-released versions even after upstream source is corrected.

`scripts/link-fixups.json` is the safety net. Each entry maps a broken `old` URL to a working `new` URL, and the generator rewrites every occurrence in the generated content for all versions. To add a fix-up:

1. Append an entry to `scripts/link-fixups.json` with the broken URL (`old`), the working URL (`new`), and a short `reason`.
2. Also fix the link in the kgateway source so new releases ship the correct URL; this file only patches docs generated from older, frozen releases.

Matching is plain substring replacement, not regex. Two consequences to keep in mind:

- **Order matters.** Entries are applied top to bottom, so when one `old` URL is a prefix of another, list the longer, more specific URL first. Otherwise the shorter entry rewrites the prefix and the specific entry never matches. A unit test in `scripts/tests/test_link_fixups.py` enforces this ordering.
- **An empty `new` deletes the `old` string** instead of replacing it. Use that for text in a source comment that shouldn't be published at all, such as a developer-facing note that links to an upstream issue.

The fix-ups run twice over the API reference: once in `_post_process_api_docs`, and again over the finished file after `generate-shared-types.py` appends the shared type documentation. The second pass is needed because that appended section is read straight from Go doc comments and never goes through the first pass.

## Unit tests

Unit tests for scripts in this directory live in `scripts/tests/`.

Run them from the repository root:

```shell
python3 -m pytest scripts/tests -q
```

The tests cover two doc-generating scripts. These scripts build parts of the API reference documentation by reading source code and version information, then writing Markdown. If one of them has a small bug, it can quietly produce incorrect docs instead of failing loudly, so the tests focus on the helper logic that decides what content to generate.

### Test helper

`scripts/tests/conftest.py` is not a test file. It loads scripts such as `generate-ref-docs.py` and `generate-shared-types.py` as Python modules, because Python cannot import filenames with dashes through normal import syntax.

### `generate-ref-docs.py`

The tests for `generate-ref-docs.py` check that the script:

- Identifies which docs versions are `2.2.x` or newer, including `main`.
- Extracts only the requested API package section from a Markdown file that contains multiple packages.
- Returns no package content when the requested package is missing.
- Resolves the expected branch or release tag for a docs version.
- Skips prerelease tags such as release candidates and beta releases when choosing the latest stable tag.
- Calls `generate-shared-types.py` with the expected inputs when shared Go types are present.
- Rewrites every broken link in `scripts/link-fixups.json` to its working URL, leaves already-correct links untouched, and tolerates a missing fix-ups file.

These tests replace real `git` subprocess calls with test doubles so they run quickly and do not require network access.

### `generate-shared-types.py`

The tests for `generate-shared-types.py` check that the script:

- Reads human-written Go doc comments separately from `+kubebuilder` annotations.
- Collects validation annotations when they are needed.
- Parses Go structs, aliases, JSON field names, and required versus optional fields.
- Formats links for documented types while leaving unknown types as plain text.
- Labels enterprise duplicate type names so they do not collide with open-source types.
- Finds documented types and detects broken type links in generated Markdown.

These tests create small temporary input files and run the script logic against those fixtures.

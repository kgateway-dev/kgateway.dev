#!/usr/bin/env bash
# Write doc-test results into page front matter, for the "Verified" badge.
#
# Run it just before the production Hugo build:
#
#   bash scripts/doc-test-status.sh && <the usual build command>
#
# It downloads the latest `doc-test-results` artifact from this repo's Doc tests
# workflow (.github/workflows/doc-tests.yaml) on main, then sets
# `test_status: passed`, `failed`, or `partial` on each tested page. The theme
# shows the badge only for `passed`. Pages are changed in the build checkout
# only; never commit them.
#
# Needs GITHUB_TOKEN in the build environment: GitHub requires a token to
# download artifacts, even from a public repo. Read-only access to this repo's
# Actions is enough.
#
# The badge is decoration, so nothing here may fail the build. Without a token,
# results, or network, the site builds as before, with no badges.

set -u

DOCS_TESTS_DIR="${DOCS_TESTS_DIR:-out/docs-tests}"
DOCS_TESTS_URL="${DOCS_TESTS_URL:-https://github.com/solo-io/docs-tests.git}"

warn() { echo "Warning: $*; building without the Verified badge." >&2; exit 0; }

if [ -z "${GITHUB_TOKEN:-}" ]; then
  warn "GITHUB_TOKEN is not set"
fi

if [ ! -d "$DOCS_TESTS_DIR" ]; then
  git clone --quiet --depth 1 "$DOCS_TESTS_URL" "$DOCS_TESTS_DIR" || warn "could not clone docs-tests"
fi

python3 -c "import yaml" 2>/dev/null || pip install --quiet --user pyyaml || warn "could not install PyYAML"

DOC_TESTS_SITE_REPO=kgateway-dev/kgateway.dev \
  bash "$DOCS_TESTS_DIR/scripts/doc_test_fetch_artifacts.sh" || warn "could not fetch doc-test results"

if [ ! -f out/tests/generated/test-results.yaml ]; then
  warn "no doc-test results were found"
fi

python3 "$DOCS_TESTS_DIR/scripts/doc_test_inject_status.py" --repo-root . || warn "could not write test status"

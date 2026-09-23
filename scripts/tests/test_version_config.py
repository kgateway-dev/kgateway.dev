'''Guards `.docs-test.toml` against drifting away from `versions.json`.

`versions.json` is the single source of truth for which doc versions this repo
builds. `.docs-test.toml` repeats that list for the Playwright harness, and
nothing tied the two together, so the lists silently diverged: `2.3.x` shipped
without ever being added, and a long-dead `2.0.x` stayed behind. This test is
the tie.

Nothing in CI could have caught this, which is why the check belongs here. The
framework-tests workflow runs only the harness's `static` and `content`
projects. The spec that asserts every configured version appears in the version
dropdown lives in the `browser` project, which that workflow never invokes. The
`static` specs that do read this list — auto-cards, card-image, custom-alert —
either generate no tests at all or skip outright when pointed at a consumer's
own build rather than the harness fixture. The drift was invisible by
construction, not merely unreported.

One caveat before relying on this test: it only blocks a merge while
`scripts-tests` is a required check, and as of this commit the `main` ruleset
requires only `DCO`.
'''

import json
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_docs_test_toml_versions_match_active_versions():
    """Verify that .docs-test.toml [versioning].versions matches versions.json.

    The Playwright testing harness in solo-io/docs-theme-extras relies on
    .docs-test.toml to decide which version trees the per-version specs
    synthesize URLs for. A version missing from the list is never checked by
    those specs; a version present but not built makes them chase pages that
    do not exist.
    """
    versions_json_path = REPO_ROOT / "versions.json"
    assert versions_json_path.exists(), "versions.json does not exist"
    active_versions = json.loads(versions_json_path.read_text(encoding="utf-8"))
    expected_link_versions = [v["linkVersion"] for v in active_versions]

    docs_test_path = REPO_ROOT / ".docs-test.toml"
    assert docs_test_path.exists(), ".docs-test.toml does not exist"
    config = tomllib.loads(docs_test_path.read_text(encoding="utf-8"))

    versioning = config.get("versioning")
    assert versioning is not None, "[versioning] table is missing from .docs-test.toml"
    actual_versions = versioning.get("versions")
    assert actual_versions is not None, (
        "[versioning].versions is missing from .docs-test.toml"
    )

    # ORDER IS PART OF THE CONTRACT. Do not relax this to a set or a sorted
    # comparison because the "Missing"/"Obsolete" wording below reads like a set
    # difference. The harness treats `versions[0]` as the version its dropdown
    # navigation test clicks through to, so `versions.json` order (newest first,
    # `main` then `latest`) has to survive into `.docs-test.toml` verbatim.
    assert actual_versions == expected_link_versions, (
        f".docs-test.toml [versioning].versions does not match active versions in versions.json.\n"
        f"Configured: {actual_versions}\n"
        f"Expected:   {expected_link_versions}\n"
        f"Missing:    {[v for v in expected_link_versions if v not in actual_versions]}\n"
        f"Obsolete:   {[v for v in actual_versions if v not in expected_link_versions]}\n"
        f"Order:      {'differs' if sorted(actual_versions) == sorted(expected_link_versions) else 'n/a'}"
    )

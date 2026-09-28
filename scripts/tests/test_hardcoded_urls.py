import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = REPO_ROOT / "assets" / "kgw-docs"
CONTENT_DIR = REPO_ROOT / "content" / "docs"


def test_no_inverted_envoy_url_paths_in_shared_assets():
    """Verify assets/kgw-docs and content/docs have no inverted path orders like /docs/{version}/envoy/."""
    inverted_pattern = re.compile(
        r"https?://kgateway\.dev/docs/(?:main|latest|2\.\d+\.x)/envoy/"
    )
    violations = []
    for search_dir in [ASSETS_DIR, CONTENT_DIR]:
        for md_file in search_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            for line_num, line in enumerate(content.splitlines(), start=1):
                if inverted_pattern.search(line):
                    rel_path = md_file.relative_to(REPO_ROOT)
                    violations.append(f"{rel_path}:{line_num}: {line.strip()}")

    assert not violations, (
        f"Found inverted /docs/{{version}}/envoy/ URLs (should be /docs/envoy/{{version}}/):\n"
        + "\n".join(violations)
    )


if __name__ == "__main__":
    test_no_inverted_envoy_url_paths_in_shared_assets()
    print("All tests passed!")

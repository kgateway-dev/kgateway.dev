import re
import sys
from pathlib import Path, PurePosixPath

CARD_PATTERN = re.compile(r'{{<\s*card\s+(?:link|path)="([^"]+)"')
HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)


def has_markdown_content(path):
    """Return True when the directory contains markdown content."""
    return path.is_dir() and any(child.suffix == ".md" for child in path.iterdir())


def get_docs_root():
    return (Path(__file__).resolve().parent / "../content/docs").resolve()


def get_section_root(base_dir, docs_root):
    """Resolve the versioned docs root used by absolute `path=` cards."""
    try:
        relative_parts = base_dir.resolve().relative_to(docs_root).parts
    except ValueError:
        return docs_root

    if len(relative_parts) >= 2:
        return docs_root.joinpath(*relative_parts[:2])
    return docs_root


def normalize_doc_target(candidate):
    """Resolve a candidate path to either an existing markdown file or docs directory."""
    if candidate.is_file():
        return candidate
    if has_markdown_content(candidate):
        return candidate

    markdown_candidate = candidate.with_suffix(".md")
    if markdown_candidate.is_file():
        return markdown_candidate

    return None


def resolve_card_target(base_dir, docs_root, target):
    """Resolve link/path card values to a docs file or directory when possible."""
    if target.startswith(("http://", "https://")):
        return None

    posix_target = PurePosixPath(target)
    if target.startswith("/docs/"):
        candidate = docs_root.joinpath(*posix_target.parts[2:])
    elif target.startswith("/"):
        candidate = get_section_root(base_dir, docs_root).joinpath(*posix_target.parts[1:])
    else:
        candidate = base_dir.joinpath(*posix_target.parts)

    return normalize_doc_target(candidate.resolve())


def extract_card_targets(index_file):
    """Extract link/path values from card shortcodes and ignore HTML comments."""
    content = index_file.read_text(encoding="utf-8")
    uncommented = HTML_COMMENT_PATTERN.sub("", content)
    return set(CARD_PATTERN.findall(uncommented))


def find_valid_links(directory):
    """Find the direct child links that should appear in local cards."""
    valid_links = set()

    for item in directory.iterdir():
        if item.is_file() and item.suffix == ".md" and item.name != "_index.md":
            valid_links.add(item.stem)
        elif has_markdown_content(item):
            valid_links.add(item.name)

    return valid_links


def map_to_local_link(base_dir, resolved_target, valid_links):
    """Map a resolved target back to a local child card when it points into this subtree."""
    try:
        relative_path = resolved_target.relative_to(base_dir)
    except ValueError:
        return None

    if len(relative_path.parts) == 1 and resolved_target.is_file():
        candidate = resolved_target.stem
        return candidate if candidate in valid_links else None

    candidate = relative_path.parts[0]
    return candidate if candidate in valid_links else None


def check_directory(directory, docs_root):
    """Check for missing or extra cards in _index.md."""
    index_file = directory / "_index.md"

    if not index_file.exists():
        print(f"Skipping {directory}: No _index.md file.")
        return

    card_targets = extract_card_targets(index_file)
    valid_links = find_valid_links(directory)
    matched_local_links = set()
    extra_cards = set()

    for target in card_targets:
        if target.startswith(("http://", "https://")):
            continue

        if target in valid_links:
            matched_local_links.add(target)
            continue

        resolved_target = resolve_card_target(directory, docs_root, target)
        if not resolved_target:
            extra_cards.add(target)
            continue

        local_match = map_to_local_link(directory, resolved_target, valid_links)
        if local_match:
            matched_local_links.add(local_match)

    missing_cards = valid_links - matched_local_links

    if missing_cards:
        print(f"[WARN] Missing cards in {index_file}: {missing_cards}")

    if extra_cards:
        print(
            "[ERROR] Extra cards in "
            f"{index_file} that don't match any local .md file, valid subdirectory, or valid relative path: {extra_cards}"
        )


def main():
    """Run checks for a specific directory or default to 'content/docs'."""
    if len(sys.argv) > 1:
        content_root = Path(sys.argv[1]).resolve()
    else:
        content_root = get_docs_root()

    print(f"Checking directories under: {content_root}")

    for root, _, files in content_root.walk():
        if "_index.md" in files:
            check_directory(root, content_root)


if __name__ == "__main__":
    main()

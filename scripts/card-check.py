import os
import re
import sys

def resolve_relative_path(base_dir, relative_path):
    """Convert a relative Hugo link (e.g., ../../traffic-management/direct-response) to an absolute path."""
    abs_path = os.path.normpath(os.path.join(base_dir, relative_path))
    if os.path.isdir(abs_path) and any(f.endswith(".md") for f in os.listdir(abs_path)):
        return os.path.basename(abs_path)  # Valid directory with .md files
    elif os.path.isfile(abs_path + ".md"):
        return os.path.basename(abs_path)  # Valid .md file
    return None  # Invalid link

def find_cards_in_index(index_file, base_dir):
    """Extract card links from _index.md file and resolve relative paths."""
    with open(index_file, "r", encoding="utf-8") as file:
        content = file.read()

    raw_card_links = re.findall(r'{{<\s*card\s+link="([^"]+)"', content)
    resolved_links = set()

    for link in raw_card_links:
        if link.startswith(("http", "https")):
            resolved_links.add(link)  # Allow external links
        elif link.startswith("../") or link.startswith("./") or link.startswith("/"):
            resolved = resolve_relative_path(base_dir, link)
            if resolved:
                resolved_links.add(resolved)  # Add valid resolved relative paths
        else:
            resolved_links.add(link)  # Add normal local links

    return resolved_links

def find_valid_links(directory):
    """Find all valid links (either .md files or subdirectories that contain at least one .md file)."""
    valid_links = set()

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        # If it's a markdown file (excluding _index.md), add it as a valid link
        if item.endswith(".md") and item != "_index.md":
            valid_links.add(os.path.splitext(item)[0])

        # If it's a directory, check if it contains at least one .md file
        elif os.path.isdir(item_path):
            md_files = [f for f in os.listdir(item_path) if f.endswith(".md")]
            if md_files:  # Only include subdirectories with .md files
                valid_links.add(item)

    return valid_links

def check_directory(directory):
    """Check for missing or extra cards in _index.md."""
    index_file = os.path.join(directory, "_index.md")

    if not os.path.exists(index_file):
        print(f"Skipping {directory}: No _index.md file.")
        return

    card_links = find_cards_in_index(index_file, directory)
    valid_links = find_valid_links(directory)

    # Allow external links (http, https)
    extra_cards = {card for card in card_links if card not in valid_links and not card.startswith(("http", "https"))}
    missing_cards = valid_links - card_links

    if missing_cards:
        print(f"⚠️ Missing cards in {index_file}: {missing_cards}")

    if extra_cards:
        print(f"❌ Extra cards in {index_file} that don’t match any local .md file, valid subdirectory, or valid relative path: {extra_cards}")

def main():
    """Run checks for a specific directory or default to 'content/docs'."""
    if len(sys.argv) > 1:
        content_root = os.path.abspath(sys.argv[1])
    else:
        content_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../content/docs"))

    print(f"Checking directories under: {content_root}")  # Debugging

    for root, dirs, files in os.walk(content_root):
        if "_index.md" in files:
            check_directory(root)

if __name__ == "__main__":
    main()
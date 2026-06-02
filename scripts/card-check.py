#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

def parse_cards_from_file(filepath):
    """
    Parses a markdown file and extracts link or path attributes from card shortcodes.
    Matches formats like:
      {{< card link="http" title="HTTP listener" >}}
      {{< card path="/integrations" title="Integrations" >}}
    """
    card_links = set()
    if not os.path.exists(filepath):
        return card_links

    # Regex to find card shortcodes (not inside HTML comments)
    card_re = re.compile(r'{{\s*<\s*card\s+([^>]+)>\s*}}')
    # Regex to find link or path attributes within a card shortcode
    attr_re = re.compile(r'(?:link|path)\s*=\s*"([^"]+)"')
    # Regex to detect HTML comments
    comment_re = re.compile(r'<!--.*?-->', re.DOTALL)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Strip HTML comments to avoid matching commented-out card shortcodes
    content_no_comments = comment_re.sub('', content)

    for match in card_re.finditer(content_no_comments):
        attrs_str = match.group(1)
        attr_match = attr_re.search(attrs_str)
        if attr_match:
            card_links.add(attr_match.group(1))

    return card_links

def is_external_link(link):
    return link.startswith(('http://', 'https://', 'mailto:', '//'))

def clean_link(link):
    # Strip query parameters and anchors
    link = link.split('#')[0].split('?')[0]
    # Strip leading/trailing slashes for easier path matching
    return link.strip('/')

def check_cards(docs_root):
    """
    Checks all directories under docs_root.
    """
    has_errors = False

    print(f"Checking directories under: {docs_root}")

    for root, dirs, files in os.walk(docs_root):
        index_path = os.path.join(root, '_index.md')
        if not os.path.exists(index_path):
            continue

        # Get all local files (except _index.md) and subdirectories
        local_items = set()
        for f in files:
            if f.endswith('.md') and f != '_index.md':
                # Remove extension to match hugo links
                local_items.add(f[:-3])

        for d in dirs:
            # Check if directory contains a markdown file or _index.md
            dir_path = os.path.join(root, d)
            has_markdown = False
            for _, _, subfiles in os.walk(dir_path):
                if any(sf.endswith('.md') for sf in subfiles):
                    has_markdown = True
                    break
            if has_markdown:
                local_items.add(d)

        # Parse card links from the _index.md
        card_links = parse_cards_from_file(index_path)

        # Validate each card link
        extra_cards = set()
        referenced_local_items = set()

        for original_link in card_links:
            if is_external_link(original_link):
                continue

            cleaned = clean_link(original_link)

            # Check if this resolves relative to the current directory
            # e.g., if link is "basic", we check basic.md or basic/_index.md in the current directory
            # normpath resolves ".." components so that ../failover works correctly
            target_path_relative = os.path.normpath(os.path.join(root, cleaned))
            target_file_md = target_path_relative + '.md'
            target_index_md = os.path.join(target_path_relative, '_index.md')

            if os.path.exists(target_file_md) or os.path.exists(target_index_md):
                # Valid relative path or local item
                # Check if it matches a direct child local item (e.g. 'basic' or 'subfolder')
                # If the link starts with "../", it's referencing a parent directory, so it won't match a direct local item
                if cleaned in local_items:
                    referenced_local_items.add(cleaned)
                continue

            # Check if this is a root-relative path
            # If the original link starts with /docs/, it resolves relative to content/
            if original_link.startswith('/docs/'):
                content_root = os.path.abspath(os.path.join(docs_root, '..'))
                target_path_docs_root = os.path.join(content_root, cleaned)
                if os.path.exists(target_path_docs_root + '.md') or os.path.exists(os.path.join(target_path_docs_root, '_index.md')):
                    continue

            # Otherwise check if it is relative to the version directory
            version_dir = None
            parts = Path(os.path.abspath(root)).parts
            for idx in range(len(parts) - 2):
                if parts[idx] == 'docs' and parts[idx+1] in ('envoy', 'agentgateway'):
                    version_dir = os.path.sep.join(parts[:idx+3])
                    break

            if version_dir:
                target_path_root_rel = os.path.join(version_dir, cleaned)
                if os.path.exists(target_path_root_rel + '.md') or os.path.exists(os.path.join(target_path_root_rel, '_index.md')):
                    continue

            # Check if it resolves relative to content/docs/
            target_path_docs_rel = os.path.join(docs_root, cleaned)
            if os.path.exists(target_path_docs_rel + '.md') or os.path.exists(os.path.join(target_path_docs_rel, '_index.md')):
                continue

            # If not resolved, it is an invalid link
            extra_cards.add(original_link)

        # Missing cards: local files/directories not referenced in any card link
        missing_cards = local_items - referenced_local_items

        if missing_cards or extra_cards:
            print(f"\nScanning: {root}")
            if missing_cards:
                print(f"  [WARNING] Missing cards in {os.path.relpath(index_path)}: {missing_cards}")
            if extra_cards:
                print(f"  [ERROR] Extra cards in {os.path.relpath(index_path)} that don’t match any local .md file, valid subdirectory, or valid relative path: {extra_cards}")
                has_errors = True

    return not has_errors

if __name__ == '__main__':
    # Root content/docs directory relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.abspath(os.path.join(script_dir, '..', 'content', 'docs'))
    
    success = check_cards(docs_dir)
    if not success:
        sys.exit(1)
    else:
        print("\nAll cards are valid! No broken references found.")
        sys.exit(0)

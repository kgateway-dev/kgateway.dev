import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

def resolve_relative_path(base_dir, link):
    if link.startswith("/"):
        abs_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "content", link.lstrip("/"))
        )
    else:
        abs_path = os.path.normpath(os.path.join(base_dir, link))
    
    return os.path.exists(abs_path) or os.path.exists(abs_path + ".md")

def find_cards_in_index(index_file, base_dir):
    with open(index_file, "r", encoding="utf-8") as file:
        content = file.read()

    raw_card_links = re.findall(r'{{<\s*card\s+(?:link|path)="([^"]+)"', content)
    
    resolved_links = set()
    
    for link in raw_card_links:
        if link.startswith(("http://", "https://")):
            continue
        elif link.startswith(("../", "./", "/")):
            if not resolve_relative_path(base_dir, link):
                resolved_links.add(link)
        elif "/" in link:
            abs_path = os.path.normpath(os.path.join(base_dir, link))
            if not (os.path.exists(abs_path) or os.path.exists(abs_path + ".md")):
                resolved_links.add(link)
        else:
            resolved_links.add(link)
    return resolved_links

def find_valid_links(directory):
    valid_links = set()
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if item.endswith(".md") and item != "_index.md":
            valid_links.add(os.path.splitext(item)[0])
        elif os.path.isdir(item_path):
            md_files = [f for f in os.listdir(item_path) if f.endswith(".md")]
            if md_files:
                valid_links.add(item)
    return valid_links

def check_directory(directory):
    index_file = os.path.join(directory, "_index.md")
    if not os.path.exists(index_file):
        return

    card_links = find_cards_in_index(index_file, directory)
    valid_links = find_valid_links(directory)

    extra_cards = card_links - valid_links
    missing_cards = valid_links - card_links

    if missing_cards:
        print(f"⚠️ Missing cards in {index_file}: {missing_cards}")
    if extra_cards:
        print(f"❌ Extra cards in {index_file}: {extra_cards}")

def main():
    content_dir = os.path.join(os.path.dirname(__file__), "..", "content")
    for root, dirs, files in os.walk(content_dir):
        if "_index.md" in files:
            check_directory(root)

if __name__ == "__main__":
    main()
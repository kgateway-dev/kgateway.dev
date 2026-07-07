import json


def test_shipped_fixups_rewrite_known_broken_links(gen_ref_docs):
    '''Every entry in scripts/link-fixups.json should rewrite its broken URL.'''
    with open("scripts/link-fixups.json") as f:
        replacements = json.load(f)["replacements"]

    assert replacements, "expected at least one shipped fix-up"

    for entry in replacements:
        old, new = entry["old"], entry["new"]
        content = f"prefix {old} suffix"
        result = gen_ref_docs._apply_link_fixups(content)
        assert old not in result, f"broken link not rewritten: {old}"
        assert new in result, f"replacement URL missing: {new}"


def test_apply_link_fixups_is_substring_replacement(gen_ref_docs, monkeypatch):
    monkeypatch.setattr(
        gen_ref_docs,
        "_LINK_FIXUPS_CACHE",
        [{"old": "http://old.example/x", "new": "http://new.example/y"}],
    )
    content = "see http://old.example/x and http://old.example/x again"
    result = gen_ref_docs._apply_link_fixups(content)
    assert result == "see http://new.example/y and http://new.example/y again"


def test_apply_link_fixups_leaves_correct_links_untouched(gen_ref_docs, monkeypatch):
    monkeypatch.setattr(
        gen_ref_docs,
        "_LINK_FIXUPS_CACHE",
        [{"old": "http://old.example/x", "new": "http://new.example/y"}],
    )
    content = "http://new.example/y stays as is"
    assert gen_ref_docs._apply_link_fixups(content) == content


def test_apply_link_fixups_skips_incomplete_entries(gen_ref_docs, monkeypatch):
    monkeypatch.setattr(
        gen_ref_docs,
        "_LINK_FIXUPS_CACHE",
        [{"old": "", "new": "http://x"}, {"old": "http://y"}],
    )
    content = "untouched http://y here"
    assert gen_ref_docs._apply_link_fixups(content) == content


def test_load_link_fixups_missing_file_returns_empty(gen_ref_docs, monkeypatch):
    monkeypatch.setattr(gen_ref_docs, "_LINK_FIXUPS_CACHE", None)
    assert gen_ref_docs._load_link_fixups("scripts/does-not-exist.json") == []

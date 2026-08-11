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


def test_shipped_fixups_are_ordered_specific_before_general(gen_ref_docs):
    '''A shorter 'old' URL must not be listed ahead of a longer one it prefixes.

    Fix-ups are plain substring replacements applied top to bottom, so a general
    entry listed first would rewrite the prefix and leave the specific entry dead.
    '''
    with open("scripts/link-fixups.json") as f:
        olds = [entry["old"] for entry in json.load(f)["replacements"]]

    for i, general in enumerate(olds):
        for specific in olds[i + 1:]:
            assert not specific.startswith(general), (
                f"'{specific}' is prefixed by the earlier entry '{general}'; "
                "list the more specific URL first"
            )


def test_apply_link_fixups_deletes_when_new_is_empty(gen_ref_docs, monkeypatch):
    monkeypatch.setattr(
        gen_ref_docs,
        "_LINK_FIXUPS_CACHE",
        [{"old": "internal note: http://old.example/x<br />", "new": ""}],
    )
    content = "| field | internal note: http://old.example/x<br />Real description |"
    result = gen_ref_docs._apply_link_fixups(content)
    assert result == "| field | Real description |"


def test_apply_link_fixups_to_file_rewrites_appended_content(
    gen_ref_docs, monkeypatch, tmp_path
):
    '''generate-shared-types.py appends raw Go doc comments after the first
    fix-up pass, so the file-level pass has to catch them.'''
    monkeypatch.setattr(
        gen_ref_docs,
        "_LINK_FIXUPS_CACHE",
        [{"old": "http://old.example/x", "new": "http://new.example/y"}],
    )
    api_file = tmp_path / "api.md"
    api_file.write_text("appended type doc: http://old.example/x\n", encoding="utf-8")

    gen_ref_docs._apply_link_fixups_to_file(str(api_file))

    assert api_file.read_text(encoding="utf-8") == "appended type doc: http://new.example/y\n"


def test_apply_link_fixups_to_file_tolerates_missing_file(gen_ref_docs, tmp_path):
    gen_ref_docs._apply_link_fixups_to_file(str(tmp_path / "does-not-exist.md"))


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

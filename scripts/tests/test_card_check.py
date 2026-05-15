def test_resolve_relative_path_file_and_directory(card_check, tmp_path):
    base_dir = tmp_path / "content" / "docs" / "listeners"
    base_dir.mkdir(parents=True)

    relative_file_dir = tmp_path / "content" / "docs" / "security"
    relative_file_dir.mkdir(parents=True)
    (relative_file_dir / "jwt.md").write_text("jwt", encoding="utf-8")

    relative_subdir = tmp_path / "content" / "docs" / "traffic"
    relative_subdir.mkdir(parents=True)
    (relative_subdir / "timeout.md").write_text("timeout", encoding="utf-8")

    assert card_check.resolve_relative_path(str(base_dir), "../security/jwt") == "jwt"
    assert card_check.resolve_relative_path(str(base_dir), "../traffic") == "traffic"
    assert card_check.resolve_relative_path(str(base_dir), "../missing/path") is None


def test_find_cards_in_index_resolves_relative_and_external(card_check, tmp_path):
    base_dir = tmp_path / "content" / "docs" / "listeners"
    base_dir.mkdir(parents=True)

    relative_file_dir = tmp_path / "content" / "docs" / "security"
    relative_file_dir.mkdir(parents=True)
    (relative_file_dir / "jwt.md").write_text("jwt", encoding="utf-8")

    index_file = base_dir / "_index.md"
    index_file.write_text(
        '\n'.join(
            [
                "{{< cards >}}",
                '  {{< card link="http" title="HTTP listener" >}}',
                '  {{< card link="../security/jwt" title="JWT" >}}',
                '  {{< card link="https://example.com" title="External" >}}',
                "{{< /cards >}}",
            ]
        ),
        encoding="utf-8",
    )

    links = card_check.find_cards_in_index(str(index_file), str(base_dir))
    assert links == {"http", "jwt", "https://example.com"}


def test_find_valid_links_ignores_index_and_empty_dirs(card_check, tmp_path):
    (tmp_path / "_index.md").write_text("index", encoding="utf-8")
    (tmp_path / "http.md").write_text("http", encoding="utf-8")
    (tmp_path / "https.md").write_text("https", encoding="utf-8")
    (tmp_path / "empty-dir").mkdir()
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    (nested_dir / "readme.md").write_text("nested", encoding="utf-8")

    valid_links = card_check.find_valid_links(str(tmp_path))
    assert valid_links == {"http", "https", "nested"}


def test_check_directory_reports_missing_and_extra_cards(card_check, tmp_path, capsys):
    (tmp_path / "good.md").write_text("good", encoding="utf-8")
    (tmp_path / "missing.md").write_text("missing", encoding="utf-8")
    (tmp_path / "_index.md").write_text(
        '\n'.join(
            [
                "{{< cards >}}",
                '  {{< card link="good" title="Good" >}}',
                '  {{< card link="extra" title="Extra" >}}',
                "{{< /cards >}}",
            ]
        ),
        encoding="utf-8",
    )

    card_check.check_directory(str(tmp_path))

    output = capsys.readouterr().out
    assert "Missing cards" in output
    assert "missing" in output
    assert "Extra cards" in output
    assert "extra" in output

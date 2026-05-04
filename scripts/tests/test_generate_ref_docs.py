from types import SimpleNamespace


def test_is_version_2_2_or_later(gen_ref_docs):
    assert gen_ref_docs.is_version_2_2_or_later("main") is True
    assert gen_ref_docs.is_version_2_2_or_later("2.2.x") is True
    assert gen_ref_docs.is_version_2_2_or_later("2.3.x") is True
    assert gen_ref_docs.is_version_2_2_or_later("2.1.x") is False
    assert gen_ref_docs.is_version_2_2_or_later("invalid") is False


def test_extract_package_section(gen_ref_docs):
    content = "\n".join(
        [
            "# API Reference",
            "## Packages",
            "- [gateway.kgateway.dev/v1alpha1](#gatewaykgatewaydevv1alpha1)",
            "- [other.package/v1alpha1](#otherpackagev1alpha1)",
            "",
            "## gateway.kgateway.dev/v1alpha1",
            "Gateway package docs",
            "",
            "## other.package/v1alpha1",
            "Other package docs",
        ]
    )
    extracted = gen_ref_docs.extract_package_section(content, "gateway.kgateway.dev/v1alpha1")
    assert extracted is not None
    assert "## Packages" in extracted
    assert "gateway.kgateway.dev/v1alpha1" in extracted
    assert "Gateway package docs" in extracted
    assert "other.package/v1alpha1" not in extracted.split("## gateway.kgateway.dev/v1alpha1", 1)[1]


def test_extract_package_section_returns_none_when_missing(gen_ref_docs):
    content = "## Packages\n- [a](#a)\n"
    assert gen_ref_docs.extract_package_section(content, "missing.package/v1alpha1") is None


def test_resolve_branch_for_version(gen_ref_docs, monkeypatch):
    calls = []

    def fake_run(cmd, capture_output, text, check):
        calls.append(cmd)
        return SimpleNamespace(stdout="abc refs/heads/v2.2.x")

    monkeypatch.setattr(gen_ref_docs.subprocess, "run", fake_run)

    assert gen_ref_docs.resolve_branch_for_version("2.2.x", "latest") == "v2.2.x"
    assert calls, "expected ls-remote check to run for non-main versions"
    assert gen_ref_docs.resolve_branch_for_version("2.2.x", "main") == "main"


def test_resolve_tag_for_version_filters_rc_beta_and_returns_latest(gen_ref_docs, monkeypatch):
    output = "\n".join(
        [
            "sha1 refs/tags/v2.2.1",
            "sha2 refs/tags/v2.2.3-rc1",
            "sha3 refs/tags/v2.2.4-beta1",
            "sha4 refs/tags/v2.2.5",
        ]
    )

    def fake_run(cmd, capture_output, text, check):
        return SimpleNamespace(stdout=output)

    monkeypatch.setattr(gen_ref_docs.subprocess, "run", fake_run)

    resolved = gen_ref_docs.resolve_tag_for_version("2.2.x", "latest")
    assert resolved == "v2.2.5"


def test_generate_shared_types_invokes_script_when_shared_exists(gen_ref_docs, monkeypatch, tmp_path):
    api_file = tmp_path / "api.md"
    api_file.write_text("api", encoding="utf-8")

    kgateway_dir = tmp_path / "kgateway"
    shared_dir = kgateway_dir / "api" / "v1alpha1" / "shared"
    source_dir = kgateway_dir / "api" / "v1alpha1" / "kgateway"
    shared_dir.mkdir(parents=True)
    source_dir.mkdir(parents=True)

    calls = []

    def fake_run(cmd, check):
        calls.append(cmd)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(gen_ref_docs.subprocess, "run", fake_run)

    gen_ref_docs._generate_shared_types(str(api_file), kgateway_dir=str(kgateway_dir))

    assert len(calls) == 1
    assert calls[0][0:2] == ["python3", "scripts/generate-shared-types.py"]
    assert calls[0][2] == str(shared_dir)
    assert calls[0][3] == str(api_file)
    assert calls[0][4] == str(source_dir)

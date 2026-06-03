from pathlib import Path


def test_extract_doc_comment_skips_kubebuilder_annotations(gen_shared_types):
    lines = [
        "// +kubebuilder:validation:Enum=HTTP1;HTTP2",
        "// HTTP version to use.",
        "type HTTPVersion string",
    ]
    assert gen_shared_types.extract_doc_comment(lines, 2) == "HTTP version to use."


def test_extract_validation_annotations(gen_shared_types):
    lines = [
        "// +kubebuilder:validation:Enum=HTTP1;HTTP2",
        "// +kubebuilder:validation:MinLength=1",
        "type HTTPVersion string",
    ]
    assert gen_shared_types.extract_validation_annotations(lines, 2) == [
        "Enum=HTTP1;HTTP2",
        "MinLength=1",
    ]


def test_parse_go_file_extracts_struct_and_alias(gen_shared_types, tmp_path):
    go_file = tmp_path / "types.go"
    go_file.write_text(
        "\n".join(
            [
                "package shared",
                "",
                "// AuthConfig contains auth settings.",
                "type AuthConfig struct {",
                '    // Issuer is the token issuer.',
                '    Issuer string `json:"issuer"`',
                '    // Audiences are accepted audiences.',
                '    Audiences []string `json:"audiences,omitempty"`',
                "}",
                "",
                "// ProtocolName is the protocol enum.",
                "type ProtocolName = string",
            ]
        ),
        encoding="utf-8",
    )

    parsed = gen_shared_types.parse_go_file(go_file, source="shared", is_enterprise=False)
    by_name = {type_info.name: type_info for type_info in parsed}

    struct_type = by_name["AuthConfig"]
    assert struct_type.kind == "struct"
    assert struct_type.description == "AuthConfig contains auth settings."
    assert len(struct_type.fields) == 2
    assert struct_type.fields[0].json_name == "issuer"
    assert struct_type.fields[0].required is True
    assert struct_type.fields[1].json_name == "audiences"
    assert struct_type.fields[1].required is False

    alias_type = by_name["ProtocolName"]
    assert alias_type.kind == "alias"
    assert alias_type.underlying_type == "string"


def test_format_go_type_as_link_respects_documented_types(gen_shared_types):
    assert (
        gen_shared_types.format_go_type_as_link("AuthConfig", {"AuthConfig"})
        == "[AuthConfig](#authconfig)"
    )
    assert gen_shared_types.format_go_type_as_link("UnknownType", {"AuthConfig"}) == "_UnknownType_"
    assert (
        gen_shared_types.format_go_type_as_link("[]*AuthConfig", {"AuthConfig"})
        == "[]*[AuthConfig](#authconfig)"
    )


def test_generate_markdown_adds_enterprise_suffix_for_duplicates(gen_shared_types):
    oss = gen_shared_types.TypeInfo(
        name="AuthConfig",
        kind="struct",
        source="shared",
        is_enterprise=False,
        fields=[
            gen_shared_types.FieldInfo(
                name="Issuer",
                go_type="string",
                json_name="issuer",
                description="Issuer field.",
                required=True,
            )
        ],
    )
    enterprise = gen_shared_types.TypeInfo(
        name="AuthConfig",
        kind="struct",
        source="shared",
        is_enterprise=True,
        fields=[
            gen_shared_types.FieldInfo(
                name="Issuer",
                go_type="string",
                json_name="issuer",
                description="Enterprise issuer field.",
                required=True,
            )
        ],
    )

    markdown = gen_shared_types.generate_markdown(
        [oss, enterprise],
        referenced_types={"AuthConfig"},
        existing_doc_types=set(),
    )

    assert "#### AuthConfig" in markdown
    assert "#### AuthConfig (Enterprise)" in markdown


def test_find_documented_types_and_broken_links(gen_shared_types, tmp_path):
    doc_file = Path(tmp_path / "api.md")
    doc_file.write_text(
        "\n".join(
            [
                "#### KnownType",
                "",
                "Works with [KnownType](#knowntype).",
                "Broken link to [MissingType](#missingtype).",
            ]
        ),
        encoding="utf-8",
    )

    documented = gen_shared_types.find_documented_types(doc_file)
    broken = gen_shared_types.find_all_broken_links(doc_file)

    assert documented == {"KnownType"}
    assert broken == {"MissingType"}

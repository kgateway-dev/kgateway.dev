from pathlib import Path


REDIRECTS = Path(__file__).resolve().parents[2] / "static" / "_redirects"


def _rules():
    rules = []
    for line_number, line in enumerate(
        REDIRECTS.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        fields = line.split()
        assert len(fields) == 3, f"malformed redirect on line {line_number}: {line}"
        source, destination, status = fields
        assert status in {"301", "302", "303", "307", "308"}
        rules.append((source, destination, status, line_number))
    return rules


def _resolve(path, rules):
    for source, destination, status, line_number in rules:
        if "*" in source:
            prefix, suffix = source.split("*", 1)
            if path.startswith(prefix) and path.endswith(suffix):
                splat = path[len(prefix) : len(path) - len(suffix) if suffix else None]
                return destination.replace(":splat", splat), status, line_number
        elif path == source:
            return destination, status, line_number
    return None


def test_redirect_file_stays_below_observed_cloudflare_cutoff():
    rules = _rules()
    assert len(rules) < 100
    assert sum("*" in source for source, *_ in rules) <= 100


def test_static_redirects_precede_wildcards():
    rules = _rules()
    wildcard_seen = False
    for source, _, _, line_number in rules:
        if "*" in source:
            wildcard_seen = True
        elif wildcard_seen:
            raise AssertionError(
                f"static redirect after wildcard on line {line_number}: {source}"
            )


def test_maintainer_requested_redirects():
    rules = _rules()
    expected = {
        "/docs/2.0.x/integrations/inference-extension": "/docs/envoy/latest/integrations",
        "/docs/2.0.x/integrations/istio/ambient/waypoint": "/docs/envoy/latest/integrations/istio/ambient",
        "/docs/2.0.x/setup/customize/general-steps": "/docs/envoy/latest/setup/customize",
        "/docs/latest": "/docs/envoy/latest/",
        "/docs/main": "/docs/envoy/main/",
        "/docs/2.0.x": "/docs/envoy/latest/",
        "/docs/latest/ai/about": "https://agentgateway.dev/docs/kubernetes/latest/documentation/about/",
        "/docs/main/ai/about": "https://agentgateway.dev/docs/kubernetes/main/documentation/about/",
        "/docs/latest/ai/prompt-guards": "https://agentgateway.dev/docs/kubernetes/latest/documentation/llm/guardrails/",
        "/docs/main/ai/prompt-guards": "https://agentgateway.dev/docs/kubernetes/main/documentation/llm/guardrails/",
        "/docs/latest/ai/tracing/": "https://agentgateway.dev/docs/kubernetes/latest/documentation/",
        "/docs/main/ai/tracing/": "https://agentgateway.dev/docs/kubernetes/main/documentation/",
        "/docs/agentgateway/2.0.x/reference/api/": "https://agentgateway.dev/docs/kubernetes/latest/reference/api/",
        "/docs/agentgateway/latest/about/": "https://agentgateway.dev/docs/kubernetes/latest/about/",
    }

    for source, destination in expected.items():
        resolved = _resolve(source, rules)
        assert resolved is not None, f"no redirect for {source}"
        assert resolved[:2] == (destination, "301"), (
            f"unexpected redirect for {source}: {resolved}"
        )


def test_page_moves_resolve_with_and_without_trailing_slash():
    rules = _rules()
    expected = {
        "/docs/latest/glossary": "/docs/envoy/latest/reference/glossary/",
        "/docs/latest/resiliency/tcp-keepalive": "/docs/envoy/latest/resiliency/keepalive/tcp/",
        "/docs/latest/setup/hpa": "/docs/envoy/latest/setup/customize/configs/",
        "/docs/latest/setup/selfmanaged": "/docs/envoy/latest/setup/customize/envoy/selfmanaged/",
        "/docs/main/resiliency/tcp-keepalive": "/docs/envoy/main/resiliency/keepalive/tcp/",
        "/docs/main/setup/hpa": "/docs/envoy/main/setup/customize/configs/",
        "/docs/main/setup/selfmanaged": "/docs/envoy/main/setup/customize/envoy/selfmanaged/",
    }
    for version in ("2.1.x", "2.2.x", "2.3.x", "latest", "main"):
        expected[f"/docs/envoy/{version}/security/jwt/basic"] = (
            f"/docs/envoy/{version}/security/jwt/simple/basic/"
        )

    for source, destination in expected.items():
        for path in (source, source + "/"):
            resolved = _resolve(path, rules)
            assert resolved is not None, f"no redirect for {path}"
            assert resolved[:2] == (destination, "301"), (
                f"unexpected redirect for {path}: {resolved}"
            )

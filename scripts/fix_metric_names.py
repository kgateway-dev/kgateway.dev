#!/usr/bin/env python3
"""Correct the findmetrics markdown table for constants declared in another file.

findmetrics resolves a `Namespace:`, `Subsystem:`, or label identifier only against
constants declared in the SAME FILE as the metric. A constant declared elsewhere in the
package is dropped from the name, or a label is listed by its Go identifier
(`gatewayLabel` instead of `gateway`). This re-resolves those identifiers across the
package and rewrites the rows. Ported from agentgateway/website#1407.

Usage: fix_metric_names.py SOURCE_DIR [--default-namespace NS] < table.md > fixed.md
"""

import argparse
import os
import re
import sys

_METRIC_CALL_RE = re.compile(r"\bmetrics\.New(?:Counter|Gauge|Histogram)\(\s*metrics\.\w+Opts\{")
_OPT_RE = re.compile(r'\b(Namespace|Subsystem|Name|Help)\s*:\s*("(?:[^"\\]|\\.)*"|\w+(?:\.\w+)?)')
_LABELS_RE = re.compile(r"\s*,\s*\[\]string\{([^}]*)\}")
_DECL_BLOCK_RE = re.compile(r"^(?:const|var) \((.*?)^\)", re.MULTILINE | re.DOTALL)
_DECL_LINE_RE = re.compile(r'^(?:const|var) (\w+)(?: string)? = "((?:[^"\\]|\\.)*)"', re.MULTILINE)
_BLOCK_ENTRY_RE = re.compile(r'^\s+(\w+)(?: string)? *= *"((?:[^"\\]|\\.)*)"', re.MULTILINE)
DEFAULT_NAMESPACE = "kgateway"


def _warn(message: str) -> None:
    print(f"    Warning: {message}", file=sys.stderr)


def _metric_full_name(namespace: str, subsystem: str, name: str) -> str:
    return "_".join(p for p in (namespace, subsystem, name) if p)


def _string_consts(src: str) -> dict[str, str]:
    consts = dict(_DECL_LINE_RE.findall(src))
    for block in _DECL_BLOCK_RE.finditer(src):
        consts.update(_BLOCK_ENTRY_RE.findall(block.group(1)))
    return consts


def _opts_end(src: str, start: int) -> int:
    """Return the index of the `}` that closes an Opts literal opened just before start."""
    depth = 1
    for i in range(start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return len(src)


def fix_metric_names(md_content: str, source_dir: str, default_namespace: str = DEFAULT_NAMESPACE) -> str:
    package_consts: dict[str, dict[str, str]] = {}
    file_consts: dict[str, dict[str, str]] = {}
    sources: dict[str, str] = {}
    for root, _, files in os.walk(source_dir):
        for name in files:
            if not name.endswith(".go") or name.endswith("_test.go"):
                continue
            path = os.path.join(root, name)
            with open(path, encoding="utf-8") as f:
                src = f.read()
            consts = _string_consts(src)
            sources[path] = src
            file_consts[path] = consts
            package_consts.setdefault(os.path.dirname(path), {}).update(consts)

    # Keyed by the (name, help) pair findmetrics printed: (new name, {identifier: label}).
    fixes: dict[tuple[str, str], tuple[str, dict[str, str]]] = {}
    for path, src in sources.items():
        local = file_consts[path]
        package = package_consts[os.path.dirname(path)]
        rel = os.path.relpath(path, source_dir)
        for call in _METRIC_CALL_RE.finditer(src):
            end = _opts_end(src, call.end())
            opts = dict(_OPT_RE.findall(src[call.end():end]))
            if not opts.get("Name", "").startswith('"'):
                continue
            name = opts["Name"].strip('"')
            found = {"Namespace": "", "Subsystem": ""}
            fixed = dict(found)
            for key in found:
                value = opts.get(key, "")
                if value.startswith('"'):
                    found[key] = fixed[key] = value.strip('"')
                elif value:
                    found[key] = local.get(value, "")
                    fixed[key] = package.get(value, found[key])
                    if not fixed[key]:
                        _warn(f"cannot resolve {key} {value} for metric {name} in {rel}; its documented name may be wrong")
            found["Namespace"] = found["Namespace"] or default_namespace
            fixed["Namespace"] = fixed["Namespace"] or default_namespace
            wrong = _metric_full_name(found["Namespace"], found["Subsystem"], name)
            right = _metric_full_name(fixed["Namespace"], fixed["Subsystem"], name)

            labels: dict[str, str] = {}
            labels_match = _LABELS_RE.match(src, end + 1)
            if labels_match:
                for item in (i.strip() for i in labels_match.group(1).split(",")):
                    if re.fullmatch(r"\w+", item) and item not in local:
                        if item in package:
                            labels[item] = package[item]
                        else:
                            _warn(f"cannot resolve label {item} for metric {name} in {rel}")

            if wrong != right or labels:
                # findmetrics trims only the quotes, so a Help with escapes still matches its cell.
                fixes[(wrong, opts.get("Help", "").strip('"'))] = (right, labels)

    if not fixes:
        return md_content

    lines = md_content.splitlines()
    header, rows = lines[:2], lines[2:]
    fixed_rows = []
    for row in rows:
        cells = row.split("|")
        key = (cells[0], "|".join(cells[3:])) if len(cells) >= 4 else None
        fix = fixes.pop(key, None) if key else None
        if fix:
            new_name, labels = fix
            if new_name != cells[0]:
                print(f"    ✓ Renamed metric {cells[0]} -> {new_name}", file=sys.stderr)
                cells[0] = new_name
            if labels:
                cells[2] = ", ".join(labels.get(label, label) for label in cells[2].split(", "))
                print(f"    ✓ Resolved labels of {cells[0]}: {cells[2]}", file=sys.stderr)
        fixed_rows.append("|".join(cells))
    for (wrong, _), (right, _) in fixes.items():
        _warn(f"no row for {wrong} in the findmetrics output; expected to fix it as {right}")
    # findmetrics sorts by full name, so restore that order after renaming.
    fixed_rows.sort(key=lambda r: r.split("|", 1)[0])
    return "\n".join(header + fixed_rows) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source_dir", help="Go source tree that findmetrics scanned")
    parser.add_argument("--default-namespace", default=DEFAULT_NAMESPACE)
    args = parser.parse_args()
    sys.stdout.write(fix_metric_names(sys.stdin.read(), args.source_dir, args.default_namespace))


if __name__ == "__main__":
    main()

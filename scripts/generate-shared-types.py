#!/usr/bin/env python3
"""
Generate markdown documentation for shared types from Go source files.

This script parses Go source files in the shared package and generates
markdown documentation for types that crd-ref-docs cannot generate
(types without +kubebuilder:object:root=true annotations).
"""

import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FieldInfo:
    name: str
    go_type: str
    json_name: str
    description: str
    required: bool = False
    validation: list = field(default_factory=list)


@dataclass
class TypeInfo:
    name: str
    kind: str  # 'struct', 'alias', 'const'
    underlying_type: Optional[str] = None
    description: str = ""
    fields: list = field(default_factory=list)
    validation: list = field(default_factory=list)
    source: str = ""  # Source directory name (e.g., 'shared', 'kgateway')
    is_enterprise: bool = False  # Whether this type is from an enterprise source


def extract_doc_comment(lines: list[str], end_line: int) -> str:
    """Extract documentation comment above a declaration."""
    comments = []
    i = end_line - 1
    while i >= 0:
        line = lines[i].strip()
        if line.startswith("//"):
            comment_text = line[2:].strip()
            # Skip kubebuilder annotations and other markers
            if comment_text.startswith("+"):
                i -= 1
                continue
            comments.insert(0, comment_text)
            i -= 1
        elif line == "" and comments:
            # Empty line before comments - stop
            break
        elif line == "":
            i -= 1
        else:
            break
    return " ".join(comments)


def extract_validation_annotations(lines: list[str], end_line: int) -> list[str]:
    """Extract kubebuilder validation annotations above a declaration."""
    validations = []
    i = end_line - 1
    while i >= 0:
        line = lines[i].strip()
        if line.startswith("// +kubebuilder:validation:"):
            # Extract the validation rule
            rule = line.replace("// +kubebuilder:validation:", "")
            validations.insert(0, rule)
        elif line.startswith("//"):
            pass  # Other comments, continue looking
        elif line == "":
            i -= 1
            continue
        else:
            break
        i -= 1
    return validations


def parse_struct_fields(content: str, struct_start: int, struct_end: int, lines: list[str]) -> list[FieldInfo]:
    """Parse fields from a struct definition."""
    fields = []
    struct_content = content[struct_start:struct_end]
    
    # Find the opening brace
    brace_start = struct_content.find("{")
    if brace_start == -1:
        return fields
    
    # Get content between braces
    brace_count = 1
    i = brace_start + 1
    field_content_start = i
    
    while i < len(struct_content) and brace_count > 0:
        if struct_content[i] == "{":
            brace_count += 1
        elif struct_content[i] == "}":
            brace_count -= 1
        i += 1
    
    field_content = struct_content[field_content_start:i-1]
    
    # Parse each field line
    # Match: FieldName Type `json:"name,omitempty"`
    field_pattern = re.compile(
        r'^\s*(\w+)\s+([^\s`]+(?:\s*\[[^\]]*\][^\s`]*)?)\s*`json:"([^"]+)"',
        re.MULTILINE
    )
    
    # Also handle embedded structs: FieldName `json:",inline"`
    embedded_pattern = re.compile(
        r'^\s*(\w+)\s+`json:"([^"]+)"',
        re.MULTILINE
    )
    
    for match in field_pattern.finditer(field_content):
        field_name = match.group(1)
        field_type = match.group(2).strip()
        json_tag = match.group(3)
        
        # Parse json tag
        json_parts = json_tag.split(",")
        json_name = json_parts[0] if json_parts[0] else field_name
        required = "omitempty" not in json_tag
        
        # Find the line number for this field to get its comment
        field_line_match = re.search(
            rf'^\s*{re.escape(field_name)}\s+',
            content[struct_start:struct_end],
            re.MULTILINE
        )
        
        description = ""
        validation = []
        if field_line_match:
            # Count newlines to find line number
            field_pos = struct_start + field_line_match.start()
            line_num = content[:field_pos].count('\n')
            description = extract_doc_comment(lines, line_num)
            validation = extract_validation_annotations(lines, line_num)
        
        fields.append(FieldInfo(
            name=field_name,
            go_type=field_type,
            json_name=json_name,
            description=description,
            required=required,
            validation=validation
        ))
    
    return fields


def parse_go_file(filepath: Path, source: str = "", is_enterprise: bool = False) -> list[TypeInfo]:
    """Parse a Go file and extract type definitions."""
    types = []
    
    content = filepath.read_text()
    lines = content.split('\n')
    
    # Find type definitions
    # Pattern for: type Name struct { or type Name = string or type Name string
    type_pattern = re.compile(
        r'^type\s+(\w+)\s+(struct\s*\{|=?\s*(\w+))',
        re.MULTILINE
    )
    
    for match in type_pattern.finditer(content):
        type_name = match.group(1)
        type_def = match.group(2).strip()
        
        # Get line number for doc comment
        line_num = content[:match.start()].count('\n')
        description = extract_doc_comment(lines, line_num)
        validation = extract_validation_annotations(lines, line_num)
        
        if type_def.startswith("struct"):
            # Find the end of the struct
            brace_count = 0
            started = False
            end_pos = match.start()
            for i in range(match.start(), len(content)):
                if content[i] == "{":
                    brace_count += 1
                    started = True
                elif content[i] == "}":
                    brace_count -= 1
                    if started and brace_count == 0:
                        end_pos = i + 1
                        break
            
            fields = parse_struct_fields(content, match.start(), end_pos, lines)
            
            types.append(TypeInfo(
                name=type_name,
                kind="struct",
                description=description,
                fields=fields,
                validation=validation,
                source=source,
                is_enterprise=is_enterprise
            ))
        else:
            # Type alias
            underlying = match.group(3) if match.group(3) else type_def.replace("=", "").strip()
            types.append(TypeInfo(
                name=type_name,
                kind="alias",
                underlying_type=underlying,
                description=description,
                validation=validation,
                source=source,
                is_enterprise=is_enterprise
            ))
    
    return types


def format_go_type_as_link(go_type: str) -> str:
    """Convert a Go type to markdown with links to other types."""
    # Handle slices
    if go_type.startswith("[]"):
        inner = go_type[2:]
        return f"[]{format_go_type_as_link(inner)}"
    
    # Handle pointers
    if go_type.startswith("*"):
        inner = go_type[1:]
        return f"*{format_go_type_as_link(inner)}"
    
    # Handle maps
    if go_type.startswith("map["):
        return go_type  # Keep maps as-is for simplicity
    
    # Check if it's a custom type (starts with uppercase, not a builtin)
    builtins = {"string", "int", "int32", "int64", "bool", "float32", "float64", "byte", "error"}
    if go_type and go_type[0].isupper() and go_type.lower() not in builtins:
        # Check for package prefix
        if "." in go_type:
            parts = go_type.split(".")
            type_name = parts[-1]
            return f"[{go_type}](#{type_name.lower()})"
        return f"[{go_type}](#{go_type.lower()})"
    
    return go_type


def generate_markdown(types: list[TypeInfo], referenced_types: set[str]) -> str:
    """Generate markdown documentation for the types."""
    output = []
    output.append("")
    output.append("## Shared Types")
    output.append("")
    output.append("The following types are defined in the shared package and used across multiple APIs.")
    output.append("")
    
    # Filter to only types that are referenced
    types_to_doc = [t for t in types if t.name in referenced_types]
    
    # Group types by name and whether they're enterprise
    oss_by_name = {}  # name -> list of OSS TypeInfo
    ent_by_name = {}  # name -> list of Enterprise TypeInfo
    
    for t in types_to_doc:
        if t.is_enterprise:
            if t.name not in ent_by_name:
                ent_by_name[t.name] = []
            ent_by_name[t.name].append(t)
        else:
            if t.name not in oss_by_name:
                oss_by_name[t.name] = []
            oss_by_name[t.name].append(t)
    
    # For each name, pick the first occurrence (directories are passed in priority order)
    def pick_first(type_list: list) -> 'TypeInfo':
        """Pick the first type (from priority source based on parsing order)."""
        return type_list[0]
    
    # Get first OSS and first enterprise for each name
    best_oss = {name: pick_first(types) for name, types in oss_by_name.items()}
    best_ent = {name: pick_first(types) for name, types in ent_by_name.items()}
    
    # Find names that exist in both OSS and enterprise
    duplicates = set(best_oss.keys()) & set(best_ent.keys())
    
    # Build output list
    all_to_output = []
    
    # Add all OSS types with original names
    for name, t in best_oss.items():
        all_to_output.append((t, name))
    
    # Add enterprise types
    for name, t in best_ent.items():
        if name in duplicates:
            # This type exists in both OSS and enterprise - use different name
            display_name = f"{name} (Enterprise)"
            all_to_output.append((t, display_name))
        else:
            # This type only exists in enterprise - use original name
            all_to_output.append((t, name))
    
    # Sort alphabetically by display name
    all_to_output.sort(key=lambda x: x[1])
    
    for type_info, display_name in all_to_output:
        output.append(f"#### {display_name}")
        output.append("")
        
        if type_info.kind == "alias":
            output.append(f"_Underlying type:_ _{type_info.underlying_type}_")
            output.append("")
        
        if type_info.description:
            output.append(type_info.description)
            output.append("")
        
        if type_info.validation:
            output.append("**Validation:**")
            for v in type_info.validation:
                output.append(f"- {v}")
            output.append("")
        
        if type_info.fields:
            output.append("| Field | Type | Description |")
            output.append("|-------|------|-------------|")
            for field in type_info.fields:
                type_str = format_go_type_as_link(field.go_type)
                req_str = " **Required.**" if field.required else ""
                desc = field.description + req_str if field.description else req_str.strip()
                # Escape pipes in description
                desc = desc.replace("|", "\\|")
                output.append(f"| `{field.json_name}` | {type_str} | {desc} |")
            output.append("")
    
    return "\n".join(output)


def find_all_broken_links(doc_file: Path) -> set[str]:
    """Find all broken anchor links in a markdown file."""
    if not doc_file.exists():
        return set()
    
    content = doc_file.read_text()
    
    # Find all links like [TypeName](#typename)
    link_pattern = re.compile(r'\[([A-Z][A-Za-z0-9_]*)\]\(#([a-z][a-z0-9_]*)\)')
    
    broken = set()
    for match in link_pattern.finditer(content):
        type_name = match.group(1)
        anchor = match.group(2)
        
        # Check if the anchor exists in the document
        anchor_pattern = f"#### {type_name}"
        if anchor_pattern not in content:
            broken.add(type_name)
    
    return broken


def main():
    if len(sys.argv) < 3:
        print("Usage: generate-shared-types.py <shared_dir> <doc_file> [source_dir...]")
        print("  shared_dir: Directory containing shared Go types")
        print("  doc_file: Markdown file to append documentation to")
        print("  source_dir: Additional source directories to parse for types")
        sys.exit(1)
    
    shared_dir = Path(sys.argv[1])
    doc_file = Path(sys.argv[2])
    source_dirs = [Path(d) for d in sys.argv[3:]] if len(sys.argv) > 3 else []
    
    if not doc_file.exists():
        print(f"Doc file not found: {doc_file}")
        sys.exit(0)
    
    # Helper to detect if a directory is from enterprise repo
    def is_enterprise_source(dir_path: Path) -> bool:
        """Check if directory is from enterprise repo (contains 'enterprise' in path)."""
        return "enterprise" in str(dir_path).lower()
    
    # Parse all Go files in the shared directory
    all_types = []
    if shared_dir.exists():
        is_ent = is_enterprise_source(shared_dir)
        for go_file in shared_dir.glob("*.go"):
            if go_file.name.startswith("zz_generated"):
                continue  # Skip generated files
            types = parse_go_file(go_file, source="shared", is_enterprise=is_ent)
            all_types.extend(types)
            print(f"Parsed shared/{go_file.name}: found {len(types)} types")
    
    # Parse additional source directories for types
    for source_dir in source_dirs:
        if source_dir.exists():
            dir_name = source_dir.name
            is_ent = is_enterprise_source(source_dir)
            for go_file in source_dir.glob("*.go"):
                if go_file.name.startswith("zz_generated"):
                    continue
                types = parse_go_file(go_file, source=dir_name, is_enterprise=is_ent)
                all_types.extend(types)
                if types:
                    print(f"Parsed {dir_name}/{go_file.name}: found {len(types)} types")
    
    # Find all broken links in the document
    broken_links = find_all_broken_links(doc_file)
    print(f"Found {len(broken_links)} broken links: {broken_links}")
    
    # Find which types we can document
    type_names = {t.name for t in all_types}
    referenced = broken_links & type_names
    
    # Also find nested types
    type_map = {t.name: t for t in all_types}
    
    def add_nested_refs(type_name: str, visited: set[str]):
        if type_name in visited or type_name not in type_map:
            return
        visited.add(type_name)
        
        type_info = type_map[type_name]
        for field in type_info.fields:
            clean_type = field.go_type.replace("[]", "").replace("*", "")
            if clean_type in type_map and clean_type not in referenced:
                referenced.add(clean_type)
                add_nested_refs(clean_type, visited)
    
    visited = set()
    for name in list(referenced):
        add_nested_refs(name, visited)
    
    print(f"Types to document: {referenced}")
    
    if not referenced:
        print("No missing type references found that we can document")
        # Report any remaining broken links
        remaining = broken_links - type_names
        if remaining:
            print(f"Warning: These broken links could not be resolved: {remaining}")
        sys.exit(0)
    
    # Generate markdown for referenced types
    markdown = generate_markdown(all_types, referenced)
    
    # Append to doc file
    with open(doc_file, "a") as f:
        f.write(markdown)
    
    print(f"Successfully appended documentation for {len(referenced)} types")
    
    # Report any remaining broken links
    remaining = broken_links - referenced
    if remaining:
        print(f"Warning: These broken links could not be resolved: {remaining}")


if __name__ == "__main__":
    main()

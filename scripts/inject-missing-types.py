#!/usr/bin/env python3
"""
Post-process API documentation to inject missing type definitions.

This script identifies types that are referenced in the generated API docs
but don't have their own documentation sections (e.g., types only used as
embedded structs, array elements, or pointers), then extracts their definitions
from Go source files and injects them into the documentation.
"""

import re
import os
import sys
from typing import Dict, List, Set, Tuple, Optional


def find_referenced_types(markdown_content: str) -> Set[str]:
    """Find all type names referenced in markdown links."""
    # Pattern matches: [TypeName](#typename) or [TypeName](#typename-other)
    pattern = r'\[([A-Z][a-zA-Z0-9]+)\]\(#[a-z0-9-]+\)'
    matches = re.findall(pattern, markdown_content)
    return set(matches)


def find_documented_types(markdown_content: str) -> Set[str]:
    """Find all types that have documentation sections."""
    # Pattern matches: #### TypeName (section headers)
    pattern = r'^#### ([A-Z][a-zA-Z0-9]+)$'
    matches = re.findall(pattern, markdown_content, re.MULTILINE)
    return set(matches)


def find_missing_types(markdown_content: str) -> Set[str]:
    """Find types that are referenced but not documented."""
    referenced = find_referenced_types(markdown_content)
    documented = find_documented_types(markdown_content)
    
    # Also check for types that appear as empty structs (these need field injection)
    # Find sections that show "_Underlying type:_" with no field table
    empty_structs = set()
    sections = re.split(r'(?=^#### )', markdown_content, flags=re.MULTILINE)
    for section in sections:
        if not section.strip().startswith('#### '):
            continue
        header_match = re.match(r'^#### ([A-Z][a-zA-Z0-9]+)', section)
        if header_match:
            type_name = header_match.group(1)
            # Check if this section has "_Underlying type:_" (with or without hyperlink) but no field table
            has_underlying_type = '_Underlying type:_' in section
            has_field_table = '| Field |' in section
            if has_underlying_type and not has_field_table:
                empty_structs.add(type_name)
    
    # Types referenced but not documented, or documented as empty structs
    missing = (referenced - documented) | empty_structs
    
    # Filter out known types that shouldn't be documented (like List types)
    missing = {t for t in missing if not t.endswith('List')}
    
    return missing


def parse_go_struct(go_file_path: str, type_name: str) -> Optional[Dict]:
    """Parse a Go file to extract struct definition for a given type."""
    try:
        with open(go_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            content = ''.join(lines)
    except Exception as e:
        print(f"    Warning: Could not read {go_file_path}: {e}")
        return None
    
    # Find the struct definition line
    struct_start = None
    for i, line in enumerate(lines):
        if re.match(rf'^\s*type\s+{re.escape(type_name)}\s+struct', line):
            struct_start = i
            break
    
    if struct_start is None:
        return None
    
    # Extract doc comment (lines before struct definition)
    # Skip +kubebuilder validation lines
    doc_lines = []
    for i in range(struct_start - 1, -1, -1):
        line = lines[i].strip()
        if line.startswith('// +'):
            # Skip kubebuilder markers
            continue
        elif line.startswith('//'):
            # Regular comment - collect it
            doc_lines.insert(0, line[2:].strip())
        elif line == '':
            # Empty line - continue
            continue
        else:
            # Non-comment, non-empty line - stop
            break
    doc_comment = '\n'.join(doc_lines)
    
    # Find the end of the struct (matching braces)
    brace_count = 0
    struct_end = struct_start
    in_struct = False
    
    for i in range(struct_start, len(lines)):
        line = lines[i]
        for char in line:
            if char == '{':
                brace_count += 1
                in_struct = True
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and in_struct:
                    struct_end = i
                    break
        if brace_count == 0 and in_struct:
            break
    
    # Extract struct body
    struct_body_lines = lines[struct_start:struct_end + 1]
    struct_body = ''.join(struct_body_lines)
    
    # Extract fields - more robust parsing
    fields = []
    i = struct_start + 1
    while i < struct_end:
        line = lines[i]
        
        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith('//'):
            i += 1
            continue
        
        # Check if this is a field definition
        # Pattern: FieldName Type `json:"name"` (Type can contain spaces, *, [], etc.)
        # More flexible pattern that handles complex types
        field_match = re.match(r'^\s*([A-Z][a-zA-Z0-9]+)\s+(.+?)\s+`json:"([^"]+)"', line)
        if field_match:
            field_name = field_match.group(1)
            field_type = field_match.group(2).strip()
            json_name = field_match.group(3)
            
            # Remove ,omitempty suffix from JSON name
            if json_name.endswith(',omitempty'):
                json_name = json_name[:-10]
            
            # Get comment from previous lines
            # Skip +kubebuilder lines but continue looking backwards for actual comments
            comment_lines = []
            j = i - 1
            while j >= struct_start:
                prev_line = lines[j].strip()
                if prev_line.startswith('// +'):
                    # Skip kubebuilder markers but continue looking backwards
                    j -= 1
                    continue
                elif prev_line.startswith('//'):
                    # This is a regular comment - collect it
                    comment_lines.insert(0, prev_line[2:].strip())
                    j -= 1
                elif prev_line == '':
                    # Empty line - continue looking backwards
                    j -= 1
                else:
                    # Non-comment, non-empty line - stop
                    break
            comment = ' '.join(comment_lines)
            
            # Extract validation markers and defaults from preceding lines
            validation = []
            default_value = ''
            preceding = ''.join(lines[max(struct_start, i-10):i])
            
            if re.search(r'\+required', preceding):
                validation.append('Required')
            if re.search(r'\+optional', preceding):
                validation.append('Optional')
            
            # Extract default value
            if match := re.search(r'\+kubebuilder:default="([^"]+)"', preceding):
                default_value = match.group(1)
            elif match := re.search(r'\+kubebuilder:default=([^\s]+)', preceding):
                default_value = match.group(1)
            
            # Extract validation constraints
            for pattern, label in [
                (r'MinItems=(\d+)', 'MinItems'),
                (r'MaxItems=(\d+)', 'MaxItems'),
                (r'Minimum=(\d+)', 'Minimum'),
                (r'Maximum=(\d+)', 'Maximum'),
                (r'MinLength=(\d+)', 'MinLength'),
                (r'MaxLength=(\d+)', 'MaxLength'),
            ]:
                if match := re.search(pattern, preceding):
                    validation.append(f'{label}: {match.group(1)}')
            
            if match := re.search(r'Enum=([^\]]+)', preceding):
                validation.append(f'Enum: [{match.group(1)}]')
            
            # Extract Pattern validation (simplified - just note it exists)
            if re.search(r'\+kubebuilder:validation:Pattern=', preceding):
                validation.append('Pattern')
            
            # Extract XValidation rules (simplified - just note they exist)
            if re.search(r'\+kubebuilder:validation:XValidation:', preceding):
                validation.append('XValidation')
            
            fields.append({
                'name': field_name,
                'type': field_type,
                'json_name': json_name,
                'comment': comment,
                'validation': validation,
                'default': default_value
            })
        
        i += 1
    
    return {
        'name': type_name,
        'fields': fields,
        'doc_comment': doc_comment
    }


def format_type_link(type_name: str) -> str:
    """Format a type name as a markdown link."""
    # Remove package prefixes for known types
    if '.' in type_name:
        # Extract just the type name (last part after dot)
        type_name = type_name.split('.')[-1]
    # Create anchor link (lowercase, no special chars)
    anchor = type_name.lower()
    return f"_[{type_name}](#{anchor})_"


def format_type_markdown(type_info: Dict) -> str:
    """Format a type definition as markdown matching crd-ref-docs format."""
    lines = []
    lines.append(f"#### {type_info['name']}")
    lines.append("")
    
    # Don't output doc_comment if it's empty or just kubebuilder markers
    if type_info.get('doc_comment') and type_info['doc_comment'].strip():
        # Format doc comment (skip any kubebuilder lines that might have slipped through)
        doc_lines = []
        for line in type_info['doc_comment'].split('\n'):
            stripped = line.strip()
            # Skip kubebuilder validation lines
            if stripped and not stripped.startswith('+kubebuilder:'):
                doc_lines.append(stripped)
        if doc_lines:
            lines.extend(doc_lines)
            lines.append("")
    
    lines.append("")
    lines.append("_Appears in:_")
    lines.append("- [Various types](#various-types)")
    lines.append("")
    
    if type_info['fields']:
        lines.append("| Field | Description | Default | Validation |")
        lines.append("| --- | --- | --- | --- |")
        
        for field in type_info['fields']:
            # Format field type (simplify complex types and create proper links)
            field_type = field['type']
            
            # Convert pointer types
            if field_type.startswith('*'):
                inner_type = field_type[1:]
                field_type = format_type_link(inner_type)
            # Convert array types
            elif field_type.startswith('[]'):
                inner_type = field_type[2:]
                field_type = f"{format_type_link(inner_type)} array"
            # Handle map types
            elif field_type.startswith('map['):
                # Extract key and value types from map[key]value
                map_match = re.match(r'map\[([^\]]+)\](.+)', field_type)
                if map_match:
                    key_type = map_match.group(1)
                    value_type = map_match.group(2)
                    field_type = f"object (keys:{key_type}, values:{format_type_link(value_type)})"
                else:
                    field_type = f"_{field_type}_"
            # Handle known Kubernetes types
            elif 'k8s.io' in field_type or 'sigs.k8s.io' in field_type:
                # Extract type name and create link
                type_name = field_type.split('.')[-1]
                # Get Kubernetes version from environment (same as crd-ref-docs uses)
                # Handle empty string case - if not set or empty, use default
                kube_version = os.environ.get('KUBE_VERSION') or '1.31'
                # Check if it's a known type that should link to Kubernetes docs
                if 'k8s.io/api/core/v1' in field_type:
                    field_type = f"_[{type_name}](https://kubernetes.io/docs/reference/generated/kubernetes-api/v{kube_version}/#{type_name.lower()}-v1-core)_"
                elif 'k8s.io/apimachinery' in field_type:
                    if 'Duration' in type_name:
                        # Match crd-ref-docs format: use Kubernetes API docs with version
                        field_type = f"_[{type_name}](https://kubernetes.io/docs/reference/generated/kubernetes-api/v{kube_version}/#duration-v1-meta)_"
                    elif 'Time' in type_name:
                        field_type = f"_[{type_name}](https://kubernetes.io/docs/reference/generated/kubernetes-api/v{kube_version}/#time-v1-meta)_"
                    else:
                        field_type = format_type_link(type_name)
                elif 'gateway-api' in field_type:
                    field_type = f"_[{type_name}](https://gateway-api.sigs.k8s.io/reference/spec/#{type_name.lower()})_"
                else:
                    field_type = format_type_link(type_name)
            else:
                # Regular type - create link
                field_type = format_type_link(field_type)
            
            # Format validation
            validation_str = ' <br />'.join(field['validation']) if field['validation'] else ''
            
            # Format description - clean up and format multi-line comments
            description = field['comment'] or ''
            # Replace newlines with <br /> for markdown
            description = description.replace('\n', '<br />')
            
            # Format default value
            default_str = field.get('default', '') or ''
            
            lines.append(f"| `{field['json_name']}` {field_type} | {description} | {default_str} | {validation_str} |")
    else:
        lines.append("_Underlying type:_ _struct_")
    
    lines.append("")
    return '\n'.join(lines)


def find_insertion_point(markdown_content: str, type_name: str) -> int:
    """Find where to insert a new type definition in alphabetical order."""
    # Find all type section headers
    type_headers = []
    for match in re.finditer(r'^#### ([A-Z][a-zA-Z0-9]+)$', markdown_content, re.MULTILINE):
        type_headers.append((match.group(1), match.start()))
    
    # Sort types alphabetically
    type_headers.sort(key=lambda x: x[0].lower())
    
    # Find insertion point
    for i, (name, pos) in enumerate(type_headers):
        if name.lower() > type_name.lower():
            return pos
    
    # If we get here, insert at the end before the last newline
    return len(markdown_content)


def inject_missing_types(markdown_file: str, go_source_dir: str) -> bool:
    """Inject missing type definitions into markdown file."""
    print(f"  → Checking for missing types in {markdown_file}")
    
    # Read markdown content
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"    Error reading {markdown_file}: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Find missing types
    missing_types = find_missing_types(content)
    
    if not missing_types:
        print(f"    ✓ No missing types found")
        return True
    
    print(f"    Found {len(missing_types)} missing types: {', '.join(sorted(missing_types))}")
    
    # Find Go source files
    go_files = []
    if os.path.isdir(go_source_dir):
        for root, dirs, files in os.walk(go_source_dir):
            for file in files:
                if file.endswith('.go') and not file.startswith('zz_'):
                    go_files.append(os.path.join(root, file))
    
    # Extract type definitions
    type_definitions = {}
    for type_name in missing_types:
        found = False
        for go_file in go_files:
            try:
                type_info = parse_go_struct(go_file, type_name)
                if type_info and type_info.get('fields'):
                    type_definitions[type_name] = type_info
                    print(f"    ✓ Found definition for {type_name} with {len(type_info['fields'])} fields")
                    found = True
                    break
            except Exception as e:
                print(f"    ⚠ Error parsing {go_file} for {type_name}: {e}")
                continue
        if not found:
            print(f"    ⚠ Could not find definition for {type_name}")
    
    if not type_definitions:
        print(f"    ⚠ No type definitions found in Go source")
        return False
    
    # Generate markdown for missing types
    type_markdowns = {}
    for type_name, type_info in type_definitions.items():
        type_markdowns[type_name] = format_type_markdown(type_info)
    
    # Replace existing empty sections or insert new ones
    new_content = content
    
    for type_name, type_markdown in sorted(type_markdowns.items(), key=lambda x: x[0].lower()):
        # Check if type already has a section (even if empty)
        # Find the section header
        header_pattern = rf'^#### {re.escape(type_name)}$'
        header_match = re.search(header_pattern, new_content, re.MULTILINE)
        
        if header_match:
            # Find the end of this section (next #### or ## header, or end of file)
            section_start = header_match.start()
            section_end = len(new_content)
            
            # Look for next section header
            next_header = re.search(r'^#### |^## ', new_content[section_start + 1:], re.MULTILINE)
            if next_header:
                section_end = section_start + 1 + next_header.start()
            
            existing_section = new_content[section_start:section_end]
            
            # Extract "Appears in" section from existing markdown
            appears_in_match = re.search(r'_Appears in:_\n((?:- \[[^\]]+\]\(#[^\)]+\)\n?)+)', existing_section)
            appears_in_lines = []
            if appears_in_match:
                appears_in_lines = [line.strip() for line in appears_in_match.group(1).strip().split('\n') if line.strip()]
            
            # Only replace if it's an empty struct section (check for _Underlying type:_ without field table)
            has_underlying_type = '_Underlying type:_' in existing_section
            has_field_table = '| Field |' in existing_section
            if has_underlying_type and not has_field_table:
                # Update the markdown to include the "Appears in" section
                if appears_in_lines:
                    # Replace the "Appears in" section in the generated markdown
                    updated_markdown = re.sub(
                        r'_Appears in:_\n- \[Various types\]\(#various-types\)',
                        '_Appears in:_\n' + '\n'.join(appears_in_lines),
                        type_markdown
                    )
                else:
                    updated_markdown = type_markdown
                
                new_content = new_content[:section_start] + updated_markdown + new_content[section_end:]
                print(f"    ✓ Replaced empty section for {type_name}")
            else:
                print(f"    ⚠ Skipping {type_name} - already has fields documented")
        else:
            # Insert new section in alphabetical order
            # Find insertion point
            type_headers = []
            for m in re.finditer(r'^#### ([A-Z][a-zA-Z0-9]+)$', new_content, re.MULTILINE):
                type_headers.append((m.group(1), m.start()))
            
            # Sort and find where to insert
            type_headers.sort(key=lambda x: x[0].lower())
            insert_pos = len(new_content)
            
            for i, (name, pos) in enumerate(type_headers):
                if name.lower() > type_name.lower():
                    # Find end of previous section
                    if i > 0:
                        prev_name, prev_pos = type_headers[i-1]
                        # Find end of previous section
                        next_section = new_content.find('\n#### ', prev_pos + 1)
                        if next_section == -1:
                            next_section = new_content.find('\n## ', prev_pos + 1)
                        if next_section != -1:
                            insert_pos = next_section
                    else:
                        # Insert before first section
                        insert_pos = pos
                    break
            
            # Insert the new section
            new_content = new_content[:insert_pos] + '\n' + type_markdown + new_content[insert_pos:]
            print(f"    ✓ Inserted new section for {type_name}")
    
    # Write back
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"    ✓ Processed {len(type_definitions)} type definitions")
    return True


def main():
    """Main entry point."""
    print("Starting inject-missing-types.py...")
    try:
        if len(sys.argv) < 3:
            print("Usage: inject-missing-types.py <markdown-file> <go-source-dir>")
            sys.exit(1)
        
        markdown_file = sys.argv[1]
        go_source_dir = sys.argv[2]
        
        if not os.path.exists(markdown_file):
            print(f"Error: Markdown file not found: {markdown_file}")
            sys.exit(1)
        
        if not os.path.exists(go_source_dir):
            print(f"Error: Go source directory not found: {go_source_dir}")
            sys.exit(1)
        
        success = inject_missing_types(markdown_file, go_source_dir)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()


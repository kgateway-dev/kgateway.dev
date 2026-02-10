#!/usr/bin/env python3
"""
Simple test script to demonstrate missing types issue
"""
import re
import sys

def find_missing_types(markdown_file):
    """Find types that are referenced but not documented."""
    with open(markdown_file, 'r') as f:
        content = f.read()
    
    # Find referenced types
    referenced = set(re.findall(r'\[([A-Z][a-zA-Z0-9]+)\]\(#[a-z0-9-]+\)', content))
    
    # Find documented types
    documented = set(re.findall(r'^#### ([A-Z][a-zA-Z0-9]+)$', content, re.MULTILINE))
    
    # Find empty structs
    empty_structs = set()
    sections = re.split(r'(?=^#### )', content, flags=re.MULTILINE)
    for section in sections:
        if not section.strip().startswith('#### '):
            continue
        header_match = re.match(r'^#### ([A-Z][a-zA-Z0-9]+)', section)
        if header_match:
            type_name = header_match.group(1)
            if '_Underlying type:_ _struct_' in section and '| Field |' not in section:
                empty_structs.add(type_name)
    
    missing = (referenced - documented) | empty_structs
    missing = {t for t in missing if not t.endswith('List')}
    
    return missing, referenced, documented, empty_structs

if __name__ == '__main__':
    api_file = 'content/docs/agentgateway/main/reference/api.md'
    
    missing, referenced, documented, empty_structs = find_missing_types(api_file)
    
    print("=" * 60)
    print("MISSING TYPES ANALYSIS")
    print("=" * 60)
    print(f"\nReferenced types: {len(referenced)}")
    print(f"Documented types: {len(documented)}")
    print(f"Empty structs: {len(empty_structs)}")
    print(f"\nMissing types: {len(missing)}")
    print("\nMissing type details:")
    for t in sorted(missing):
        is_referenced = t in referenced
        is_documented = t in documented
        is_empty = t in empty_structs
        status = []
        if is_referenced and not is_documented:
            status.append("referenced but not documented")
        if is_empty:
            status.append("documented as empty struct")
        print(f"  - {t}: {', '.join(status)}")
    
    print("\n" + "=" * 60)
    print("SPECIFIC ISSUES:")
    print("=" * 60)
    
    # Check specific types that must be documented
    failures = []
    for type_name in ['BackendSimple', 'RemoteJWKS', 'RateLimitDescriptorEntry', 'KubernetesResourceOverlay']:
        print(f"\n{type_name}:")
        if type_name in referenced:
            print(f"  ✓ Referenced in docs")
        else:
            print(f"  ✗ Not referenced")
            failures.append(f"{type_name} is not referenced in docs")
        if type_name in documented:
            print(f"  ✓ Has documentation section")
            if type_name in empty_structs:
                print(f"  ⚠ But shows as empty struct (no fields)")
                failures.append(f"{type_name} is documented as empty struct")
        else:
            print(f"  ✗ No documentation section")
            failures.append(f"{type_name} is not documented")

    if failures:
        print(f"\n{'=' * 60}")
        print("FAILURES:")
        print('=' * 60)
        for f in failures:
            print(f"  ✗ {f}")
        sys.exit(1)


#!/usr/bin/env python3
"""
Generate API, Helm, and Metrics reference documentation for kgateway.dev

This script processes versions from hugo.yaml and generates documentation
for each version by cloning the kgateway repository and running doc generators.
"""

import json
import sys
import subprocess
import os
import re


def resolve_tag_for_version(version, link_version):
    '''Resolve the git tag to use for a given version (for release triggers)'''
    if link_version == 'main':
        return 'main'
    
    # For other linkVersions, get the latest tag matching the version pattern
    try:
        result = subprocess.run(['git', 'ls-remote', '--tags', '--sort=-version:refname', 'https://github.com/kgateway-dev/kgateway.git'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            # Filter tags that match our version pattern
            # Create regex pattern: 2.1.x becomes v2\.1\.\d+
            version_pattern = version.replace('.x', r'\.\d+')
            pattern = f'v{version_pattern}'
            matching_tags = []
            for line in result.stdout.strip().split('\n'):
                if 'refs/tags/' in line:
                    tag_name = line.split('/')[-1]
                    if re.match(pattern, tag_name) and not any(suffix in tag_name for suffix in ['-rc', '-beta', '-main', '-agw']):
                        matching_tags.append(tag_name)
            
            if matching_tags:
                # Sort by version and take the latest
                matching_tags.sort(key=lambda x: [int(n) for n in x.replace('v', '').split('.')], reverse=True)
                return matching_tags[0]
            else:
                print(f'No stable tags found for version {version}')
                return None
        else:
            print(f'No tags found in repository for version {version}')
            return None
    except subprocess.CalledProcessError as e:
        print(f'Error fetching tags for version {version}: {e}')
        return None


def resolve_branch_for_version(version, link_version):
    '''Resolve the git branch to use for a given version (for manual triggers)'''
    if link_version == 'main':
        return 'main'
    
    # For other linkVersions, construct the branch name from the version
    # e.g., version "2.1.x" -> branch "v2.1.x"
    branch_name = f'v{version}'
    
    # Verify the branch exists in the remote repository
    try:
        result = subprocess.run(['git', 'ls-remote', '--heads', 'https://github.com/kgateway-dev/kgateway.git', branch_name], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print(f'   Found branch: {branch_name}')
            return branch_name
        else:
            print(f'   Warning: Branch {branch_name} not found, trying to use it anyway')
            # Still return the branch name - clone will fail if it doesn't exist
            return branch_name
    except subprocess.CalledProcessError as e:
        print(f'   Warning: Error checking branch {branch_name}: {e}')
        # Still return the branch name - clone will fail if it doesn't exist
        return branch_name


def clone_repository(ref, kgateway_dir='kgateway'):
    '''Clone the kgateway repository at the specified branch or tag'''
    # Clean up any existing directory
    if os.path.exists(kgateway_dir):
        subprocess.run(['rm', '-rf', kgateway_dir], check=True)
    
    # Clone repository
    if ref == 'main':
        subprocess.run(['git', 'clone', '--branch', 'main', '--depth', '1', 'https://github.com/kgateway-dev/kgateway.git', kgateway_dir], check=True)
    else:
        subprocess.run(['git', 'clone', '--depth', '1', '--branch', ref, 'https://github.com/kgateway-dev/kgateway.git', kgateway_dir], check=True)


def is_version_2_2_or_later(version):
    '''Check if version is 2.2.x or later'''
    try:
        # Parse version string (e.g., "2.2.x", "2.1.x", "main")
        if version == 'main':
            return True  # main is always latest
        parts = version.split('.')
        if len(parts) >= 2:
            major = int(parts[0])
            minor = int(parts[1].replace('x', '0'))
            return major > 2 or (major == 2 and minor >= 2)
        return False
    except (ValueError, IndexError):
        return False


def extract_package_section(content, package_name):
    '''Extract a specific package section from generated markdown'''
    lines = content.split('\n')
    
    # Find the Packages section header
    packages_start = None
    packages_end = None
    
    for i, line in enumerate(lines):
        if line.strip() == '## Packages':
            packages_start = i
        elif packages_start is not None and line.strip().startswith('## ') and not line.strip() == '## Packages':
            packages_end = i
            break
    
    if packages_start is None:
        return None
    
    if packages_end is None:
        packages_end = len(lines)
    
    # Extract and filter the Packages list
    packages_section = ['## Packages']
    found_package = False
    
    for i in range(packages_start + 1, packages_end):
        line = lines[i]
        # Check if this line contains the target package
        if package_name in line:
            packages_section.append(line)
            found_package = True
        elif found_package and line.strip() == '':
            # Add empty line after packages list
            packages_section.append('')
            break
    
    if not found_package:
        return None
    
    # Find the package section header
    # Pattern: ## package.name/v1alpha1
    package_header_pattern = rf'^## {re.escape(package_name)}$'
    
    package_start_idx = None
    
    # Find the start of the package section
    for i, line in enumerate(lines):
        if re.match(package_header_pattern, line.strip()):
            package_start_idx = i
            break
    
    if package_start_idx is None:
        return None
    
    # Find the end of the package section (next ## header or end of file)
    package_end_idx = len(lines)
    for i in range(package_start_idx + 1, len(lines)):
        if lines[i].startswith('## '):
            package_end_idx = i
            break
    
    # Extract the package section content
    package_section_lines = lines[package_start_idx:package_end_idx]
    
    # Combine packages section and package content
    result = '\n'.join(packages_section + package_section_lines)
    return result


def _post_process_api_docs(api_file):
    '''Apply post-processing to API docs file'''
    # Format the generated docs with sed commands
    subprocess.run(['sed', '-i', 's/Required: {}/Required/g', api_file], check=True)
    subprocess.run(['sed', '-i', 's/Optional: {}/Optional/g', api_file], check=True)
    subprocess.run(['sed', '-i', '/^# API Reference$/,/^$/d', api_file], check=True)
    
    # Additional post-processing to clean up complex struct types
    with open(api_file, 'r') as f:
        content = f.read()
    
    # Replace complex struct type definitions with simple "struct"
    # Pattern matches: _Underlying type:_ _[struct{...}...]_
    content = re.sub(
        r'_Underlying type:_ _\[struct\{[^\]]+\}\]\([^\)]+\)_',
        '_Underlying type:_ _struct_',
        content
    )
    
    # Handle empty struct{} patterns
    content = re.sub(
        r'_Underlying type:_ _\[struct\{\}\]\(#struct\{\}\)_',
        '_Underlying type:_ _struct_',
        content
    )
    
    # Also handle cases without the link wrapper
    content = re.sub(
        r'_Underlying type:_ _struct\{[^\}]+\}_',
        '_Underlying type:_ _struct_',
        content
    )
    
    with open(api_file, 'w') as f:
        f.write(content)


def generate_api_docs(version, link_version, url_path, kgateway_dir='kgateway'):
    '''Generate API reference documentation'''
    print(f'  → Generating API docs for version {version}')
    
    # Check if the API directory exists
    api_path = f'{kgateway_dir}/api/v1alpha1/'
    if not os.path.exists(api_path):
        print(f'    Warning: API directory {api_path} does not exist, skipping API docs')
        return False
    
    # Generate API docs using individual subprocess calls
    with open('scripts/crd-ref-docs-config.yaml', 'r') as f:
        config_content = f.read()
    
    # Substitute environment variables in config (handle both $VAR and ${VAR} formats)
    kube_version = os.environ.get('KUBE_VERSION', '')
    config_content = config_content.replace('${KUBE_VERSION}', kube_version)
    
    with open(f'crd-ref-docs-config-{link_version}.yaml', 'w') as f:
        f.write(config_content)
    
    subprocess.run([
        'go', 'run', 'github.com/elastic/crd-ref-docs@v0.1.0',
        f'--source-path={api_path}',
        '--renderer=markdown',
        '--output-path=./',
        f'--config=crd-ref-docs-config-{link_version}.yaml'
    ], check=True)
    
    os.remove(f'crd-ref-docs-config-{link_version}.yaml')
    
    # Read the generated content once
    with open('./out.md') as f:
        generated_content = f.read()
    
    os.remove('./out.md')
    
    # Check if version is 2.2.x or later
    split_api = is_version_2_2_or_later(version)
    
    if split_api:
        # For 2.2.x+, split by package
        print(f'    Version {version} uses split API - generating separate docs per package')
        
        # Extract agentgateway.dev/v1alpha1 package
        agentgateway_content = extract_package_section(generated_content, 'agentgateway.dev/v1alpha1')
        if agentgateway_content:
            target_path = f'content/docs/agentgateway/{url_path}/reference/'
            os.makedirs(target_path, exist_ok=True)
            api_file = f'{target_path}api.md'
            
            with open(api_file, 'w') as f:
                f.write('---\n')
                f.write('title: API reference\n')
                f.write('weight: 10\n')
                f.write('---\n\n')
                f.write(agentgateway_content)
            
            # Apply post-processing
            _post_process_api_docs(api_file)
            print(f'    ✓ Generated agentgateway API docs in {api_file}')
        else:
            print(f'    ⚠ Warning: Could not extract agentgateway.dev/v1alpha1 package')
        
        # Extract gateway.kgateway.dev/v1alpha1 package
        envoy_content = extract_package_section(generated_content, 'gateway.kgateway.dev/v1alpha1')
        if envoy_content:
            target_path = f'content/docs/envoy/{url_path}/reference/'
            os.makedirs(target_path, exist_ok=True)
            api_file = f'{target_path}api.md'
            
            with open(api_file, 'w') as f:
                f.write('---\n')
                f.write('title: API reference\n')
                f.write('weight: 10\n')
                f.write('---\n\n')
                f.write(envoy_content)
            
            # Apply post-processing
            _post_process_api_docs(api_file)
            print(f'    ✓ Generated envoy API docs in {api_file}')
        else:
            print(f'    ⚠ Warning: Could not extract gateway.kgateway.dev/v1alpha1 package')
        
        return True
    else:
        # For earlier versions, write same content to both directories (legacy behavior)
        print(f'    Version {version} uses unified API - generating same docs for both sections')
        
        for doc_dir in ['envoy', 'agentgateway']:
            target_path = f'content/docs/{doc_dir}/{url_path}/reference/'
            os.makedirs(target_path, exist_ok=True)
            
            api_file = f'{target_path}api.md'
            
            # Create API reference file with frontmatter
            with open(api_file, 'w') as f:
                f.write('---\n')
                f.write('title: API reference\n')
                f.write('weight: 10\n')
                f.write('---\n\n')
                f.write(generated_content)
            
            # Apply post-processing
            _post_process_api_docs(api_file)
            print(f'    ✓ Generated API docs in {api_file}')
        
        return True


def generate_helm_docs(version, link_version, url_path, kgateway_dir='kgateway'):
    '''Generate Helm chart reference documentation'''
    print(f'  → Generating Helm docs for version {version}')
    
    # Generate Helm docs for each chart
    charts = ['kgateway:kgateway', 'kgateway-crds:kgateway-crds']
    generated_any = False
    
    for chart in charts:
        dir_name, file_name = chart.split(':')
        helm_path = f'{kgateway_dir}/install/helm/{dir_name}'
        
        # Check if Helm directory exists
        if not os.path.exists(helm_path):
            print(f'    Warning: Helm directory {helm_path} does not exist, skipping {file_name}')
            continue
        
        result = subprocess.run([
            'go', 'run', 'github.com/norwoodj/helm-docs/cmd/helm-docs@v1.14.2',
            f'--chart-search-root={helm_path}',
            '--dry-run'
        ], capture_output=True, text=True, check=True)
        
        # Write the raw helm-docs output to assets directory
        # Use actual version numbers (2.2.x, 2.1.x, etc.) not linkVersion (main, latest)
        # This prevents overwriting when promoting versions
        assets_path = f'assets/docs/pages/reference/helm/{version}/'
        os.makedirs(assets_path, exist_ok=True)
        
        helm_file = f'{assets_path}{file_name}.md'
        
        with open(helm_file, 'w') as f:
            f.write(result.stdout)
        
        # Remove badge line and following empty line
        subprocess.run(['sed', '-i', '/!\[Version:/,/^$/d', helm_file], check=True)
        
        # Remove the title (# heading) and description lines from the top
        # These will be hardcoded in the content files instead
        # Remove lines 1-3 which contain: title, blank line, description
        subprocess.run(['sed', '-i', '1,3d', helm_file], check=True)
        
        # Add a note for charts with no configurable values (like kgateway-crds)
        with open(helm_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Normalize any bare type=info callouts before further processing
        content = content.replace('{{< callout type=info >}}', '{{< callout type="info" >}}')
        
        # If no values table, append callout (once). Otherwise normalize callout quotes.
        if '## Values' not in content or ('## Values' in content and '|-----|' not in content):
            note = '\n\n{{< callout type="info" >}}\nNo configurable values are currently available for this chart.\n{{< /callout >}}\n'
            if '{{< callout' not in content:
                content = content.rstrip() + note
        
        # Swap Default and Description columns in the values table
        swapped_lines = []
        in_table = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith('| Key ') and 'Default' in line and 'Description' in line:
                in_table = True
                swapped_lines.append('| Key | Type | Description | Default |')
                continue
            if in_table and stripped.startswith('|-----'):
                swapped_lines.append('|-----|------|-------------|---------|')
                continue
            if in_table:
                if not stripped.startswith('|'):
                    in_table = False
                    swapped_lines.append(line)
                    continue
                parts = [p.strip() for p in line.split('|')]
                # Expect 6 elements with leading/trailing blanks; ensure we have enough
                if len(parts) >= 6:
                    key, typ, default, desc = parts[1], parts[2], parts[3], parts[4]
                    swapped_lines.append(f'| {key} | {typ} | {desc} | {default} |')
                else:
                    swapped_lines.append(line)
            else:
                swapped_lines.append(line)
        content = '\n'.join(swapped_lines)
        
        with open(helm_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f'    ✓ Generated Helm docs in {helm_file}')
        
        generated_any = True
    
    return generated_any


def generate_metrics_docs(version, link_version, url_path, kgateway_dir='kgateway'):
    '''Generate control plane metrics documentation'''
    print(f'  → Generating metrics docs for version {version}')
    
    os.makedirs(f'assets/docs/snippets/{link_version}', exist_ok=True)
    
    # Check if metrics tool exists
    metrics_tool_path = f'{kgateway_dir}/pkg/metrics/cmd/findmetrics/main.go'
    if not os.path.exists(metrics_tool_path):
        print(f'    Warning: Metrics tool {metrics_tool_path} does not exist, skipping metrics docs')
        return False
    
    # Run the metrics finder tool
    result = subprocess.run([
        'go', 'run', metrics_tool_path, 
        '--markdown', f'./{kgateway_dir}'
    ], capture_output=True, text=True, check=True)
    
    with open(f'assets/docs/snippets/{link_version}/metrics-control-plane.md', 'w') as f:
        f.write(result.stdout)
    
    print(f'    ✓ Generated metrics docs in assets/docs/snippets/{link_version}/metrics-control-plane.md')
    return True


def main():
    # Main processing logic - determine target version
    event_name = os.environ.get('GITHUB_EVENT_NAME', '')
    release_tag = os.environ.get('GITHUB_RELEASE_TAG', '')
    input_version = os.environ.get('INPUT_VERSION', 'all')
    
    is_release_trigger = event_name == 'release'
    
    if is_release_trigger:
        # Release trigger: determine version from release tag
        print(f'🎉 Release trigger detected: {release_tag}')
        
        # Parse release tag (e.g., "v2.1.1") to version family (e.g., "2.1.x")
        if release_tag.startswith('v'):
            version_parts = release_tag[1:].split('.')  # Remove 'v' and split
            if len(version_parts) >= 2:
                target_version = f'{version_parts[0]}.{version_parts[1]}.x'
                print(f'📋 Mapped release {release_tag} to version family: {target_version}')
            else:
                print(f'❌ Invalid release tag format: {release_tag}')
                sys.exit(1)
        else:
            print(f'❌ Release tag does not start with "v": {release_tag}')
            sys.exit(1)
    else:
        # Manual dispatch: use input version
        target_version = input_version
        print(f'👤 Manual trigger with version: {target_version}')
    
    with open('versions.json', 'r') as f:
        versions = json.load(f)
    
    # Filter versions based on target
    if target_version != 'all':
        all_versions = versions  # Keep original list for error reporting
        versions = [v for v in versions if v['version'] == target_version]
        if not versions:
            print(f'❌ Version {target_version} not found in versions.json')
            print(f'📋 Available versions: {[v["version"] for v in all_versions]}')
            sys.exit(1)
    
    print(f'Processing {len(versions)} version(s): {[v["version"] for v in versions]}')
    
    for version_info in versions:
        version = version_info['version']
        link_version = version_info['linkVersion']
        url_path = version_info['url']
        
        print(f'\n🔄 Processing version: {version} (linkVersion: {link_version}, path: {url_path})')
        
        # Resolve tag or branch based on trigger type
        if is_release_trigger:
            # Use tags for release triggers
            ref = resolve_tag_for_version(version, link_version)
            ref_type = 'tag'
        else:
            # Use branches for manual triggers
            ref = resolve_branch_for_version(version, link_version)
            ref_type = 'branch'
        
        if not ref:
            print(f'❌ Skipping version {version} - could not resolve {ref_type}')
            continue
        
        print(f'   Using {ref_type}: {ref}')
        
        # Clone repository once per version
        try:
            clone_repository(ref)
            subprocess.run(['git', '-C', 'kgateway', 'rev-parse', 'HEAD'], check=True)
            print(f'   ✓ Cloned repository')
        except subprocess.CalledProcessError as e:
            print(f'❌ Failed to clone repository for version {version}: {e}')
            continue
        
        # Generate all documentation types for this version
        success_count = 0
        
        try:
            if generate_api_docs(version, link_version, url_path):
                success_count += 1
        except Exception as e:
            print(f'   ⚠ API docs failed: {e}')
        
        try:
            if generate_helm_docs(version, link_version, url_path):
                success_count += 1
        except Exception as e:
            print(f'   ⚠ Helm docs failed: {e}')
        
        try:
            if generate_metrics_docs(version, link_version, url_path):
                success_count += 1
        except Exception as e:
            print(f'   ⚠ Metrics docs failed: {e}')
        
        # Clean up repository after processing this version
        subprocess.run(['rm', '-rf', 'kgateway'], check=True)
        
        print(f'✅ Completed version {version} - generated {success_count}/3 doc types')
    
    print('\n🎉 All versions processed!')


if __name__ == '__main__':
    main()


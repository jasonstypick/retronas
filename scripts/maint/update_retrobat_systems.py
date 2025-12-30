#!/usr/bin/env python3
"""
Update retronas_systems.yml with RetroBat system mappings from CSV.

This script updates the 'src' field in retronas_systems.yml to match the
paths specified in 'local_docs/Retrobat Supported Systems.csv'.
"""

import csv
import sys
import re
from pathlib import Path


def read_csv_mappings(csv_path):
    """Read CSV and extract system mappings."""
    mappings = {}

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header

        for row in reader:
            if len(row) < 4:
                continue

            full_name = row[0]
            system_name = row[1]
            retrobat_path = row[2]  # Not used, but for reference
            retronas_path = row[3]

            # Transform /roms/sega/sega32x → sega/sega32x
            src_path = retronas_path.replace('/roms/', '')

            mappings[system_name] = {
                'full_name': full_name,
                'src': src_path,
                'retrobat_path': retrobat_path
            }

    print(f"✓ Loaded {len(mappings)} systems from CSV")
    return mappings


def update_yaml_file(yaml_path, mappings):
    """Update retronas_systems.yml with new src paths."""

    # Read the entire file
    with open(yaml_path, 'r') as f:
        lines = f.readlines()

    updated_count = 0
    not_found = []

    # Process each line
    for i, line in enumerate(lines):
        # Look for lines with retrobat: "system_name"
        match = re.search(r'retrobat:\s*"([^"]+)"', line)
        if not match:
            continue

        system_name = match.group(1)

        # Skip if not in our CSV
        if system_name not in mappings:
            continue

        # Find the src field on this same line
        src_match = re.search(r'src:\s*"([^"]+)"', line)
        if not src_match:
            print(f"⚠ Warning: Found retrobat:'{system_name}' but no src field on line {i+1}")
            continue

        current_src = src_match.group(1)
        new_src = mappings[system_name]['src']

        # Update if different
        if current_src != new_src:
            # Replace the src value while preserving the rest of the line
            new_line = re.sub(
                r'src:\s*"[^"]+"',
                f'src: "{new_src}"',
                line
            )
            lines[i] = new_line
            updated_count += 1
            print(f"  Updated: {system_name:<20} {current_src} → {new_src}")

    # Write back the file
    with open(yaml_path, 'w') as f:
        f.writelines(lines)

    print(f"\n✓ Updated {updated_count} systems in retronas_systems.yml")

    # Check for systems in CSV but not in YAML
    yaml_content = ''.join(lines)
    for system_name in mappings:
        if f'retrobat: "{system_name}"' not in yaml_content:
            not_found.append(system_name)

    if not_found:
        print(f"\n⚠ Warning: {len(not_found)} systems from CSV not found in YAML:")
        for sys in sorted(not_found):
            print(f"  - {sys}: {mappings[sys]['full_name']}")

    return updated_count, not_found


def main():
    # Paths
    repo_root = Path(__file__).parent.parent.parent
    csv_path = repo_root / "local_docs" / "Retrobat Supported Systems.csv"
    yaml_path = repo_root / "ansible" / "retronas_systems.yml"

    # Verify files exist
    if not csv_path.exists():
        print(f"✗ Error: CSV file not found: {csv_path}")
        sys.exit(1)

    if not yaml_path.exists():
        print(f"✗ Error: YAML file not found: {yaml_path}")
        sys.exit(1)

    print("RetroBat Systems Updater")
    print("=" * 60)
    print(f"CSV:  {csv_path}")
    print(f"YAML: {yaml_path}")
    print()

    # Read CSV mappings
    mappings = read_csv_mappings(csv_path)

    # Create backup
    backup_path = yaml_path.with_suffix('.yml.backup')
    print(f"✓ Creating backup: {backup_path}")
    with open(yaml_path, 'r') as src, open(backup_path, 'w') as dst:
        dst.write(src.read())

    # Update YAML
    print("\nUpdating retronas_systems.yml...")
    updated_count, not_found = update_yaml_file(yaml_path, mappings)

    print("\n" + "=" * 60)
    print(f"Summary: {updated_count} systems updated")

    if not_found:
        print(f"Warning: {len(not_found)} systems need to be added manually")
        return 1

    print("✓ All systems from CSV are present in YAML")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Extract inline CSS from tutorial HTML files and replace with external stylesheet links.

This script:
1. Finds all HTML files in prototype/tutorials/
2. Removes the <style>...</style> block from each
3. Adds <link> tags to the shared CSS files
4. Uses the appropriate theme based on the tutorial folder

Usage:
    python scripts/extract-css.py [--dry-run]
"""

import re
import sys
from pathlib import Path

# Map tutorial folders to theme files
THEME_MAP = {
    '01-gaussian': 'gaussian',
    '02-logistic': 'binomial',
    '03-poisson': 'poisson',
    '04-negbin': 'negbin',
    '05-gamma': 'gamma',
}

# CSS link tags to insert
CSS_LINKS = '''  <!-- Shared CSS -->
  <link rel="stylesheet" href="../../css/base.css">
  <link rel="stylesheet" href="../../css/components.css">
  <link rel="stylesheet" href="../../css/dialogs.css">
  <link rel="stylesheet" href="../../css/progress.css">
  <link rel="stylesheet" href="../../css/themes/{theme}.css">'''

def get_theme_for_path(file_path: Path) -> str:
    """Determine the theme based on the tutorial folder."""
    for folder, theme in THEME_MAP.items():
        if folder in str(file_path):
            return theme
    raise ValueError(f"Unknown tutorial folder for {file_path}")

def process_html_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Process a single HTML file to extract inline CSS.

    Returns True if file was modified, False if skipped.
    """
    content = file_path.read_text()

    # Check if already converted (has CSS links)
    if '../../css/base.css' in content:
        print(f"  SKIP (already converted): {file_path}")
        return False

    # Find and remove <style>...</style> block
    # Match from <style> to </style> including newlines
    style_pattern = r'\s*<style>.*?</style>\s*'

    if not re.search(style_pattern, content, re.DOTALL):
        print(f"  SKIP (no style block): {file_path}")
        return False

    # Get the theme for this file
    theme = get_theme_for_path(file_path)
    css_links = CSS_LINKS.format(theme=theme)

    # Remove the style block
    new_content = re.sub(style_pattern, '\n' + css_links + '\n', content, count=1, flags=re.DOTALL)

    if dry_run:
        print(f"  DRY-RUN: {file_path} (theme: {theme})")
        # Show first few lines of change
        lines = new_content.split('\n')[:20]
        for line in lines:
            print(f"    {line}")
        print("    ...")
    else:
        file_path.write_text(new_content)
        print(f"  CONVERTED: {file_path} (theme: {theme})")

    return True

def main():
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("DRY RUN MODE - no files will be modified\n")

    # Find all HTML files in tutorials
    base_path = Path(__file__).parent.parent / 'prototype' / 'tutorials'
    html_files = sorted(base_path.glob('**/*.html'))

    print(f"Found {len(html_files)} HTML files\n")

    converted = 0
    skipped = 0

    for html_file in html_files:
        if process_html_file(html_file, dry_run):
            converted += 1
        else:
            skipped += 1

    print(f"\nSummary: {converted} converted, {skipped} skipped")

    if dry_run:
        print("\nRun without --dry-run to apply changes")

if __name__ == '__main__':
    main()

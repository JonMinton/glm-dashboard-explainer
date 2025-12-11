#!/usr/bin/env python3
"""
Add navigation links to all tutorial HTML files.

This script:
1. Adds a "← All Tutorials" link in the header of every page
2. On advanced.html (final page), updates navigation to include "Next Tutorial" link

Usage:
    python scripts/build/add-navigation.py [--dry-run]
"""

import re
import sys
from pathlib import Path

# Tutorial order and next tutorial mapping
TUTORIALS = [
    ('01-gaussian', '02-logistic', 'Heart Disease Classification'),
    ('02-logistic', '03-poisson', 'Bike Rental Demand'),
    ('03-poisson', '04-negbin', 'Handling Overdispersion'),
    ('04-negbin', '05-gamma', 'Blood Pressure Prediction'),
    ('05-gamma', None, None),  # Last tutorial
]

def get_next_tutorial(current_folder):
    """Get the next tutorial folder and title."""
    for folder, next_folder, next_title in TUTORIALS:
        if folder == current_folder:
            return next_folder, next_title
    return None, None


def add_header_nav(content: str) -> str:
    """Add 'All Tutorials' link to header if not present."""
    if '../../index.html' in content or 'All Tutorials' in content:
        return content  # Already has navigation

    # Find the header and add navigation link
    # Pattern: <header>\n    <div class="container">\n      <h1>
    header_pattern = r'(<header>\s*<div class="container">)'

    replacement = r'''\1
      <a href="../../index.html" class="back-to-index">&larr; All Tutorials</a>'''

    new_content = re.sub(header_pattern, replacement, content)

    # Add CSS for the link if not present
    if '.back-to-index' not in new_content:
        css_addition = '''
    .back-to-index {
      display: inline-block;
      color: rgba(255,255,255,0.8);
      text-decoration: none;
      font-size: 0.85em;
      margin-bottom: 10px;
      transition: color 0.2s;
    }
    .back-to-index:hover {
      color: white;
    }
'''
        # Insert before closing </style>
        new_content = new_content.replace('</style>', css_addition + '  </style>')

    return new_content


def update_advanced_nav(content: str, next_folder: str, next_title: str) -> str:
    """Update advanced.html navigation with Next Tutorial link."""
    if next_folder is None:
        # Last tutorial - add completion message and link back to index
        # Find the nav-buttons section
        nav_pattern = r'(<div class="nav-buttons">.*?)(Start Tutorial Over.*?</a>)(.*?</div>)'

        completion_nav = '''<a href="../../index.html" class="btn btn-success">
          &#10003; Complete! Back to All Tutorials
        </a>'''

        new_content = re.sub(
            nav_pattern,
            r'\1' + completion_nav + r'\3',
            content,
            flags=re.DOTALL
        )
    else:
        # Has next tutorial - add Next Tutorial link
        nav_pattern = r'(<div class="nav-buttons">.*?)(Start Tutorial Over.*?</a>)(.*?</div>)'

        next_nav = f'''<a href="../{next_folder}/systematic.html" class="btn btn-primary">
          Next: {next_title} &rarr;
        </a>'''

        new_content = re.sub(
            nav_pattern,
            r'\1' + next_nav + r'\3',
            content,
            flags=re.DOTALL
        )

    # Add CSS for success button if not present
    if '.btn-success' not in new_content and next_folder is None:
        css_addition = '''
    .btn-success {
      background: #27ae60;
      color: white;
    }
    .btn-success:hover {
      background: #219a52;
    }
'''
        new_content = new_content.replace('</style>', css_addition + '  </style>')

    return new_content


def process_file(file_path: Path, dry_run: bool = False) -> bool:
    """Process a single HTML file."""
    content = file_path.read_text()
    original_content = content

    # Add header navigation to all pages
    content = add_header_nav(content)

    # For advanced.html, update the bottom navigation
    if file_path.name == 'advanced.html':
        folder_name = file_path.parent.name
        next_folder, next_title = get_next_tutorial(folder_name)
        content = update_advanced_nav(content, next_folder, next_title)

    if content == original_content:
        return False

    if not dry_run:
        file_path.write_text(content)

    return True


def main():
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("DRY RUN MODE - no files will be modified\n")

    # Find all HTML files in tutorials
    base_path = Path(__file__).parent.parent.parent / 'docs' / 'tutorials'
    html_files = sorted(base_path.glob('**/*.html'))

    print(f"Found {len(html_files)} HTML files\n")

    modified = 0
    skipped = 0

    for html_file in html_files:
        if process_file(html_file, dry_run):
            action = "WOULD MODIFY" if dry_run else "MODIFIED"
            print(f"  {action}: {html_file.relative_to(base_path)}")
            modified += 1
        else:
            skipped += 1

    print(f"\nSummary: {modified} modified, {skipped} skipped")

    if dry_run:
        print("\nRun without --dry-run to apply changes")


if __name__ == '__main__':
    main()

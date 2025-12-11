#!/usr/bin/env python3
"""
Add feedback widget script to all tutorial HTML files.

This script adds a <script> tag for feedback.js before the closing </body> tag
in each tutorial HTML file.
"""

import os
from pathlib import Path

# Root of tutorials
TUTORIALS_DIR = Path(__file__).parent.parent.parent / "docs" / "tutorials"
INDEX_FILE = Path(__file__).parent.parent.parent / "docs" / "index.html"

# Script tag to add (path relative from tutorial page location)
SCRIPT_TAG_TUTORIAL = '<script src="../../js/feedback.js"></script>'
SCRIPT_TAG_INDEX = '<script src="js/feedback.js"></script>'

def add_feedback_to_file(filepath: Path, script_tag: str) -> bool:
    """Add feedback script to an HTML file if not already present."""
    content = filepath.read_text()

    # Check if already added
    if 'feedback.js' in content:
        print(f"  Skipping {filepath.name} (already has feedback.js)")
        return False

    # Insert before </body>
    if '</body>' not in content:
        print(f"  Warning: {filepath.name} has no </body> tag")
        return False

    new_content = content.replace(
        '</body>',
        f'\n  {script_tag}\n</body>'
    )

    filepath.write_text(new_content)
    print(f"  Added feedback widget to {filepath.name}")
    return True

def main():
    modified_count = 0

    # Process tutorial pages
    print("Processing tutorial pages...")
    for tutorial_dir in sorted(TUTORIALS_DIR.iterdir()):
        if tutorial_dir.is_dir() and tutorial_dir.name.startswith(('01', '02', '03', '04', '05')):
            print(f"\n{tutorial_dir.name}/")
            for html_file in sorted(tutorial_dir.glob("*.html")):
                if add_feedback_to_file(html_file, SCRIPT_TAG_TUTORIAL):
                    modified_count += 1

    # Process index page
    print(f"\nProcessing index page...")
    if add_feedback_to_file(INDEX_FILE, SCRIPT_TAG_INDEX):
        modified_count += 1

    print(f"\nDone! Modified {modified_count} files.")

if __name__ == "__main__":
    main()

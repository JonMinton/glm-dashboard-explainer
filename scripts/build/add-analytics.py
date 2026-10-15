#!/usr/bin/env python3
"""
Add the Cloudflare Web Analytics beacon to every HTML page in docs/.

The beacon is cookie-free and does not fingerprint visitors; the site is listed
under Web Analytics in the Cloudflare account (stats-board.jonminton.net).
It goes just before </head>. Safe to re-run: pages that already have it are
skipped, so run it again after adding new pages.

Usage:
    python scripts/build/add-analytics.py [--dry-run]
"""

import sys
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent.parent / "docs"

SNIPPET = (
    "<!-- Cloudflare Web Analytics --><script type='module' "
    "src='https://static.cloudflareinsights.com/beacon.min.js' "
    "data-cf-beacon='{\"token\": \"56085bf9b20f49ab9161126ecd94712b\"}'></script>"
    "<!-- End Cloudflare Web Analytics -->"
)


def add_analytics_to_file(filepath: Path, dry_run: bool) -> bool:
    """Insert the beacon before </head> if not already present."""
    content = filepath.read_text()
    if "cloudflareinsights" in content:
        return False
    if "</head>" not in content:
        print(f"  Warning: no </head> in {filepath.relative_to(DOCS_DIR)}")
        return False
    if not dry_run:
        filepath.write_text(content.replace("</head>", SNIPPET + "\n</head>", 1))
    return True


def main():
    dry_run = "--dry-run" in sys.argv
    added = [p for p in sorted(DOCS_DIR.rglob("*.html")) if add_analytics_to_file(p, dry_run)]
    verb = "Would add" if dry_run else "Added"
    print(f"{verb} the analytics beacon to {len(added)} page(s).")


if __name__ == "__main__":
    main()

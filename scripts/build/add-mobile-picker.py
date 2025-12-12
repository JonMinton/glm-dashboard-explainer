#!/usr/bin/env python3
"""
Add mobile tap-to-select support to tutorial systematic.html pages.

This script:
1. Adds CSS for mobile selected state and hint toast
2. Adds script tag for variable-picker.js
3. Replaces setupDropZones function to use initVariablePicker

Usage:
    python scripts/build/add-mobile-picker.py [--dry-run]
"""

import re
import sys
from pathlib import Path

# CSS to add after .variable-card.dimmed
MOBILE_CSS = '''
    /* Mobile: Selected state for tap-to-select */
    .variable-card.selected {
      border-color: #9b59b6;
      background: #f5eef8;
      box-shadow: 0 0 0 3px rgba(155, 89, 182, 0.3);
    }

    /* Mobile hint toast */
    .mobile-picker-hint {
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%) translateY(100px);
      background: #2c3e50;
      color: white;
      padding: 12px 24px;
      border-radius: 8px;
      font-size: 0.9em;
      z-index: 1000;
      opacity: 0;
      transition: all 0.3s ease;
      pointer-events: none;
    }

    .mobile-picker-hint.show {
      transform: translateX(-50%) translateY(0);
      opacity: 1;
    }

    /* Touch device: change cursor and add tap hint */
    .touch-device .variable-card:not(.dimmed) {
      cursor: pointer;
    }

    .touch-device .variable-card .target-badge {
      content: 'Tap me!';
    }

    .touch-device .target-badge::after {
      content: ' (tap)';
    }
'''

# New setupDropZones function
NEW_SETUP_DROP_ZONES = '''    function setupDropZones() {
      // Initialize the variable picker with mobile support
      initVariablePicker({
        variablePool: variablePool,
        predictorZone: predictorZone,
        responseZone: responseZone,

        // Validate if this drop is allowed for the current step
        validateDrop: function(varName, zoneType) {
          const step = steps[currentStep];
          const expectedZone = step.target?.zone;
          const expectedVar = step.target?.variable;

          return varName === expectedVar && zoneType === expectedZone;
        },

        // Handle successful drop
        onDrop: function(varName, zoneType) {
          if (zoneType === 'predictor') {
            selectedPredictors.push(varName);
          } else {
            selectedResponse = varName;
          }

          renderAssigned();

          // Advance step after short delay
          setTimeout(() => {
            currentStep++;
            updateStep();
          }, 400);
        }
      });
    }'''


def add_mobile_support(file_path: Path, dry_run: bool = False) -> bool:
    """Add mobile picker support to a systematic.html file."""
    content = file_path.read_text()
    original = content
    modified = False

    # Check if already has mobile support
    if '.variable-card.selected' in content:
        print(f"  SKIP (already has mobile CSS): {file_path.name}")
        return False

    # 1. Add mobile CSS after .variable-card.dimmed block
    dimmed_pattern = r'(\.variable-card\.dimmed \{[^}]+\})'
    if re.search(dimmed_pattern, content):
        content = re.sub(
            dimmed_pattern,
            r'\1\n' + MOBILE_CSS,
            content
        )
        modified = True

    # 2. Add variable-picker.js script before the main <script> tag
    # Find first <script> (not src=)
    script_pattern = r'(\n  <script>\n    // )'
    if re.search(script_pattern, content) and 'variable-picker.js' not in content:
        content = re.sub(
            script_pattern,
            '\n  <!-- Load variable picker before main script -->\n  <script src="../../js/variable-picker.js"></script>\n\n  <script>\n    // ',
            content
        )
        modified = True

    # 3. Replace setupDropZones function
    # Match from "function setupDropZones()" to the end of the function
    setup_pattern = r'    function setupDropZones\(\) \{[^}]+\[predictorZone, responseZone\]\.forEach\(zone => \{.*?\}\);\s*\}\s*\}'

    if re.search(setup_pattern, content, re.DOTALL):
        content = re.sub(
            setup_pattern,
            NEW_SETUP_DROP_ZONES,
            content,
            flags=re.DOTALL
        )
        modified = True

    if not modified:
        print(f"  SKIP (no changes needed): {file_path.name}")
        return False

    if dry_run:
        print(f"  WOULD MODIFY: {file_path.name}")
    else:
        file_path.write_text(content)
        print(f"  MODIFIED: {file_path.name}")

    return True


def main():
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("DRY RUN MODE - no files will be modified\n")

    # Find systematic.html files (skip tutorial 1 which is already done)
    base_path = Path(__file__).parent.parent.parent / 'docs' / 'tutorials'

    tutorials = ['02-logistic', '03-poisson', '04-negbin', '05-gamma']

    modified = 0
    for tutorial in tutorials:
        file_path = base_path / tutorial / 'systematic.html'
        if file_path.exists():
            if add_mobile_support(file_path, dry_run):
                modified += 1

    print(f"\nSummary: {modified} files modified")

    if dry_run:
        print("\nRun without --dry-run to apply changes")


if __name__ == '__main__':
    main()

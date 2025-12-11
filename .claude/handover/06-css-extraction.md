# Handover: CSS Extraction and Shared Styles

## Task Summary
Extract common CSS patterns from the tutorial HTML files into shared stylesheet(s) to reduce repetition and improve maintainability.

## Background
The tutorial series (5 tutorials × 6 pages each = 30 HTML files) contains significant CSS repetition. Each file has inline `<style>` blocks with similar patterns for:
- Layout and container styles
- Progress bar components
- Option cards with selection states
- Modal dialog overlays
- Buttons and navigation
- Instruction/result panels
- Typography and spacing

## Current State
All tutorials now use consistent modal dialog patterns (`.dialog-overlay` with `.dialog` classes). This standardization was completed in December 2025.

## Proposed Structure

```
prototype/
├── css/
│   ├── base.css           # Reset, typography, container, body
│   ├── components.css     # Reusable: buttons, cards, panels
│   ├── dialogs.css        # Modal overlay and dialog styles
│   ├── progress.css       # Progress bar component
│   └── themes/
│       ├── gaussian.css   # Tutorial 1 theme (green: #27ae60)
│       ├── binomial.css   # Tutorial 2 theme (blue: #3498db)
│       ├── poisson.css    # Tutorial 3 theme (purple: #9b59b6)
│       ├── negbin.css     # Tutorial 4 theme (orange: #d35400)
│       └── gamma.css      # Tutorial 5 theme (red: #c0392b)
```

## CSS Patterns to Extract

### 1. Base Styles (`base.css`)
```css
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, ...; background: #f8f9fa; color: #333; line-height: 1.6; }
.container { max-width: 1000px; margin: 0 auto; padding: 20px; }
```

### 2. Button Components (`components.css`)
```css
.btn { padding: 10px 20px; border-radius: 6px; font-weight: 500; cursor: pointer; ... }
.btn-primary { /* theme-colored */ }
.btn-secondary { background: #ecf0f1; color: #666; }
.btn-success { background: #27ae60; color: white; }
```

### 3. Card Components (`components.css`)
```css
.option-card { background: white; border: 3px solid #dee2e6; border-radius: 12px; ... }
.option-card:hover:not(.dimmed):not(.selected) { /* hover state */ }
.option-card.selected { border-color: #27ae60; background: #d4edda; }
.option-card.wrong { border-color: #e74c3c; background: #f8d7da; animation: shake 0.3s; }
.option-card.semi-valid { border-color: #f39c12; background: #fff3cd; }
.option-card.dimmed { opacity: 0.4; filter: grayscale(40%); pointer-events: none; }
```

### 4. Dialog Overlay (`dialogs.css`)
```css
.dialog-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; ... }
.dialog-overlay.show { display: flex; }
.dialog { background: white; border-radius: 12px; padding: 25px; max-width: 600px; ... }
.dialog.success { border-top: 4px solid #27ae60; }
.dialog.warning { border-top: 4px solid #f39c12; }
.dialog.error { border-top: 4px solid #e74c3c; }
```

### 5. Progress Bar (`progress.css`)
```css
.progress-container { background: white; border-radius: 8px; padding: 20px; ... }
.progress-bar { display: flex; justify-content: space-between; position: relative; }
.step-dot { width: 32px; height: 32px; border-radius: 50%; ... }
.step-dot.completed { /* theme color */ }
.step-dot.current { /* theme color, transform: scale(1.2) */ }
```

### 6. Theme Variables (CSS Custom Properties)
```css
/* themes/gaussian.css */
:root { --theme-primary: #27ae60; --theme-secondary: #219a52; --theme-light: #d4edda; }

/* themes/negbin.css */
:root { --theme-primary: #d35400; --theme-secondary: #ba4a00; --theme-light: #fef5e7; }
```

## Implementation Steps

1. **Create CSS directory structure**
   ```bash
   mkdir -p prototype/css/themes
   ```

2. **Extract base.css** - Common reset and layout

3. **Extract components.css** - Buttons, cards, panels

4. **Extract dialogs.css** - Modal overlay system

5. **Extract progress.css** - Progress bar component

6. **Create theme files** - One per tutorial with CSS custom properties

7. **Update HTML files** - Replace inline `<style>` with `<link>` tags:
   ```html
   <link rel="stylesheet" href="../../css/base.css">
   <link rel="stylesheet" href="../../css/components.css">
   <link rel="stylesheet" href="../../css/dialogs.css">
   <link rel="stylesheet" href="../../css/progress.css">
   <link rel="stylesheet" href="../../css/themes/negbin.css">
   ```

8. **Test each tutorial** - Verify styling unchanged

## Considerations

### CSS Custom Properties Approach
Using CSS variables allows theme colors to be defined once:
```css
header { background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-secondary) 100%); }
.step-dot.completed { background: var(--theme-primary); }
.btn-primary { background: var(--theme-primary); }
```

### File Size vs HTTP Requests
- Separate files = cleaner organisation but more HTTP requests
- Could combine into single `tutorial-styles.css` for production
- CDN caching may make separate files acceptable

### Potential Issues
- Some pages may have unique styles (e.g., code panels with syntax highlighting)
- KaTeX has its own CSS (loaded from CDN)
- Need to maintain relative paths for different tutorial depths

## Related Tasks

### R/ and py/ Validation Code
You mentioned creating `R/` and `py/` folders for validation scripts. This could be combined with the CSS extraction as a general "project organisation" task.

Suggested structure:
```
R/
├── validate-gaussian.R      # Tutorial 1 coefficient validation
├── validate-binomial.R      # Tutorial 2
├── validate-poisson.R       # Tutorial 3
├── validate-negbin.R        # Tutorial 4
└── validate-gamma.R         # Tutorial 5

py/
├── validate_gaussian.py
├── validate_binomial.py
├── validate_poisson.py
├── validate_negbin.py
└── validate_gamma.py
```

## Priority
Medium - This is a refactoring/maintenance task. The tutorials work correctly with inline styles. Extract CSS when:
- Adding more tutorials
- Making global style changes
- Setting up build process

## Estimated Effort
- CSS extraction: ~1-2 hours
- Testing all pages: ~30 minutes
- Documentation updates: ~15 minutes

---

## Notes for Next Session

### Starting Point
Read this file first. The CSS extraction is a self-contained task that doesn't block other work.

### Key Files to Reference
- Any tutorial link.html or distribution.html - they now all use modal dialogs
- [prototype/tutorials/01-gaussian/distribution.html](prototype/tutorials/01-gaussian/distribution.html) - reference implementation

### Testing Approach
Open each tutorial page in browser and:
1. Verify header colours correct for theme
2. Click through option cards, verify modal appears
3. Confirm selection, verify result panel shows
4. Check navigation buttons work

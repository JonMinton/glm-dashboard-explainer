# Git Workflow for Claude Code Sessions

## Quick Start

At the **start** of each Claude Code session, run one of:

```bash
git fresh-feature   # For new features/enhancements
git fresh-bugfix    # For bug fixes/corrections
```

This resets the working branch to match `main`, giving you a clean slate.

## Available Aliases

| Command | Creates Branch | Use For |
|---------|----------------|---------|
| `git fresh-feature` | `feature/claude` | New features, enhancements, new pages |
| `git fresh-bugfix` | `bugfix/claude` | Bug fixes, corrections, typos |

## What the Aliases Do

1. Switch to `main`
2. Pull latest from origin
3. Delete the working branch (if it exists)
4. Create a fresh branch from current `main`

## End of Session

**Keep the work** (merge to main):
```bash
git checkout main
git merge feature/claude  # or bugfix/claude
git push origin main
```

**Discard the work**:
```bash
git checkout main
git branch -D feature/claude  # or bugfix/claude
```

## Comparing Branches

```bash
# What's changed in your working branch?
git diff main --stat

# Detailed diff
git diff main

# Commits in working branch not in main
git log main..HEAD --oneline
```

## Setup (Run Once)

If the aliases aren't available, run this to set them up:

```bash
git config --local alias.fresh-feature '!git checkout main && git pull origin main && git branch -D feature/claude 2>/dev/null; git checkout -b feature/claude'
git config --local alias.fresh-bugfix '!git checkout main && git pull origin main && git branch -D bugfix/claude 2>/dev/null; git checkout -b bugfix/claude'
```

## Notes

- Aliases are stored in `.git/config` (local to this repo, not committed)
- Always start sessions with `fresh-*` to avoid conflicts
- The `claude` suffix identifies these as AI-assisted branches

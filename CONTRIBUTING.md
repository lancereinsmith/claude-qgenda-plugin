# Contributing

## Setup

After cloning the repository, install dependencies and git hooks:

```bash
just deps
just hooks
```

## Git Hooks

Git hooks live in the `git-hooks/` directory and are installed into `.git/hooks/` via `just hooks`.

### pre-commit

Syncs the `version` field from `pyproject.toml` into `.claude-plugin/plugin.json` automatically. This ensures the plugin version stays in sync whenever you commit a version bump — no manual editing of `plugin.json` required.

## Running Tests

```bash
just test
```

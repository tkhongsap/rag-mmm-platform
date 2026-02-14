# Data Management Policy

## Purpose

This project keeps raw and generated data out of Git history to avoid committing
large files and sensitive datasets.

## Git-Tracked vs Ignored Data

Ignored paths are defined in `.gitignore`:

- `data/raw/*`
- `data/processed/*`
- `data/embeddings/*`
- `data/mmm/*`

Tracked exception:

- `data/**/.gitkeep` (directory placeholders only)

## What This Means for `data/raw/`

- Files under `data/raw/` are local-only by default.
- They will not appear in normal `git status` output.
- They cannot be pushed to the remote repository unless ignore rules are changed.

## Validation Commands

Use these commands to confirm ignore behavior:

```bash
git check-ignore -v data/raw/<filename>
git ls-files data/raw
```

Expected result:

- `git check-ignore` reports a matching `.gitignore` rule for the file.
- `git ls-files data/raw` shows only `.gitkeep` entries.

## Recommended Team Workflow

1. Store shared raw datasets in external storage (for example: S3, GCS, or an internal shared drive).
2. Sync required files into local `data/raw/` for development and analysis.
3. Commit only code, configs, and documentation changes to Git.

## If You Intentionally Need Data in Git

If policy changes, choose one of these approaches and update docs/repo config:

- Remove ignore rules and commit files directly (not recommended for large datasets).
- Use Git LFS for large binary/tabular artifacts.

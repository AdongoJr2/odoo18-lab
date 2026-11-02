# Contributing

Thanks for your interest in contributing to Academy Management.

## Getting started

1. Fork the repository and clone your fork.
2. Create a feature branch: `git checkout -b feat/your-feature`.
3. Run the stack locally with `docker compose up -d`.
4. Make your changes, keeping the addon's conventions (see below).

## Conventions

- Python: follow PEP 8; use Odoo's ORM patterns (`_name`, `_description`, fields).
- XML views: keep list/form views consistent with existing files.
- Security: every new model needs an entry in `security/ir.model.access.csv`.
- Manifest: bump `version` for user-visible changes.
- Commit messages: use Conventional Commits (e.g. `feat:`, `fix:`, `docs:`).

## Pull requests

- Keep PRs focused and small.
- Describe what and why; link related issues.
- Ensure the module installs/upgrades cleanly on Odoo 18.

## Code of Conduct

By participating you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

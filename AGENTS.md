# AGENTS.md

Instructions and conventions for AI/code agents working in this repository.

## Ground Rules

- **Targeted Changes**: Prefer small, focused modifications. Avoid unrequested drive-by refactoring.
- **Pre-flight Validation**: Always run linters, type checks, and test coverage before declaring tasks complete:
  - `make python-validate` (`ruff check`, `ruff format`, `mypy`)
  - `make python-test-cov` (`coverage run`, `coverage report`, `generate_coverage_badge.py`)
- **Fix Root Causes**: Fix linter and type errors properly; do not mask symptoms or disable rules without explicit approval.
- **Secret Safety**: Never log, print, or commit passwords, SSH keys, tokens, or client credentials.

## Code Style & Conventions

- **File Handle Naming**: ALWAYS use `fdesc` instead of `f` when naming file object variables in Python (e.g. `with open(...) as fdesc:`).
- **Tooling**:
  - Formatter & Linter: `ruff` (configured in `pyproject.toml`, line length 100).
  - Type Checker: `mypy`.
  - Package Manager: `uv` (`uv sync`, `uv run`).

## Testing & Coverage Badges

- **Test Execution**: Run tests using `uv run python -m src.tests.runner` or `make python-test-cov`.
- **Coverage Badges**: Generate SVG coverage badges using `uv run python scripts/generate_coverage_badge.py`.
  - Avoid unmaintained third-party badge packages (e.g., `coverage-badge`) that depend on deprecated/removed modules like `pkg_resources`.

## Shell & Docker

- **Shell Scripts**: Must include `set -euo pipefail`.
- **Docker**: Container builds should be validated via `make build` or `make docker-build`.

# Validation and boundaries

## Local validation — 2026-10-26 (UTC revalidation)

- Python **3.10.22, 3.11.17 and 3.12.15**: editable install, strict configured `ruff check src/ tests/`, `ruff format --check src/ tests/`, `mypy src/` and `pytest -v` passed on each version.
- **4 tests per Python version**. Dependencies: pytest 9.1.1, Ruff 0.17.2, mypy 2.4.0 and Pydantic 2.14.1 in the recorded local matrix. Dependency ranges may resolve differently later.
- Test processes used isolated HOME/config paths with real socket connections denied. Synthetic responses are not evidence of real backend authentication or permissions.

## Reproduce the strict local checks

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/
pytest -v
```

## What remains unproven

Planner/worker/validator behavior uses local fallback clients in tests. No real LLM provider invocation, model quality evaluation or production orchestration deployment was exercised.

GitHub Actions has been prepared, not run on GitHub by this delivery. It preserves the three-version lint/format/type/test matrix and separately gates Gitleaks 8.30.1 directory/full-fetched-history scans without suppressions or soft-failure operators. External Actions are pinned to verified commit SHAs. The Go-based scanner installation is CI configuration, not a claim that this machine executed that installation. A badge is a link to the workflow status, not proof of a successful remote run.

## Public-source hygiene

Private-history sanitation was performed only in a local working clone, using git-filter-repo with independent full-history backups and private commit maps retained outside this source. There was no push, visibility change or remote repository metadata update. The maintainer must coordinate reviewed history replacement; old remote branches/caches are not erased by a local rewrite. Never commit real customer data, tokens, account identifiers or user-specific filesystem/network paths.

Please report sensitive issues through [GitHub Security Advisories](https://github.com/otixe/agent-harness/security/advisories/new), not public issues.

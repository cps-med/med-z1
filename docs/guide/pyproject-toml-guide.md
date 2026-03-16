# pyproject.toml — A Practical Guide for med-z1

**Audience:** Python developers new to `pyproject.toml`
**Scope:** Background, best practices, and a concrete migration plan for med-z1
**Date:** 2026-03-16

---

## Table of Contents

1. [Why pyproject.toml Exists](#1-why-pyprojecttoml-exists)
2. [The Three Sections Explained](#2-the-three-sections-explained)
3. [Libraries vs. Applications](#3-libraries-vs-applications)
4. [Tool Configuration — The Real Win](#4-tool-configuration--the-real-win)
5. [pyproject.toml vs. Other Config Files](#5-pyprojecttoml-vs-other-config-files)
6. [What Does NOT Belong in pyproject.toml](#6-what-does-not-belong-in-pyprojecttoml)
7. [The requirements.txt Question](#7-the-requirementstxt-question)
8. [med-z1 Migration Plan](#8-med-z1-migration-plan)
9. [Annotated pyproject.toml for med-z1](#9-annotated-pyprojecttoml-for-med-z1)
10. [Migration Steps](#10-migration-steps)
11. [Reference: Common Tool Sections](#11-reference-common-tool-sections)

---

## 1. Why pyproject.toml Exists

Before `pyproject.toml`, Python projects accumulated a pile of configuration files in their root directory:

| File | Purpose |
|------|---------|
| `setup.py` | Package metadata, build instructions |
| `setup.cfg` | Same as setup.py, declarative form |
| `MANIFEST.in` | Which files to include in a source distribution |
| `pytest.ini` | pytest configuration |
| `.flake8` | flake8 linter config |
| `mypy.ini` | mypy type checker config |
| `.isort.cfg` | import sorter config |
| `tox.ini` | test automation config |

This fragmentation was a known problem. Starting in 2016, a series of Python Enhancement Proposals (PEPs) established `pyproject.toml` as the single, standard configuration file for Python projects:

- **PEP 517 (2017)** — Defined a standard build system interface (not tied to setuptools)
- **PEP 518 (2018)** — Introduced `pyproject.toml` as the place to declare build dependencies
- **PEP 621 (2021)** — Standardized the `[project]` metadata table (name, version, dependencies, etc.)

The TOML format was chosen over INI (too limited) and JSON (no comments, verbose) for being human-readable, expressive, and unambiguous.

Today, `pyproject.toml` is the **Python community standard**. All major tools (pytest, ruff, black, mypy, coverage, etc.) read configuration from it. New Python projects should start here rather than creating individual tool config files.

---

## 2. The Three Sections Explained

A `pyproject.toml` file has three conceptually distinct sections. You do not need all three, but understanding what each does is essential.

### 2.1 `[build-system]` — How to Build This Package

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"
```

This tells tools like `pip` and `build` **which tool to use** when building a distributable package (a wheel or sdist). Before PEP 517, this was hardcoded to setuptools. Now you can swap in Hatchling, Flit, Poetry, PDM, etc.

**For an application like med-z1:** You are not building a package for distribution, so this section is technically optional. However, including a minimal `[build-system]` block is considered good practice because it makes your project "pip-installable" in development mode (`pip install -e .`), which is useful for resolving internal imports cleanly.

### 2.2 `[project]` — Package Metadata (PEP 621)

```toml
[project]
name = "med-z1"
version = "0.1.0"
description = "VA longitudinal health record viewer"
requires-python = ">=3.11"
```

This is the standardized metadata that tools and registries (PyPI) understand. It can also declare dependencies:

```toml
[project]
dependencies = [
    "fastapi>=0.123",
    "uvicorn>=0.38",
]
```

**For an application like med-z1:** You will not publish to PyPI, so many `[project]` fields (like `license`, `classifiers`, `urls`) are not needed. However, declaring `name`, `version`, `description`, and `requires-python` is still useful as self-documentation and for `pip install -e .` support.

### 2.3 `[tool.*]` — Tool-Specific Configuration

```toml
[tool.pytest.ini_options]
testpaths = ["scripts"]
cache_dir = ".cache/pytest"

[tool.ruff]
line-length = 100
```

Any tool can claim its own namespace under `[tool.<toolname>]`. This is the most immediately practical section — it is how you eliminate individual config files like `pytest.ini`, `.ruff.toml`, `mypy.ini`, etc.

**This is the primary reason med-z1 should adopt `pyproject.toml`.**

---

## 3. Libraries vs. Applications

This distinction fundamentally affects how you use `pyproject.toml`.

### Libraries

A library is code you publish to PyPI for others to install (`pip install requests`). For libraries:
- The `[project]` section is critical — it defines name, version, and dependencies that PyPI and pip need
- Dependencies in `[project.dependencies]` use **version ranges** (e.g., `>=2.0,<3.0`), not pinned versions
- `requirements.txt` is typically not used

### Applications

An application is a deployed program (like med-z1). For applications:
- The `[project]` section is informational, not functional
- Dependencies should be **pinned exactly** for reproducible deployments
- `requirements.txt` with exact pins (e.g., `fastapi==0.123.9`) remains the correct tool
- `pyproject.toml` is used primarily for `[tool.*]` configuration

**med-z1 is an application.** The right strategy is:
- Keep `requirements.txt` for exact dependency pins
- Use `pyproject.toml` for tool configuration and minimal project metadata
- Do NOT attempt to move `requirements.txt` into `[project.dependencies]`

---

## 4. Tool Configuration — The Real Win

The most immediate benefit of `pyproject.toml` for med-z1 is consolidating all tool configuration into one file. Here is what each supported tool looks like:

### pytest

```toml
[tool.pytest.ini_options]
cache_dir = ".cache/pytest"
testpaths = ["scripts"]
asyncio_mode = "auto"           # for pytest-asyncio
```

Eliminates: `pytest.ini`

### ruff (linter + formatter, replaces flake8/black/isort)

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I"]  # errors, pyflakes, warnings, isort
ignore = ["E501"]               # line-too-long (handled by formatter)

[tool.ruff.lint.per-file-ignores]
"scripts/*" = ["E402"]         # module-level imports not at top
```

Eliminates: `.ruff.toml`, `.flake8`

### black (formatter)

```toml
[tool.black]
line-length = 100
target-version = ["py311"]
```

Eliminates: `pyproject.toml [tool.black]` (already here) or a separate `.black` config

### mypy (type checker)

```toml
[tool.mypy]
python_version = "3.11"
ignore_missing_imports = true
```

Eliminates: `mypy.ini`

### coverage

```toml
[tool.coverage.run]
source = ["app", "ai", "etl", "vista", "ccow"]
omit = ["scripts/*", ".venv/*"]

[tool.coverage.report]
show_missing = true
```

Eliminates: `.coveragerc`

---

## 5. pyproject.toml vs. Other Config Files

| File | Status | Action for med-z1 |
|------|--------|-------------------|
| `pytest.ini` | ✅ Exists | Migrate to `[tool.pytest.ini_options]`, then delete |
| `setup.py` | ❌ Not present | Not needed |
| `setup.cfg` | ❌ Not present | Not needed |
| `tox.ini` | ❌ Not present | Not needed |
| `.flake8` | ❌ Not present | Add ruff config to `pyproject.toml` if/when linting is set up |
| `mypy.ini` | ❌ Not present | Add mypy config to `pyproject.toml` if/when type checking is set up |
| `.coveragerc` | ❌ Not present | Add coverage config to `pyproject.toml` if/when needed |
| `requirements.txt` | ✅ Exists | **Keep as-is** (see Section 7) |

For med-z1, the immediate migration is small: one file (`pytest.ini`) moves into `pyproject.toml`, and the project gains a foundation for future tool configs.

---

## 6. What Does NOT Belong in pyproject.toml

Understanding what to exclude is as important as knowing what to include.

**Do not put in pyproject.toml:**
- Secret keys, passwords, or credentials (use `.env`)
- Environment-specific settings (use `.env` or environment variables)
- Pinned runtime dependencies for an application (keep in `requirements.txt`)
- Runtime application configuration (use `config.py`)
- CI/CD pipeline definitions (use `.github/workflows/`, `Makefile`, etc.)

**A common mistake:** Developers who learn that `[project.dependencies]` can declare dependencies sometimes move everything from `requirements.txt` into it. For a library, this is correct. For an application, it breaks reproducibility because `[project.dependencies]` is designed for version ranges, not exact pins. See Section 7.

---

## 7. The requirements.txt Question

This is the single most frequently misunderstood aspect of `pyproject.toml` for application developers.

### The Two-Layer Model

Modern Python dependency management uses two conceptually separate layers:

| Layer | Purpose | File | Version Style |
|-------|---------|------|---------------|
| **Abstract dependencies** | What your code needs | `[project.dependencies]` or `requirements.in` | Ranges (`>=2.0`) |
| **Locked dependencies** | Exact reproducible environment | `requirements.txt` | Exact pins (`==2.0.1`) |

Libraries publish abstract dependencies. Build tools (pip-compile, uv, Poetry) resolve them into locked files.

### med-z1's Situation

med-z1's `requirements.txt` is already the locked layer — it has exact pins like `fastapi==0.123.9`. This is correct for a deployed application. **Do not change this.**

The question of whether to also add a `[project.dependencies]` abstract layer is an architectural decision that depends on whether you want to adopt a tool like `pip-compile` or `uv` for dependency management. For now, keeping `requirements.txt` as the single source of truth is fine. The CLAUDE.md already documents this approach.

### Practical Rule for med-z1

> Use `pyproject.toml` for tool configuration and project metadata.
> Keep `requirements.txt` for all runtime and development dependencies.

---

## 8. med-z1 Migration Plan

### What Will Change

| Before | After |
|--------|-------|
| `pytest.ini` in project root | Deleted |
| pytest config in `pytest.ini` | Moved to `[tool.pytest.ini_options]` in `pyproject.toml` |
| No `pyproject.toml` | New `pyproject.toml` created at project root |

### What Will NOT Change

- `requirements.txt` — unchanged
- `.env` — unchanged
- `config.py` — unchanged
- `.cache/pytest/` — still generated at same path (gitignored)
- All existing test scripts — unchanged

### Root Directory Before and After

**Before:**
```
med-z1/
  .cache/          ← runtime, gitignored
  .env             ← secrets, gitignored
  .gitignore
  .venv/           ← gitignored
  config.py
  pytest.ini       ← TO BE REMOVED
  requirements.txt
  ...
```

**After:**
```
med-z1/
  .cache/          ← runtime, gitignored (unchanged)
  .env             ← secrets, gitignored (unchanged)
  .gitignore
  .venv/           ← gitignored (unchanged)
  config.py
  pyproject.toml   ← NEW (replaces pytest.ini)
  requirements.txt
  ...
```

Net change: `pytest.ini` removed, `pyproject.toml` added. Same number of files, but `pyproject.toml` is the canonical location that scales as more tools are configured.

---

## 9. Annotated pyproject.toml for med-z1

This is the complete recommended `pyproject.toml` for med-z1 as of 2026-03-16. Each section includes an explanation.

```toml
# =============================================================================
# pyproject.toml — med-z1 project configuration
#
# This file serves two purposes:
#   1. Project metadata (informational, not published to PyPI)
#   2. Tool configuration (pytest, ruff, mypy, coverage, etc.)
#
# Dependencies are NOT managed here. See requirements.txt for all pinned
# runtime and development dependencies.
# =============================================================================

# -----------------------------------------------------------------------------
# Build system
# Minimal declaration enabling `pip install -e .` for clean internal imports.
# med-z1 is not published to PyPI.
# -----------------------------------------------------------------------------
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

# -----------------------------------------------------------------------------
# Project metadata (PEP 621)
# Informational only. Does not replace requirements.txt.
# -----------------------------------------------------------------------------
[project]
name = "med-z1"
version = "0.1.0"
description = "VA next-generation longitudinal health record viewer"
readme = "README.md"
requires-python = ">=3.11"
# Note: no [project.dependencies] — runtime deps live in requirements.txt

# -----------------------------------------------------------------------------
# pytest configuration
# Migrated from pytest.ini (which should be deleted after this file is added).
# -----------------------------------------------------------------------------
[tool.pytest.ini_options]
# Relocate cache directory to keep project root clean
cache_dir = ".cache/pytest"

# Look for tests in scripts/ directory (consolidated approach per CLAUDE.md)
testpaths = ["scripts"]

# Uncomment when pytest-asyncio is actively used in tests:
# asyncio_mode = "auto"

# -----------------------------------------------------------------------------
# ruff — linter and formatter (future, when linting is adopted)
# Combines flake8 + isort + pyupgrade + black-compatible formatting.
# Uncomment and configure when linting is introduced to the project.
# -----------------------------------------------------------------------------
# [tool.ruff]
# line-length = 100
# target-version = "py311"
#
# [tool.ruff.lint]
# select = ["E", "F", "W", "I"]
# ignore = []
#
# [tool.ruff.lint.per-file-ignores]
# "scripts/*" = ["E402"]   # Allow imports not at top of file in scripts

# -----------------------------------------------------------------------------
# mypy — static type checking (future, when type checking is adopted)
# Uncomment and configure when mypy is introduced to the project.
# -----------------------------------------------------------------------------
# [tool.mypy]
# python_version = "3.11"
# ignore_missing_imports = true
# warn_unused_ignores = true

# -----------------------------------------------------------------------------
# coverage — test coverage reporting (future)
# Uncomment when coverage reporting is actively used.
# -----------------------------------------------------------------------------
# [tool.coverage.run]
# source = ["app", "ai", "etl", "vista", "ccow"]
# omit = [
#     "scripts/*",
#     ".venv/*",
#     "mock/*",
# ]
#
# [tool.coverage.report]
# show_missing = true
# skip_covered = false
```

---

## 10. Migration Steps

Follow these steps in order. The migration takes about 5 minutes.

### Step 1: Create pyproject.toml

Create `pyproject.toml` in the project root using the content from Section 9.

### Step 2: Verify pytest still works

```bash
# From project root, with .venv activated
source .venv/bin/activate
pytest --co -q
```

This collects tests without running them. Confirm that pytest discovers tests in `scripts/` and that no errors reference `pytest.ini`.

### Step 3: Delete pytest.ini

```bash
rm pytest.ini
```

### Step 4: Run pytest again to confirm

```bash
pytest --co -q
```

Same result as Step 2. pytest reads `pyproject.toml` automatically when `pytest.ini` is absent.

### Step 5: Verify .gitignore covers .cache/

Confirm that `.cache/` is listed in `.gitignore`. It already is in the current med-z1 `.gitignore`:

```
.cache/
```

No action needed.

### Step 6: Commit

```
Add pyproject.toml, remove pytest.ini

Migrates pytest configuration from pytest.ini into pyproject.toml
[tool.pytest.ini_options]. Establishes pyproject.toml as the single
location for tool configuration, replacing individual config files.
No functional changes to pytest behavior.
```

---

## 11. Reference: Common Tool Sections

Quick-reference for tool sections you may add in the future.

### pytest-asyncio

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"   # or "strict" — auto applies to all async tests
```

### ruff (linting)

```toml
[tool.ruff]
line-length = 100
target-version = "py311"
exclude = [".venv", ".cache", "mock"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP"]
ignore = ["E501"]
```

### black (formatting)

```toml
[tool.black]
line-length = 100
target-version = ["py311"]
exclude = '''
/(
    \.venv
  | \.cache
  | mock
)/
'''
```

### mypy (type checking)

```toml
[tool.mypy]
python_version = "3.11"
ignore_missing_imports = true
exclude = ["mock/", "scripts/"]
```

### coverage

```toml
[tool.coverage.run]
branch = true
source = ["app", "ai", "etl", "vista", "ccow"]
omit = [".venv/*", "scripts/*", "mock/*"]

[tool.coverage.report]
show_missing = true
precision = 2
```

---

## Summary

| Question | Answer |
|----------|--------|
| What is `pyproject.toml`? | The Python standard for project and tool configuration (PEP 517/518/621) |
| Why use it? | Consolidates multiple config files into one; all major tools support it |
| Should med-z1 use it? | Yes — start with pytest config, add others as tools are adopted |
| Does it replace `requirements.txt`? | No — keep `requirements.txt` for pinned dependencies |
| How much work is the migration? | ~5 minutes for the immediate pytest migration |
| What's the long-term value? | One place to look for all tool configuration as the project grows |

# Contributing to rail-arf

This is the Rezolve fork-of-fork of the Glite Autonomous Research Framework. Most of this document
mirrors upstream `GliteTech/glite-arf`'s `CONTRIBUTING.md`; the Rezolve-specific section below
covers fork lifecycle (upstream sync, Rezolve-internal contributions, downstream forks).

## Rezolve fork lifecycle

`rail-arf` tracks `GliteTech/glite-arf` as the `upstream` git remote. Rezolve research projects
fork `rail-arf` (not `glite-arf`) so they inherit Rezolve's framework additions and lessons by
default.

### Pulling upstream framework improvements

When Glite ships a framework update we want, rebase onto upstream:

```bash
git fetch upstream
git rebase upstream/main
```

Resolve any conflicts in `arf/` (Rezolve additions: Azure ML provisioner, bootstrap/significance
library, warmup-protocol package, customised CLAUDE.md, extended setup-project skill, the two
extra verificators). Project-specific files under `project/`, `meta/`, and `tasks/` are unaffected.

Push the rebased branch and open a PR titled `Sync upstream <upstream-commit-sha>` so reviewers can
diff the rebase against `origin/main` before fast-forwarding.

### Adding Rezolve-specific framework code

Modifications to `arf/`, `meta/` (generic types only), `LESSONS.md`, or the root `CLAUDE.md` go on
the `main` branch directly (no `tasks/tXXXX_*` folder — those are reserved for project work, per
key rule 0). Open a PR if the change is non-trivial. Always increment the version of any skill or
specification you change (plain integer, +1 per change — see
`arf/styleguide/agent_instructions_styleguide.md`).

### Adding a lesson

When a Rezolve research project produces a generalizable lesson, follow the procedure at the bottom
of `LESSONS.md`: add a `## Lesson N` entry with *what went wrong*, *why*, *mitigation*, and wire
the mitigation as a default in the relevant skill, asset spec, or verificator. A lesson without a
corresponding code default is a complaint, not a lesson.

### Spawning a new Rezolve research project

```bash
gh repo fork rezolved/rail-arf --org rezolved --fork-name rail-arf-<project-slug>
```

Then run `/setup-project` in Claude Code to populate `project/description.md`, `project/budget.json`,
and the project's `meta/` entries.

## Upstream-style contributions

Thank you for your interest in contributing to the underlying Glite Autonomous Research Framework
(Glite ARF). This document describes what kinds of contributions are welcome, how to set up a
development environment, and the process for proposing changes.

Glite ARF is maintained by [Glite Tech Ltd](https://glite.ai). We use it internally to run research
on adaptive assessment and learner modeling, and we publish it because the same structure helps any
team running AI-driven research at scale.

## Scope

Glite ARF is a framework, not an application. It provides:

* Skills that drive each task stage (research, planning, implementation, analysis, reporting)
* Specifications that every artifact must follow
* Verificator scripts that enforce structure before commit
* Aggregator scripts that collect data across tasks with a corrections overlay
* Mandatory logging and frozen-task immutability

Contributions that fit the framework scope are welcome. Contributions that bend the framework into a
generic task runner, a web app, or a replacement for existing tooling (Git, Make, CI) are out of
scope and will be declined.

### In scope

* New verificators, aggregators, skills, specifications, and materializers
* Bug fixes, test coverage, and performance improvements for existing framework code
* Documentation improvements (tutorials, how-to guides, reference docs)
* New generic asset types or task types in `meta/`
* New style-guide rules backed by concrete examples

### Out of scope

* Project-specific content (categories, metrics, tasks) — these belong in your fork
* Integrations with specific experiment trackers or cloud providers unless they are generic and
  pluggable
* Breaking changes that cannot be gated behind a spec version bump

## Development setup

1. **Fork the repository** on GitHub and clone your fork.

2. **Install dependencies** — the project uses [uv](https://docs.astral.sh/uv/):

   ```bash
   uv sync
   ```

3. **Install pre-commit hooks**:

   ```bash
   uv run pre-commit install
   ```

4. **Validate the environment**:

   ```bash
   python3 doctor.py
   ```

   Fix any failures before continuing.

## Quality checks

Before opening a pull request, run every check locally:

```bash
uv run ruff check --fix .
uv run ruff format .
uv run mypy .
uv run pytest
```

The same checks run in CI on every pull request. Pull requests with failing checks will not be
merged.

## Markdown files

Edited markdown files must be normalized with Flowmark at width 100:

```bash
uv run flowmark --inplace --nobackup path/to/file.md
```

See `arf/styleguide/markdown_styleguide.md` for the full rules.

## Style guides

All code and documentation must follow the project style guides:

* `arf/styleguide/python_styleguide.md` — Python code
* `arf/styleguide/markdown_styleguide.md` — Markdown files
* `arf/styleguide/agent_instructions_styleguide.md` — skills and agent instructions

The style guides are enforced by `arf/skills/check-python-style`, `arf/skills/check-markdown-style`,
and `arf/skills/check-skill`. Run the relevant checker skill on any file you touch.

## Proposing a new specification, verificator, aggregator, or skill

1. **Open an issue first** describing the proposal and the problem it solves. This saves wasted work
   on proposals that do not fit the framework scope.
2. **Write the specification first**, not the implementation. Place it under `arf/specifications/`
   or `meta/asset_types/<name>/specification.md` with a `**Version**: 1` header.
3. **Write tests before the implementation.** See `arf/tests/` for the pattern. Tests for new
   verificators and aggregators should be written from the specification, not from the
   implementation.
4. **Implement the verificator or aggregator** under `arf/scripts/verificators/` or
   `arf/scripts/aggregators/`.
5. **Add a skill** under `arf/skills/<skill-slug>/SKILL.md` if the change introduces a new workflow.
   Symlink it into `.claude/skills/<skill-slug>` and `.codex/skills/<skill-slug>` using relative
   paths.
6. **Update `arf/docs/reference/`** so the new component is discoverable.
7. **Run the check skills** on every file you added or edited.

## Versioning and releases

Specifications and skills carry plain-integer version numbers (`**Version**: N`). Increment by one
for every backwards-incompatible change. Files produced under a spec carry a matching `spec_version`
string field.

Framework releases are tagged in the repository once a coherent set of changes is ready. There is no
fixed release cadence at the v0 stage. `CHANGELOG.md` will track release notes once the first tagged
version is cut.

## Security issues

Do not file security issues publicly. Email `info@glite.ai` with a private report. We will
acknowledge receipt within five business days.

## License

By contributing you agree that your contributions are licensed under the Apache License 2.0, the
same license as the rest of the project. See `LICENSE` for details.

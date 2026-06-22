"""PostToolUse hook: remind to run flowmark on edited Markdown files.

Replaces the /check-markdown-style skill invocation. Returns a short
one-line reminder instead of loading the 7 KB markdown styleguide.
"""

import json
import shlex
import sys
from pathlib import Path


def main() -> None:
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_input = hook_input.get("tool_input", {})
    if not isinstance(tool_input, dict):
        return

    file_path = tool_input.get("file_path", "")
    if not file_path or not file_path.endswith(".md"):
        return

    # Resolve relative paths against the hook's reported cwd.
    cwd = hook_input.get("cwd", "")
    path = Path(cwd) / file_path if cwd else Path(file_path)
    if not path.exists():
        return

    # Prefer a repo-relative path so the reminder injected into the next agent
    # turn stays short; fall back to the absolute path when cwd is unknown.
    display_path = str(path.resolve())
    if cwd:
        try:
            display_path = str(path.resolve().relative_to(Path(cwd).resolve()))
        except ValueError:
            display_path = str(path.resolve())
    quoted_path = shlex.quote(display_path)
    print(f"Run flowmark when done: uv run flowmark --inplace --nobackup {quoted_path}")


if __name__ == "__main__":
    main()

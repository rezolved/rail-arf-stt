"""PostToolUse hook: remind to run flowmark on edited Markdown files.

Replaces the /check-markdown-style skill invocation. Returns a short
one-line reminder instead of loading the 7 KB markdown styleguide.
"""
import json
import sys
from pathlib import Path


def main() -> None:
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_input = hook_input.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path or not file_path.endswith(".md"):
        return

    if not Path(file_path).exists():
        return

    print(f"Run flowmark when done: uv run flowmark --inplace --nobackup {file_path}")


if __name__ == "__main__":
    main()

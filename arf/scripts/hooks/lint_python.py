"""PostToolUse hook: run ruff + mypy on edited Python files.

Replaces the /check-python-style skill invocation. Reads the file path
from the Claude Code hook stdin payload, runs ruff and mypy, and prints
any violations. No styleguide file is loaded into context.
"""
import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_input = hook_input.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path or not file_path.endswith(".py"):
        return

    path = Path(file_path)
    if not path.exists():
        return

    results: list[str] = []

    ruff = subprocess.run(
        ["uv", "run", "ruff", "check", file_path, "--output-format=concise"],
        capture_output=True,
        text=True,
    )
    ruff_out = (ruff.stdout + ruff.stderr).strip()
    if ruff_out or ruff.returncode not in (0, 1):
        results.append("**ruff**:")
        results.extend(ruff_out.splitlines()[:20])

    mypy = subprocess.run(
        ["uv", "run", "mypy", file_path, "--no-error-summary"],
        capture_output=True,
        text=True,
    )
    mypy_out = (mypy.stdout + mypy.stderr).strip()
    if mypy_out:
        lines = [line for line in mypy_out.splitlines() if "error:" in line][:10]
        if lines:
            results.append("**mypy**:")
            results.extend(lines)

    if results:
        print("\n".join(results))
    # No output = no violations = no context added


if __name__ == "__main__":
    main()

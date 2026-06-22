"""PostToolUse hook: run ruff + mypy on edited Python files.

Replaces the /check-python-style skill invocation. Reads the file path
from the Claude Code hook stdin payload, runs ruff and mypy, and prints
any violations. No styleguide file is loaded into context.
"""

import json
import re
import subprocess
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
    if not file_path or not file_path.endswith(".py"):
        return

    # Resolve relative paths against the hook's reported cwd.
    cwd = hook_input.get("cwd", "")
    path = Path(cwd) / file_path if cwd else Path(file_path)
    if not path.exists():
        return

    abs_path = str(path.resolve())
    results: list[str] = []

    try:
        ruff = subprocess.run(
            ["uv", "run", "ruff", "check", abs_path, "--output-format=concise"],
            capture_output=True,
            text=True,
        )
        ruff_out = (ruff.stdout + ruff.stderr).strip()
        if ruff_out or ruff.returncode not in (0, 1):
            results.append("**ruff**:")
            if ruff_out:
                results.extend(ruff_out.splitlines()[:20])
            else:
                results.append(f"(ruff exited with code {ruff.returncode}, no output)")
    except Exception as e:
        results.append(f"**ruff**: could not run ({e})")

    # Use package-based mypy for task code to avoid duplicate-module-name errors
    # across task folders (per execute-task Critical Rule: uv run mypy -p tasks.$TASK_ID.code).
    task_match = re.search(r"/tasks/([^/]+)/code/", abs_path)
    if task_match:
        task_id = task_match.group(1)
        mypy_cmd = ["uv", "run", "mypy", "-p", f"tasks.{task_id}.code", "--no-error-summary"]
    else:
        mypy_cmd = ["uv", "run", "mypy", abs_path, "--no-error-summary"]

    try:
        mypy = subprocess.run(
            mypy_cmd,
            capture_output=True,
            text=True,
        )
        mypy_out = (mypy.stdout + mypy.stderr).strip()
        if mypy_out:
            lines = [line for line in mypy_out.splitlines() if "error:" in line][:10]
            if lines:
                results.append("**mypy**:")
                results.extend(lines)
            elif mypy.returncode != 0:
                # Surface non-"error:" mypy failures (config issues, crashes).
                results.append("**mypy**:")
                results.extend(mypy_out.splitlines()[:5])
    except Exception as e:
        results.append(f"**mypy**: could not run ({e})")

    if results:
        print("\n".join(results))
    # No output = no violations = no context added


if __name__ == "__main__":
    main()

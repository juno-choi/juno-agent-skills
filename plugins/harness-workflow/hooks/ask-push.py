#!/usr/bin/env python3
"""PreToolUse hook: when a Bash command invokes `git push`, return an `ask`
decision so Claude Code shows a permission prompt with the current branch name
and the push target. This does NOT block — it requires explicit human approval.
"""
import json
import re
import subprocess
import sys


PUSH_PATTERN = re.compile(
    r"""(?:^|[\s;&|()"'`])
        git\s+push
        (?:\s|$|[;&|()"'`])
    """,
    re.VERBOSE,
)


def current_branch(cwd):
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode == 0:
            return result.stdout.strip() or "(unknown)"
    except Exception:
        pass
    return "(unknown)"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if payload.get("tool_name") != "Bash":
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    command = tool_input.get("command", "") or ""

    if not PUSH_PATTERN.search(command):
        return 0

    cwd = payload.get("cwd") or tool_input.get("cwd")
    branch = current_branch(cwd)

    is_force = bool(re.search(r"--force(?:-with-lease)?|(?<!\w)-f(?!\w)", command))
    danger = " ⚠️ force push 옵션 감지됨!" if is_force else ""

    reason = (
        f"`{branch}` 브랜치를 원격에 푸시합니다.{danger}\n"
        f"실행할 명령: `{command}`\n"
        f"정말 푸시할까요?"
    )

    decision = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(decision, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

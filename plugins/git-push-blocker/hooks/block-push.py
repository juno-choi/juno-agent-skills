#!/usr/bin/env python3
"""PreToolUse hook: deny any Bash command that invokes `git push`,
including wrapped variants like `bash -c "git push"`, `cd repo && git push`,
or `(cd x; git push)`.
"""
import json
import re
import sys


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if payload.get("tool_name") != "Bash":
        return 0

    command = payload.get("tool_input", {}).get("command", "") or ""

    pattern = re.compile(
        r"""(?:^|[\s;&|()"'`])   # boundary: start, whitespace, or shell metachar
            git\s+push           # the actual command
            (?:\s|$|[;&|()"'`])  # boundary on the right side
        """,
        re.VERBOSE,
    )

    if pattern.search(command):
        decision = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "git push는 차단되어 있습니다. "
                    "원격 반영은 사용자가 직접 터미널에서 실행해주세요."
                ),
            }
        }
        print(json.dumps(decision, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""PreToolUse hook: when a Bash command invokes `git commit`, return an `ask`
decision so Claude Code shows a permission prompt to review the commit before it
runs. This does NOT block — it requires explicit human approval. Any Bash command
that is not a `git commit` passes through untouched.
"""
import json
import re
import sys


COMMIT_PATTERN = re.compile(
    r"""(?:^|[\s;&|()"'`])
        git\s+commit
        (?:\s|$|[;&|()"'`])
    """,
    re.VERBOSE,
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if payload.get("tool_name") != "Bash":
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    command = tool_input.get("command", "") or ""

    if not COMMIT_PATTERN.search(command):
        return 0

    reason = (
        "커밋 내용을 확인해주세요. "
        "커밋 메시지와 변경 사항이 의도한 대로 작성되었는지 검토해주세요.\n"
        f"실행할 명령: `{command}`"
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

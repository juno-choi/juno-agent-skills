# juno agent skills

- 개인적으로 사용할 agent, skills 정리

이 저장소는 Claude Code **plugin marketplace** 형태로 구성되어 있습니다.
(`.claude-plugin/marketplace.json` + `plugins/*`)

## 포함된 플러그인

| Plugin | 설명 |
| --- | --- |
| `harness-workflow` | 프로젝트 로컬 `workspace/` 기반 plan → TDD(`test-coder`/`coder`/`verifier`) → close 워크플로우 + `git commit` / `git push` 안전 hook 번들 |

> `harness-workflow` 의 refactor 단계는 `code-simplifier:code-simplifier` skill 을 별도로 가정합니다. (별도 plugin 설치 필요)
>
> `git commit` / `git push` 실행 시 PreToolUse hook 이 권한 프롬프트(`ask`) 를 띄웁니다. push hook 은 현재 브랜치명과 force 옵션 여부도 함께 보여줍니다.

## 설치 방법

Claude Code 세션 안에서 슬래시 명령으로 마켓플레이스를 등록한 뒤 플러그인을 설치합니다.

### 1) 마켓플레이스 추가

**원격(GitHub)으로 추가:**

```
/plugin marketplace add juno-choi/juno-agent-skills
```

**로컬 경로로 추가** (저장소를 직접 수정하며 테스트할 때 유용):

```
/plugin marketplace add /path/to/juno-agent-skills
```

### 2) 플러그인 설치

```
/plugin install harness-workflow@juno-agent-skills
```

또는 인터랙티브 메뉴를 사용:

```
/plugin
```

→ `Browse marketplaces` → `juno-agent-skills` → 원하는 플러그인 선택 → Install.

### 3) 설치 확인

```
/plugin marketplace list
/plugin
```

설치된 플러그인 목록에 표시되면 정상입니다.

## 업데이트 / 삭제

```
/plugin marketplace update juno-agent-skills   # 마켓플레이스 최신화
/plugin uninstall harness-workflow             # 플러그인 제거
/plugin marketplace remove juno-agent-skills   # 마켓플레이스 등록 해제
```

## 참고

- 로컬 경로와 GitHub 경로를 동시에 등록하면 marketplace name(`juno-agent-skills`)이 충돌하므로 한 가지 방식만 사용하세요.
- hook 동작 디버깅이 필요하면 `claude --debug` 로그에서 `PreToolUse` 이벤트를 확인할 수 있습니다.

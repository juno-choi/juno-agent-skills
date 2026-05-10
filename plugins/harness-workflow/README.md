# harness-workflow

프로젝트 로컬 `workspace/` 폴더 기반의 AI 개발 하네스 plugin.
**plan → TDD(test-coder/coder/verifier) → close** 워크플로우를 강제한다.

## 구성요소

| 종류 | 이름 | 역할 |
|---|---|---|
| Skill | `/plan` | 요구사항 → `workspace/` 초기화 + `plan.md` 작성 |
| Skill | `/work` | plan.md 다음 Task 1개를 TDD 사이클(red→green→verify→refactor)로 자동 진행 + test/code/refactor 3커밋 |
| Skill | `/close` | 작업 완료 → `archive/` 이동 + brain 아카이빙 안내 |
| Agent | `test-coder` | Red 단계 — 실패 테스트 작성 |
| Agent | `coder` | Green 단계 — 기능 구현 |
| Agent | `verifier` | 검증 — read-only 리포트 |
| Hook | `git commit` PreToolUse | 커밋 직전 권한 프롬프트(`ask`) 를 띄워 메시지/변경 사항 검토 강제 |
| Hook | `git push` PreToolUse | 푸시 직전 현재 브랜치명 + force 옵션 여부를 보여주며 권한 프롬프트(`ask`) 를 띄움 |

> refactor 단계의 `code-simplifier:code-simplifier` skill 은 본 plugin에 포함되지 않는다 (별도 plugin 설치 필요).

## 전체 작동 흐름

```
사용자: 요구사항 문서 전달 + /plan 호출
  ↓
[/plan]  workspace/ 초기화 → plan.md + handoff.md 생성
  ↓
──── /work 1회 호출 = Task 1개 ────
[test-coder]                  실패 테스트 + 스켈레톤
  ↓ 자동 빌드 (redirect+tail) → Red 자동 판정
git commit  test: {commit-name} [phase-N] [task-N] {설명}
  ↓
[coder]                       최소 구현
  ↓ 자동 빌드 → Green 자동 판정 (실패 시 멈춤)
git commit  feat: {commit-name} [phase-N] [task-N] {설명}
  ↓
[verifier]                    read-only 검증 리포트
  ↓ PASS 판정 (FAIL 시 멈춤)
[code-simplifier]             refactor (별도 plugin, 미설치 시 스킵)
  ↓ 자동 빌드 → Green 유지 확인
git commit  refactor: {commit-name} [phase-N] [task-N] {설명}
  ↓
plan.md Task 체크 + handoff.md commit log 갱신
────────────────────────
  ↓ 모든 Task 완료
[/close]  workspace/archive/{N}_{slug}/ 로 이동 + brain 아카이빙 안내
```

빌드는 `workspace/.last_build.log` 로 redirect 하고 마지막 25줄만 context 에 적재한다 (context 오염 최소화).
`git commit` 은 PreToolUse `ask` hook 으로 매번 사용자 승인을 받는다.

## 설치

상위 README 참고:
```
/plugin marketplace add /path/to/juno-agent-skills
/plugin install harness-workflow@juno-agent-skills
```

## 적용 가이드 — 대상 프로젝트의 CLAUDE.md

이 plugin이 의도대로 동작하려면 **plugin을 사용할 프로젝트의 루트 `CLAUDE.md`** 에
다음 내용을 포함하는 것을 권장한다. (skill/agent 본문은 호출됐을 때만 컨텍스트에
들어오므로, "항상 적용되어야 할 규칙"은 CLAUDE.md 에 적어야 한다.)

### 왜 CLAUDE.md 인가

- **CLAUDE.md** — 모든 턴에 항상 로드 → 자동 진입 규칙, 가드레일 적합
- **skill/agent** — 호출됐을 때만 → 절차적 작업 적합
- **hook** — 이벤트 자동 발화 → 강제 차단/주입 적합 (강한 강제력)

### 권장 CLAUDE.md 템플릿

다음 블록을 프로젝트의 `CLAUDE.md` 에 추가한다. `← 프로젝트마다 수정` 이 붙은
줄은 실제 값으로 바꿔야 한다.

```markdown
# Harness Workflow 연동

## Workspace 진입 규칙
- 세션 시작 시 `workspace/handoff.md`, `workspace/plan.md` 가 존재하면 먼저 읽고
  현재 진행 상황을 1~2줄로 보고한다.
- 새 요구사항(요구사항 문서/링크)이 들어오면 `/plan` 부터 시작한다.
  plan.md 없이 바로 코드 작성 금지.

## TDD 사이클 진행
- Task 단위 진행은 `/work` 스킬을 호출한다. (`/work` 1회 = Task 1개 완료)
- `/work` 가 다음 순서를 자동 강제: test-coder → 빌드 → test 커밋 → coder → 빌드 → code 커밋 → verifier → (code-simplifier) → refactor 커밋.
- 사용자가 명시적으로 건너뛰지 않는 한 위 순서를 임의 변경하지 않는다.
- code-simplifier:code-simplifier 가 미설치면 refactor 단계는 스킵된다 (별도 plugin).

## 빌드 / 테스트 정책
- Claude 는 build/test 명령을 raw 로 직접 실행하지 않는다 (context 오염 방지).
- `/work` 는 다음 패턴으로만 빌드를 실행한다: `<build-cmd> > workspace/.last_build.log 2>&1; tail -25 workspace/.last_build.log`
  - 전체 로그는 파일로 보존, AI context 에는 마지막 25줄만 적재.
  - 실패 디버그 시 사용자가 `workspace/.last_build.log` 직접 열람.
- 본 프로젝트 빌드 명령: `./gradlew test`   ← 프로젝트마다 수정 (`/work` 가 이 라인을 grep 한다)

## 커밋 컨벤션
- 형식: `feat: {commit-name} [phase-N] [task-N] {설명}`
  - commit-name 은 `workspace/plan.md` 의 `commit name` 필드 사용
- 커밋 직후 `workspace/handoff.md` 의 `commit log` 섹션 업데이트
- `git push` 는 사용자가 직접 수행 (자동 push 금지)

## workspace/ 정책
- `workspace/` 는 `.gitignore` 대상.
- `workspace/archive/` 안의 파일은 불변 — 수정/삭제 금지.
- 세션 종료 시 `workspace/handoff.md` 의 `마지막 수정일` 과 미결 질문을 갱신한다.

## 프로젝트 컨벤션 (verifier 기준)
- 언어/프레임워크: Kotlin + Spring Boot + JPA   ← 프로젝트마다 수정
- 패키지 구조: {도메인}/{layer}                  ← 예시, 프로젝트마다 수정
- 테스트 위치: src/test/kotlin/...               ← 프로젝트마다 수정
- 트랜잭션 경계: Service 계층에서만 @Transactional
- (그 외 프로젝트별 가드레일을 추가)
```

### CLAUDE.md 외 적용 메커니즘

CLAUDE.md 만으로는 모델 준수에 의존하므로 강한 강제가 어렵다. 다음과 같이 메커니즘을 나누는 것을 권장:

| 규칙 | 적합 메커니즘 | 비고 |
|---|---|---|
| 세션 시작 시 handoff/plan 자동 인지 | CLAUDE.md (또는 SessionStart hook) | hook 이면 강제력 ↑ |
| build/test 직접 실행 금지 | **PreToolUse hook 권장** | 본 plugin `hooks/` 패턴 참고 |
| 커밋 메시지 형식 검증 | **PreToolUse hook 권장** | 본 plugin 의 `git commit` ask hook 참고 |
| 푸시 전 브랜치 확인 | **PreToolUse hook (포함됨)** | `hooks/ask-push.py` |
| Agent 호출 순서 | CLAUDE.md | 절차 강제는 어려움 — 모델 신뢰 |
| workspace/archive 불변 | CLAUDE.md (또는 PreToolUse hook) | 폴더 매칭 hook 으로 강화 가능 |

> 본 plugin 은 skill + agent + git commit/push PreToolUse hook 묶음을 함께 제공한다.
> 추가 강제(예: build/test 차단, workspace 불변)가 필요하면 `hooks/` 에 항목을 더 추가하면 된다.

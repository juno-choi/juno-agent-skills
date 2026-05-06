# harness-workflow

프로젝트 로컬 `workspace/` 폴더 기반의 AI 개발 하네스 plugin.
**plan → TDD(test-coder/coder/verifier) → close** 워크플로우를 강제한다.

## 구성요소

| 종류 | 이름 | 역할 |
|---|---|---|
| Skill | `/plan` | 요구사항 → `workspace/` 초기화 + `plan.md` 작성 |
| Skill | `/close` | 작업 완료 → `archive/` 이동 + brain 아카이빙 안내 |
| Agent | `test-coder` | Red 단계 — 실패 테스트 작성 |
| Agent | `coder` | Green 단계 — 기능 구현 |
| Agent | `verifier` | 검증 — read-only 리포트 |

> refactor 단계의 `code-simplifier:code-simplifier` skill 은 본 plugin에 포함되지 않는다 (별도 plugin 설치 필요).

## 전체 작동 흐름

```
사용자: 요구사항 문서 전달 + /plan 호출
  ↓
[/plan]  workspace/ 초기화 → plan.md + handoff.md 생성
  ↓
──── Task 단위 반복 ────
[test-coder]                  실패 테스트 + 스켈레톤
  ↓ 사용자 빌드 → Red 확인
[coder]                       최소 구현 + plan.md Task 체크
  ↓ 사용자 빌드 → Green 확인
[verifier]                    read-only 검증 리포트
  ↓ PASS 판정
[code-simplifier]             refactor (별도 plugin)
  ↓ 사용자 빌드 → Green 유지 확인
커밋:  feat: {commit-name} [phase-N] [task-N] {설명}
       handoff.md 업데이트
────────────────────────
  ↓ 모든 Task 완료
[/close]  workspace/archive/{N}_{slug}/ 로 이동 + brain 아카이빙 안내
```

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

## Agent 호출 순서 (TDD 사이클)
Task 단위 진행은 다음 순서를 강제한다. 사용자가 명시적으로 건너뛰지 않는 한 임의 변경 금지.
1. test-coder  (Red 단계 — 실패 테스트 + 스켈레톤)
2. 사용자 빌드 → Red 확인
3. coder       (Green 단계 — 최소 구현 + plan.md Task 체크)
4. 사용자 빌드 → Green 확인
5. verifier    (read-only 검증 리포트)
6. code-simplifier:code-simplifier (refactor) — 별도 plugin

## 빌드 / 테스트 정책
- Claude 는 build/test 명령을 직접 실행하지 않는다 (context 오염 방지).
- 빌드/테스트 결과는 사용자가 텍스트로 전달하며, 그 결과만 보고 다음 단계 판단.
- 본 프로젝트 빌드 명령: `./gradlew test`   ← 프로젝트마다 수정

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
| build/test 직접 실행 금지 | **PreToolUse hook 권장** | `git-push-blocker` 와 동일 패턴 |
| 커밋 메시지 형식 검증 | **PreToolUse hook 권장** | `git-commit-guard` 와 동일 패턴 |
| Agent 호출 순서 | CLAUDE.md | 절차 강제는 어려움 — 모델 신뢰 |
| workspace/archive 불변 | CLAUDE.md (또는 PreToolUse hook) | 폴더 매칭 hook 으로 강화 가능 |

> 본 plugin은 현재 skill + agent 만 포함한다. 강제 차단이 필요하면 hook 을 추가
> plugin 으로 분리하거나 본 plugin 에 hook 디렉토리를 추가하는 방향을 검토할 것.

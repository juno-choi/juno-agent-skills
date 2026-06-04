---
name: plan
description: "요구사항 문서(링크 또는 파일 경로)를 기반으로 workspace/ 폴더를 초기화하고 plan.md(Phase·Task 분해) + handoff.md 를 작성하는 스킬. 이후 /work 가 이 plan.md 를 읽어 TDD 사이클을 진행하므로, 작업을 시작하기 전 계획 수립 단계에서 반드시 사용한다.
  '플랜 만들어', 'plan 작성', '작업 계획 세워', '요구사항 보고 plan 짜줘', '요구사항 정리해서 계획', '어떻게 진행할지 계획', 'phase 나눠줘', 'task 로 쪼개줘', '작업 단계 설계', 'workspace 초기화', '이 문서로 작업 시작하자' 등 요구사항을 받아 작업 계획을 세우려는 모든 표현에 사용한다."
---

# /plan — workspace 초기화 + plan.md 작성

요구사항 문서를 읽고 `{project}/workspace/` 를 초기화한 뒤 `plan.md` 와 `handoff.md` 를 생성한다.

## 전제 조건

- 현재 작업 디렉토리가 대상 프로젝트 루트
- 사용자가 요구사항 문서 경로 또는 링크를 전달함
- `.gitignore` 에 `workspace/` 가 등재되어 있는지 확인 (없으면 추가 안내)
- 프로젝트 루트 `CLAUDE.md` 에 `/work` 용 빌드 명령 라인이 있는지 확인 (Step 5 에서 처리, 없으면 추가 안내)

## 워크플로우

### Step 1: 요구사항 읽기

사용자가 전달한 경로 또는 링크의 문서를 읽는다.
- 파일 경로면 Read
- URL이면 WebFetch
- `brain/...` 경로면 Read (brain = 사용자의 개인 지식베이스 repo. 환경에 따라 없을 수 있으며, 없으면 일반 파일 경로로 취급)

### Step 2: workspace/ 구조 생성

프로젝트 루트에 다음 구조 생성:

```
{project}/
└── workspace/
    ├── plan.md      ← Step 3에서 작성
    ├── handoff.md   ← Step 4에서 작성
    └── archive/     ← 빈 폴더 (작업 완료 시 사용)
```

`workspace/` 가 이미 존재하고 `plan.md` 가 있으면:
→ "기존 plan.md 가 있습니다. 덮어쓸까요?" 확인 후 진행.

### Step 3: plan.md 작성

아래 템플릿을 기반으로 요구사항 내용을 채운다.

**템플릿**:
```markdown
# Project
- project name : {archive를 위한 프로젝트 이름}
- commit-name : {커밋시 prefix로 사용할 이름 (예: able-wlf)}

# Phases

## Phase 1: {제목}

- **목적**:

### Tasks:
- [ ] Task 1.1 — {설명}
  - commit-type: {feat | fix | refactor | chore ...}
  - 변경 범위: {패키지/모듈 경로 — 예: `app/src/main/java/kr/co/bdacs/order/**`}
  - 완료 기준: {테스트로 검증 가능한 기준 1줄}
- [ ] Task 1.2 — {설명}
  - commit-type:
  - 변경 범위:
  - 완료 기준:

## Phase 2: {제목}

- **목적**:

### Tasks:
- [ ] Task 2.1 — {설명}
  - commit-type:
  - 변경 범위:
  - 완료 기준:

## Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
|      |        |            |

## Dependencies

-

## Rollback Plan

-

## Related Knowledge

-
```

**작성 규칙**:
- Phase = 독립적으로 완료 가능한 작업 단위 (1~3일 분량)
- Task = **의미 있는 커밋 1세트** (test / code / refactor 각 1커밋)
  - 기준: 리뷰어가 커밋 로그만 보고 변경 의도를 이해할 수 있는 응집된 단위
  - 한 Task 의 변경 범위가 서로 무관한 모듈/패키지에 걸치면 Task 를 쪼갠다
  - 반대로 한 커밋이 한 줄짜리가 될 만큼 잘게 쪼개졌으면 인접 Task 와 합친다
- Task 메타데이터 3종은 필수:
  - `commit-type`: /work 가 code 커밋 prefix 로 그대로 사용 (feat/fix/refactor/chore ...)
  - `변경 범위`: 패키지/디렉토리 수준 glob — /work 가 커밋 시 이 범위 밖 파일을 걸러낸다
  - `완료 기준`: test-coder 가 테스트로 옮길 수 있는 검증 가능한 문장
- 추측 금지 — 요구사항에서 도출되지 않는 내용은 `{TODO: 확인 필요}` 플레이스홀더

### Step 4: handoff.md 작성

초기 상태로 생성:

```markdown
> 다음 세션 · 다음 사람 (또는 미래의 나) 이 바로 이어받을 수 있게 하는 인수인계 노트.

## 현재 상태

- **작업 생성일**: {yyyy-MM-dd HH:mm}
- **마지막 수정일**: {yyyy-MM-dd HH:mm}
- **완료 Phase**: -
- **진행 Phase**: Phase 1 (시작 전)
- **다음 Phase**: -

## 이번 세션의 중요한 결정

-

## 알아야 할 위험 · 주의점

-

## 미결 질문

- [ ]

## 다음 세션 시작 지점

- workspace/plan.md 의 Phase 1, Task 1.1 부터 시작

## commit log

## 환경 · 브랜치 · 의존

- 브랜치:
- 마지막 커밋:
- 실행 중 프로세스:
- 외부 상태 (DB 마이그레이션 · MQ 등):
```

### Step 5: 환경 확인 (.gitignore + 빌드 명령)

1. **`.gitignore`**: 프로젝트 루트의 `.gitignore` 에 `workspace/` 가 있는지 확인. 없으면 사용자에게 알리고 추가 여부 확인.

2. **빌드 명령 라인**: `/work` 는 프로젝트 루트 `CLAUDE.md` 에서 다음 정확한 패턴을 grep 해 빌드 명령(`$BUILD_CMD`)을 얻는다:
   ```
   본 프로젝트 빌드 명령: `./gradlew test`
   ```
   이 라인이 없으면 `/work` 가 **매 호출마다 빌드 명령을 되묻는다**. 라인 존재를 확인하고, 없으면 어떤 명령을 쓸지 사용자에게 물어 그 값으로 추가를 안내한다. `CLAUDE.md` 자체가 없으면 생성 여부를 확인한다.

### Step 6: 완료 보고

```
✅ workspace/ 초기화 완료

생성된 파일:
  - workspace/plan.md     (Phase {N}개, Task {M}개)
  - workspace/handoff.md
  - workspace/archive/

TODO 플레이스홀더: {N}건 (있으면 목록)

커밋 prefix: {commit-name}

다음 단계:
  - /work 호출 — Task 1개씩 TDD 사이클(브랜치 확보 → test-coder → (Red 검증) → coder → code-review → verifier → simplify)을 자동 진행
  - 모든 Task 완료 후 /close 로 archive
```

> `/work` 가 빌드/테스트를 알아서 실행하므로, plan 단계에서 빌드 명령을 직접 돌릴 필요는 없다.

## 주의사항

- build 명령어는 절대 AI context 안에서 실행하지 않는다 — 사용자에게 실행 안내만 한다
- TODO 플레이스홀더가 3개 이상이면 plan 작성 전 사용자에게 핵심 질문을 한다
- `.gitignore` 추가는 사용자 승인 후 실행

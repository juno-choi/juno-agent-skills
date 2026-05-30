---
name: work
description: "workspace/plan.md 의 다음 미완료 Task 1개를 TDD 사이클(test-coder → coder → verifier → code-simplifier)로 자동 진행하고 test/code/refactor 3개 커밋으로 마무리하는 스킬. '/work', 'work', '다음 task', '다음 task 진행', '다음 task 진행해줘', '다음 작업', '다음 작업 시작', '다음 작업 진행', '다음 거 작업', '다음 거 진행', 'tdd 사이클', 'tdd 진행', 'tdd 한 번 돌려', 'red green refactor', '한 사이클 돌려', '다음 단계 진행', 'plan 다음 task', 'workspace 다음 task', 'task 이어서 진행', 'phase x task y 진행', 'task 1.x 진행' 등 workspace/plan.md 의 Task 를 이어서 진행하려는 모든 표현에 반드시 사용한다."
---

# /work — Task 1개 TDD 사이클 실행

`workspace/plan.md` 의 **다음 미완료 Task 1개** 를 자동 선택하고
test-coder → coder → verifier → code-simplifier 순으로 진행한 뒤
test / code / refactor 3개 커밋으로 마무리한다.

## 전제 조건

- 현재 작업 디렉토리가 대상 프로젝트 루트
- `workspace/plan.md` 가 존재 (없으면 `/plan` 부터 실행 안내)
- 프로젝트 루트 `CLAUDE.md` 에 빌드 명령 라인 존재 (예: `` 본 프로젝트 빌드 명령: `./gradlew test` ``)
- `git` 작업 트리가 깨끗하거나, 현재 진행 중인 Task 의 변경분만 남아있어야 함
- 작업은 `main`/`master` 가 아닌 별도 작업 브랜치에서 진행 (Step 0 에서 보장)

## 워크플로우

### Step 0: 브랜치 점검 (main 보호)

작업은 **절대 `main` 브랜치에서 직접 진행하지 않는다.**

1. 현재 브랜치 확인:
   ```bash
   git rev-parse --abbrev-ref HEAD
   ```

2. 분기 처리:
   - **현재 브랜치가 `main` (또는 `master`)인 경우**:
     - 사용자에게 새 작업 브랜치명을 물어본다:
       ```
       현재 main 브랜치입니다. 작업용 브랜치를 새로 만들겠습니다.
       브랜치명을 입력하세요 (예: feature/phase-1-task-1):
       ```
     - 입력받은 이름으로 새 브랜치를 만들고 checkout:
       ```bash
       git checkout -b {입력받은 브랜치명}
       ```
     - checkout 성공 후 다음 단계로 진행.
   - **현재 브랜치가 `main`/`master`가 아닌 다른 브랜치인 경우**:
     - 사용자에게 1회 확인:
       ```
       현재 브랜치: {브랜치명}
       이 브랜치에서 작업을 진행할까요? (y/N)
       ```
     - `y` → 그대로 다음 단계 진행.
     - `N` → 기존 로컬 브랜치 목록을 보여주고, 맨 마지막에 직접 입력 옵션을 함께 제시:
       ```bash
       git branch --format='%(refname:short)'
       ```
       위 목록을 번호와 함께 출력하고, 마지막 항목으로 `직접 입력 (새 브랜치 생성)` 을 추가:
       ```
       작업할 브랜치를 선택하세요:
         1) {기존 브랜치 A}
         2) {기존 브랜치 B}
         ...
         N) 직접 입력 (새 브랜치 생성)
       ```
       - 기존 브랜치 선택 → `git checkout {선택 브랜치}` 후 진행.
       - `직접 입력` 선택 → 새 브랜치명을 물어보고 `git checkout -b {입력값}` 후 진행.

3. 브랜치 확정 전에는 어떤 agent 호출도, 커밋도 하지 않는다.

### Step 1: 사전 점검

1. `workspace/plan.md` 존재 확인. 없으면:
   ```
   ❌ workspace/plan.md 가 없습니다.
   먼저 /plan 으로 작업 계획을 작성하세요.
   ```
   라고 보고하고 종료.

2. `git status --short` 으로 현재 작업 트리 상태 확인.
   - 깨끗하면 OK.
   - 변경분이 있으면 사용자에게 표시하고 `이 변경분을 그대로 안고 다음 Task 를 진행할까요?` 1회 확인.

3. 빌드 명령 추출. 프로젝트 루트 `CLAUDE.md` 에서 다음 패턴을 grep:
   ```
   본 프로젝트 빌드 명령:\s*`([^`]+)`
   ```
   - 매칭되면 그 명령을 `$BUILD_CMD` 로 사용.
   - 매칭 안되면 사용자에게 1회 확인:
     `CLAUDE.md 에 빌드 명령 라인이 없습니다. 어떤 명령을 사용할까요? (기본: ./gradlew test)`

4. `workspace/plan.md` 의 `# Project` 섹션에서 `commit name` 추출.
   없으면 사용자에게 확인.

### Step 2: 다음 Task 선정

`workspace/plan.md` 를 읽고:

- 가장 위쪽의 **`- [ ] Task X.Y`** 라인을 찾는다.
- 해당 Task 가 속한 Phase 번호와 Task 설명을 추출한다.
- 모든 Task 가 완료(`- [x]`)면:
  ```
  ✅ 모든 Task 가 완료되었습니다.
  /close 로 archive 진행을 권장합니다.
  ```
  종료.

확인 출력:
```
다음 Task: Phase {N} / Task {N.M}
설명: {Task 설명}

이 Task 를 진행할까요? (y/N)
```
사용자 승인 후 진행.

### Step 3: Red 단계 (test-coder)

1. `test-coder` agent 를 호출. 프롬프트에 다음을 포함:
   - 대상 Task 의 Phase / Task 번호 + 설명
   - `workspace/plan.md` 경로
   - 프로젝트 `CLAUDE.md` 경로
   - "build/test 명령은 직접 실행하지 말 것" 명시

2. agent 완료 후 자동 빌드 (redirect+tail):
   ```bash
   $BUILD_CMD > workspace/.last_build.log 2>&1; tail -25 workspace/.last_build.log
   ```
   - `workspace/.last_build.log` 에 전체 출력 저장
   - `tail -25` 결과만 context 에 적재

3. 결과 판정:
   - **BUILD FAILED + 테스트 실패**: Red 정상 → 다음 단계 진행
   - **BUILD SUCCESSFUL**: 테스트가 실패하지 않음 → 테스트가 의미 있는지 사용자 확인 요청 후 일시 중단
   - **컴파일 실패**: 스켈레톤 누락 가능성 → test-coder 에게 보강 요청 1회 재호출, 그래도 실패 시 중단

### Step 4: test 커밋

변경된 테스트/스켈레톤 파일만 add 후 커밋:

```bash
git add {test/skeleton 파일들}
git commit -m "test: {commit-name} [phase-{N}] [task-{N.M}] {Task 설명}"
```

> `git commit` 은 plugin 의 PreToolUse hook 으로 ask 권한 프롬프트가 뜬다.
> 사용자가 거부하면 스킬은 즉시 중단하고 보고만 한다.

커밋 hash 를 기록해 둔다 (Step 9 에서 사용).

### Step 5: Green 단계 (coder)

1. `coder` agent 호출. 프롬프트에 동일 컨텍스트 + Step 3 의 테스트 코드 위치 전달.

2. agent 완료 후 자동 빌드 (Step 3 와 동일 패턴).

3. 결과 판정:
   - **BUILD SUCCESSFUL**: Green → 다음 단계 진행
   - **BUILD FAILED**:
     ```
     ❌ Green 실패.
     로그: workspace/.last_build.log
     원인 파악 후 다시 /work 호출하거나, coder 에게 직접 수정 요청하세요.
     ```
     중단.

### Step 6: code 커밋

```bash
git add {구현 파일들}
git commit -m "feat: {commit-name} [phase-{N}] [task-{N.M}] {Task 설명}"
```

prefix(`feat`/`fix`/`refactor`/`chore`)는 Task 성격에 맞게 선택.
plan.md 에 별도 명시가 없으면 기본 `feat`. fix Task 면 `fix`.

### Step 7: Verifier

`verifier` agent 호출. 결과:
- **종합 판정 PASS**: 다음 단계 진행
- **종합 판정 FAIL**:
  ```
  ❌ Verifier FAIL.
  지적 사항을 정리해 사용자에게 의사결정 요청.
  ```
  중단. 사용자가 coder 재호출 / 수동 수정 / 그대로 진행 결정.

### Step 8: Refactor 단계 (선택)

1. `code-simplifier:code-simplifier` skill 가용 여부 확인.
   - 시스템에 `code-simplifier:code-simplifier` 가 등록되지 않았으면:
     ```
     ⏭️ code-simplifier 미설치 — refactor 단계 스킵.
     필요 시 별도 plugin 설치 후 수동 실행.
     ```
     Step 9 로.

2. 가용하면 호출. 변경사항이 있으면 자동 빌드 (Step 3 와 동일 패턴).
   - **BUILD SUCCESSFUL**: refactor 커밋 생성
     ```bash
     git add {변경 파일들}
     git commit -m "refactor: {commit-name} [phase-{N}] [task-{N.M}] {Task 설명}"
     ```
   - **BUILD FAILED**:
     ```
     ❌ Refactor 후 빌드 실패. 로그: workspace/.last_build.log
     ```
     중단. 사용자가 결정.
   - **변경사항 없음**: refactor 커밋 생략.

### Step 9: plan.md Task 체크 + handoff.md 갱신

1. `workspace/plan.md` 에서 해당 Task 라인을 `- [ ]` → `- [x]` 로 변경.

2. `workspace/handoff.md` 갱신:
   - `마지막 수정일` 현재 시각으로 변경
   - `완료 Phase` / `진행 Phase` / `다음 Phase` 업데이트
   - `commit log` 섹션에 이번 사이클 커밋 hash 추가:
     ```
     - [phase-{N}] [task-{N.M}] {Task 설명}
       - test    {hash} test: ...
       - code    {hash} feat: ...
       - refactor {hash} refactor: ...   (있을 때만)
     ```

3. 변경된 plan.md / handoff.md 는 별도 커밋하지 않는다 (다음 `/work` 또는 `/close` 호출 시 함께 처리).
   단, plan.md / handoff.md 만 단독 변경된 상태가 누적되지 않도록 사용자에게 짧게 보고.

### Step 10: 완료 보고

```
✅ Phase {N} / Task {N.M} 완료

커밋:
  - test  {hash}  test: ...
  - code  {hash}  feat: ...
  - refactor {hash}  refactor: ...   (있을 때만)

plan.md: Task {N.M} 체크 완료
handoff.md: commit log 갱신

남은 Task: {M개}

다음 단계:
  - 이어서 진행: /work 다시 호출
  - 모두 끝났으면: /close
```

## 주의사항

- **빌드 결과 판단은 tail -25 만 본다**: 더 자세한 분석이 필요하면 사용자에게 `workspace/.last_build.log` 직접 확인 요청.
- **agent 안에서 빌드/테스트 명령을 직접 실행하지 못하도록** test-coder/coder 호출 프롬프트에 명시 (이미 agent 정의에 적혀 있지만 한 번 더 강조).
- **커밋 메시지 prefix 는 plan.md 의 commit name 을 그대로 사용**. 추측 금지.
- **`workspace/.last_build.log` 는 `.gitignore` 에 포함된 `workspace/` 하위라서 별도 ignore 불필요**.
- **PreToolUse ask hook 이 git commit 마다 뜸**: 사용자가 거부하면 즉시 중단. amend/force 로 우회하지 않는다.
- **Task 1개 단위로 종료한다**: Phase 전체 자동 진행 금지. 매 호출마다 다음 Task 1개씩.
- **Verifier FAIL 시 자동 수정 금지**: 반드시 사용자 결정.
- **`main`/`master` 직접 작업 금지**: Step 0 에서 브랜치를 확정하기 전에는 agent 호출/커밋을 시작하지 않는다. main 이면 새 브랜치명을 물어 `checkout -b`, 다른 브랜치면 진행 여부를 1회 확인한다.

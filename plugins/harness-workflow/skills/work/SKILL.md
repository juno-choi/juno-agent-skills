---
name: work
description: "workspace/plan.md 의 다음 미완료 Task 1개를 TDD 사이클(test-coder → coder → code-review → verifier → simplify)로 자동 진행하고 test/code/refactor 3개 커밋 지점에서 plan.md 의 commit-mode 값(auto|manual)에 따라 자동 커밋하거나 커밋 메시지만 제시해 사용자가 직접 커밋하게 하는 스킬. '/work', 'work', '다음 task', '다음 task 진행', '다음 task 진행해줘', '다음 작업', '다음 작업 시작', '다음 작업 진행', '다음 거 작업', '다음 거 진행', 'tdd 사이클', 'tdd 진행', 'tdd 한 번 돌려', 'red green refactor', '한 사이클 돌려', '다음 단계 진행', 'plan 다음 task', 'workspace 다음 task', 'task 이어서 진행', 'phase x task y 진행', 'task 1.x 진행' 등 workspace/plan.md 의 Task 를 이어서 진행하려는 모든 표현에 반드시 사용한다."
---

# /work — Task 1개 TDD 사이클 실행

`workspace/plan.md` 의 **다음 미완료 Task 1개** 를 자동 선택하고
test-coder → (Red 검증) → coder → (Green 검증) → verifier(read-only) → code-review(read-only) → simplify 순으로 진행한 뒤
test / code / refactor 3개 지점에서 `plan.md` 의 `commit-mode` 플래그(`auto` | `manual`, 기본값 `manual`)에 따라 **자동으로 `git commit` 까지 실행하거나, `git add` 까지만 하고 사용자가 직접 커밋하도록 안내한다.**

## 코드 리뷰 조건(code-review) — Step 5.5 정확성 게이트

- `/work` Step 5.5 는 **내장 `code-review` skill 을 사용한다** (read-only, effort `low`|`medium`, `--fix`/`--comment` 미사용). 목적은 커밋 전 **blocking 정확성 버그만** 잡는 것이다.
- **`reviewer` agent 는 이 단계에서 쓰지 않는다.** 컨벤션 점검은 Step 7 `verifier` 의 책임이므로, Step 5.5 에서 컨벤션까지 보면 두 게이트가 중복된다. (별도로 "리뷰해줘"로 `reviewer` agent 를 직접 호출하는 것은 `/work` 흐름과 무관하게 언제든 가능하다.)
- 아래 파일이 있으면 리뷰 판단의 보조 기준으로 참조한다.
  - ~/.claude/REVIEW.md

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

0. **재개 확인** — `workspace/handoff.md` 에 `## pending` 섹션이 있으면 이전 `/work` 가 중단된 것이다. 그 내용(중단된 Task·`last-step`·dirty files·note)을 사용자에게 보여주고 `이어서 재개할까요? (y/N)` 1회 확인한다. 재개하면 기록된 `last-step` 의 다음 단계부터 진행하고, Task 정상 완료 시 `## pending` 섹션을 제거한다. (상세는 아래 "중단 처리" 참조)

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

4. `workspace/plan.md` 의 `# Project` 섹션에서 `commit-name` 추출.
   없으면 사용자에게 확인.

5. 같은 섹션에서 `commit-mode` 추출 ($COMMIT_MODE, `auto` 또는 `manual`).
   - 없으면 **기본값 `manual`** 로 간주하고 plan.md 에 `commit-mode : manual` 을 보강해둔다 (추측으로 `auto` 를 선택하지 않는다).
   - `auto`: Step 4/6/8 에서 스킬이 `git commit` 까지 자동 실행.
   - `manual`: Step 4/6/8 에서 스킬은 `git add` 까지만 하고 커밋 메시지를 제시, 실제 `git commit` 은 사용자가 직접 실행.

### Step 2: 다음 Task 선정

`workspace/plan.md` 를 읽고:

- 가장 위쪽의 **`- [ ] Task X.Y`** 라인을 찾는다.
- 해당 Task 가 속한 Phase 번호와 Task 설명을 추출한다.
- Task 하위의 메타데이터 3종을 추출한다:
  - `commit-type` → code 커밋 prefix 로 사용 ($COMMIT_TYPE)
  - `변경 범위` → 커밋 시 파일 대조 기준 ($SCOPE)
  - `완료 기준` → test-coder 프롬프트에 전달
  - 셋 중 누락이 있으면 사용자에게 1회 확인 후 plan.md 에 보강하고 진행.
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
commit-type: {commit-type}
변경 범위: {변경 범위}
완료 기준: {완료 기준}

이 Task 를 진행할까요? (y/N)
```
사용자 승인 후 진행.

### Step 3: Red 단계 (test-coder)

`test-coder` agent 를 호출. 프롬프트에 다음을 포함:
- 대상 Task 의 Phase / Task 번호 + 설명 + `완료 기준` + `변경 범위`
- "테스트는 `완료 기준` 을 검증해야 하고, 생성 파일은 `변경 범위` 안에 둘 것" 명시
- `workspace/plan.md` 경로
- 프로젝트 `CLAUDE.md` 경로
- "build/test 명령은 직접 실행하지 말 것" 명시

### Step 3.5: Red 검증 (컴파일 성공 + 테스트 실패)

test-coder 산출물이 TDD Red 원칙(`agents/test-coder.md`: "컴파일 성공 + 테스트 실패")을 실제로 만족하는지 빌드로 1회 확인한다. test 커밋 전에 Red 임을 보장해, 검증 효력 없는 테스트(항상 통과)나 컴파일조차 안 되는 스켈레톤이 커밋되는 것을 막는다.

```bash
$BUILD_CMD > workspace/.last_build.log 2>&1; CODE=$?; tail -25 workspace/.last_build.log; echo "EXIT: $CODE"
```

판정 (**exit code(`$CODE`) 가 1차 기준**, 빌드 문구·tail 은 원인 분류용 보조):
- **EXIT ≠ 0 + 로그가 컴파일 실패**: 스켈레톤이 컴파일되지 않음 → test-coder 에게 보강 요청 1회 재호출 후 재검증. 그래도 실패면 중단(Step 9 의 pending 마커 기록).
- **EXIT 0 (테스트까지 통과)**: 🚨 테스트가 실패하지 않음 = Red 가 아니다. 테스트가 기대 동작을 검증하지 못하거나 구현이 이미 존재. test-coder 에게 "실패하는 테스트로 보강" 1회 재요청 후 재검증.
- **EXIT ≠ 0 + 로그가 테스트 실패(컴파일 에러 아님)**: 정상 Red → Step 4 로 진행.

### Step 4: test 커밋 ($COMMIT_MODE 분기)

1. `git status --short` 로 변경 파일 전체를 확인한다.
2. 각 파일을 Task 의 `변경 범위`($SCOPE) 및 test/skeleton 여부와 대조한다:
   - 범위 안 + test/skeleton 파일 → add 대상
   - **범위 밖 파일은 add 하지 않고** 보고에 목록으로 남긴다
   - `git add -A` / `git add .` **금지** — 반드시 파일을 명시해서 add
3. 대상 파일만 스테이징한다:

```bash
git add {범위 안 test/skeleton 파일들}
```

4. `$COMMIT_MODE` 에 따라 분기:
   - **`auto`**: 바로 커밋 실행.
     ```bash
     git commit -m "test: {commit-name} [phase-{N}] [task-{N.M}] {Task 설명}"
     ```
     커밋 hash 를 기록해 둔다 (Step 9 에서 사용).
   - **`manual`**: **커밋은 직접 실행하지 않는다.** 아래 커밋 메시지를 제시하고 사용자에게 직접 커밋을 요청한다:
     ```
     📦 test 커밋 준비 완료. 아래 명령을 직접 실행해주세요:

     git commit -m "test: {commit-name} [phase-{N}] [task-{N.M}] {Task 설명}"

     커밋 후 계속 진행할까요? (y/N)
     ```
     사용자가 커밋 완료를 확인하면 `git rev-parse HEAD` 로 커밋 hash 를 확인해 기록해 둔다 (Step 9 에서 사용). 아직 커밋하지 않았거나 메시지를 수정했다면 그 상태를 존중하고 다음 단계로 진행하기 전에 다시 확인한다.

### Step 5: Green 단계 (coder)

1. `coder` agent 호출. 프롬프트에 동일 컨텍스트 + Step 3 의 테스트 코드 위치 전달.

2. agent 완료 후 자동 빌드 (redirect+exit code+tail):
   ```bash
   $BUILD_CMD > workspace/.last_build.log 2>&1; CODE=$?; tail -25 workspace/.last_build.log; echo "EXIT: $CODE"
   ```
   - `workspace/.last_build.log` 에 전체 출력 저장
   - exit code(`$CODE`) + `tail -25` 결과만 context 에 적재

3. 결과 판정 (**exit code 가 1차 기준**, 빌드 문구·tail 은 원인 분류용 보조 — Gradle `BUILD SUCCESSFUL`/Maven `BUILD SUCCESS`/pytest 등 빌드 도구마다 성공 문구가 달라 문구 매칭은 깨지기 쉽다):
   - **EXIT 0**: Green → 다음 단계 진행
   - **EXIT ≠ 0 (테스트/스켈레톤 컴파일 실패)**: test-coder 산출물 문제 → test-coder 에게 보강 요청 1회 재호출 후 재빌드, 그래도 실패 시 중단(Step 9 의 pending 마커 기록).
   - **EXIT ≠ 0 (구현 문제)**:
     ```
     ❌ Green 실패.
     로그: workspace/.last_build.log
     원인 파악 후 다시 /work 호출하거나, coder 에게 직접 수정 요청하세요.
     ```
     중단(Step 9 의 pending 마커 기록).

### Step 5.5: code-review (커밋 전 버그 게이트)

Green 빌드 성공 직후, **아직 커밋하기 전**(워킹트리에 구현 diff 가 남아있는 상태)에서 내장 `code-review` skill 을 호출한다.

- 옵션: `--fix` / `--comment` **둘 다 사용하지 않는다** (read-only 리뷰만). effort 는 **low 또는 medium** (high 는 불확실 finding 이 많아 게이트가 시끄러워짐).
- 목적: 방금 짠 구현 diff 의 **blocking correctness 버그**만 탐지 — "지금 커밋하면 안 되는 정확성 결함". 정리(cleanup) finding 은 Step 8 `simplify` 의 몫이라 제외하고, 달성도·커버리지·컨벤션은 Step 7 `verifier` 의 몫이라 여기서 판단하지 않는다. (세 게이트의 책임은 서로 겹치지 않게 분리되어 있다.)
- 결과 판정:
  - **심각 버그 없음**: 다음 단계(Step 6 커밋)로 진행.
  - **심각 버그 발견**:
    ```
    ⚠️ code-review 가 버그를 지적했습니다.
    지적 사항: {요약}
    → coder 재호출로 수정 / 수동 수정 / 무시하고 진행 중 선택하세요.
    ```
    커밋하지 않고 **중단**, 사용자 결정을 받는다. 수정 후 빌드가 다시 Green 이면 이 단계를 재실행한다.
- `code-review` 가 가용하지 않으면 한 줄 보고 후 스킵하고 Step 6 으로 진행한다.

### Step 6: code 커밋 ($COMMIT_MODE 분기)

1. Step 4 와 동일하게 `git status --short` → `변경 범위` 대조 후 범위 안 구현 파일만 add:

```bash
git add {범위 안 구현 파일들}
```

2. prefix 는 **plan.md 해당 Task 의 `commit-type` 필드($COMMIT_TYPE)를 그대로 사용**(누락 시 Step 2 에서 이미 보강했으므로 여기서 추측하지 않는다). `$COMMIT_MODE` 에 따라 분기:
   - **`auto`**: 바로 커밋 실행.
     ```bash
     git commit -m "{commit-type}: {commit-name} [phase-{N}] [task-{N.M}] {Task 설명}"
     ```
     커밋 hash 를 기록해 둔다.
   - **`manual`**: **커밋은 직접 실행하지 않는다.** 아래처럼 커밋 메시지를 제시하고 사용자에게 직접 커밋을 요청한다:
     ```
     📦 code 커밋 준비 완료. 아래 명령을 직접 실행해주세요:

     git commit -m "{commit-type}: {commit-name} [phase-{N}] [task-{N.M}] {Task 설명}"

     커밋 후 계속 진행할까요? (y/N)
     ```
     사용자가 커밋 완료를 확인하면 `git rev-parse HEAD` 로 커밋 hash 를 확인해 기록해 둔다.

### Step 7: Verifier

`verifier` agent 호출 (read-only — Step 6 에서 code 커밋이 **완료된 상태**여야 검증을 시작한다. `manual` 모드에서 사용자가 아직 커밋 전이면 진행하지 않고 대기한다).

- **종합 판정 PASS**: 다음 단계 진행.
- **종합 판정 FAIL**: code 커밋이 이미 생성됐으므로 그냥 중단하면 불완전한 커밋이 히스토리에 남는다. 다음을 안내하고 중단한다:
  ```
  ❌ Verifier FAIL — code 커밋이 이미 생성된 상태입니다.
  지적 사항: {요약}

  복구 옵션:
    1) 수정 후 재검증(권장): `git reset --soft HEAD~1` 로 code 커밋만 되돌려
       워킹트리에 구현 diff 를 복원 → coder 재호출/수동 수정 → Step 5 Green 빌드부터 재개
    2) fixup 보완: 커밋은 두고 별도 수정 커밋으로 보완
    3) 무시하고 진행: 사용자가 명시적으로 수용
  ```
  자동 수정 금지 — 반드시 사용자 결정. 중단 시 Step 9 의 pending 마커에 `last-step: verifier-FAIL` 로 기록한다.

### Step 8: Refactor 단계 (선택)

1. Claude Code 내장 `simplify` skill 을 호출한다.
   - `simplify` 는 변경된 코드의 중복/단순화/효율/altitude 정리만 수행하고 **버그 헌팅은 하지 않는다** (정확성 검증은 Step 7 Verifier 가 이미 담당).
   - 동작을 바꾸지 않는 구조 개선이 목적이므로 TDD Refactor 단계와 정확히 일치한다.
   - 내장 skill 이라 별도 설치가 필요 없다. 혹시 가용하지 않으면:
     ```
     ⏭️ simplify 미가용 — refactor 단계 스킵.
     ```
     Step 9 로.

2. 호출 후 변경사항이 있으면 자동 빌드 (Step 5 와 동일 패턴 — exit code 1차 판정).
   - **EXIT 0**: refactor 커밋 ($COMMIT_MODE 분기, Step 4 와 동일하게 범위 대조 후 add)
     ```bash
     git add {범위 안 변경 파일들}
     ```
     - **`auto`**: 바로 커밋 실행.
       ```bash
       git commit -m "refactor: {commit-name} [phase-{N}] [task-{N.M}] {Task 설명}"
       ```
       커밋 hash 를 기록해 둔다.
     - **`manual`**: **커밋은 직접 실행하지 않는다.** 아래 커밋 메시지를 제시하고 사용자에게 직접 커밋을 요청한다:
       ```
       📦 refactor 커밋 준비 완료. 아래 명령을 직접 실행해주세요:

       git commit -m "refactor: {commit-name} [phase-{N}] [task-{N.M}] {Task 설명}"

       커밋 후 계속 진행할까요? (y/N)
       ```
       사용자가 커밋 완료를 확인하면 `git rev-parse HEAD` 로 커밋 hash 를 확인해 기록해 둔다.
   - **EXIT ≠ 0**:
     ```
     ❌ Refactor 후 빌드 실패. 로그: workspace/.last_build.log
     ```
     중단(Step 9 의 pending 마커 기록). 사용자가 결정.
   - **변경사항 없음**: refactor 커밋 생략.

### Step 9: plan.md Task 체크 + handoff.md 갱신

1. `workspace/plan.md` 에서 해당 Task 라인을 `- [ ]` → `- [x]` 로 변경.

2. `workspace/handoff.md` 갱신:
   - `## pending` 섹션이 있으면 **제거**한다 (이번 Task 가 정상 완료됐으므로 중단 마커는 더 이상 유효하지 않다).
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

커밋에서 제외된 범위 밖 파일: {목록 또는 없음}

남은 Task: {M개}

다음 단계:
  - 이어서 진행: /work 다시 호출
  - 모두 끝났으면: /close
```

## 중단 처리 (pending 마커)

Red 검증 실패 / Green 실패 / code-review 버그 / verifier FAIL / refactor 빌드 실패 등으로 중단할 때는, 다음 `/work` 가 상태를 복원할 수 있도록 `workspace/handoff.md` 에 `## pending` 섹션을 기록한다(이미 있으면 갱신):

```markdown
## pending
- task: Phase {N} / Task {N.M} — {설명}
- last-step: {red-FAIL | green-FAIL | code-review-bug | verifier-FAIL | refactor-FAIL}
- dirty-files: {git status --short 요약}
- note: {사용자 결정 대기 사항 한 줄}
```

- Task 가 정상 완료되면(Step 9) `## pending` 섹션을 **반드시 제거**한다 — 잔존하면 다음 호출이 중단 상태로 오인한다.
- `handoff.md` 는 `.gitignore` 대상(`workspace/`)이라 커밋되지 않으므로 마커를 자유롭게 갱신해도 안전하다.

## 주의사항

- **빌드 판정은 exit code(`$CODE`) 가 1차 기준**: 빌드 도구마다 성공 문구가 다르므로(`BUILD SUCCESSFUL` vs `BUILD SUCCESS` 등) 문구 매칭에 의존하지 않는다. `tail -25` 와 빌드 문구는 실패 원인 분류용 보조다. 더 자세한 분석이 필요하면 사용자에게 `workspace/.last_build.log` 직접 확인 요청.
- **agent 안에서 빌드/테스트 명령을 직접 실행하지 못하도록** test-coder/coder 호출 프롬프트에 명시 (이미 agent 정의에 적혀 있지만 한 번 더 강조).
- **커밋 메시지의 commit-name / commit-type 은 plan.md 값을 그대로 사용**. 추측 금지.
- **커밋은 의미 있는 파일 묶음으로만**: `git add -A`/`git add .` 금지, Task `변경 범위` 밖 파일은 스테이징하지 않고 보고. 범위 밖 변경이 실제로 Task 에 필요했다면 plan.md 의 `변경 범위` 를 갱신한 뒤 커밋.
- **커밋 자동/수동 여부는 `plan.md` 의 `commit-mode` 값을 따른다**: `manual`(기본값)이면 test/code/refactor 3개 지점 모두 `git add` 로 스테이징하고 커밋 메시지를 제시하기까지만 하며, 실제 `git commit` 은 사용자가 직접 하고 완료를 확인받은 뒤 다음 단계로 진행한다. `auto` 면 각 지점에서 바로 `git commit` 까지 실행한다. `commit-mode` 를 임의로 추측해 다른 값으로 바꾸지 않는다.
- **`workspace/.last_build.log` 는 `.gitignore` 에 포함된 `workspace/` 하위라서 별도 ignore 불필요**.
- **Task 1개 단위로 종료한다**: Phase 전체 자동 진행 금지. 매 호출마다 다음 Task 1개씩.
- **Verifier FAIL 시 자동 수정 금지**: 반드시 사용자 결정.
- **`main`/`master` 직접 작업 금지**: Step 0 에서 브랜치를 확정하기 전에는 agent 호출/커밋을 시작하지 않는다. main 이면 새 브랜치명을 물어 `checkout -b`, 다른 브랜치면 진행 여부를 1회 확인한다.

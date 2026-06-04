---
name: brain-report
description: "완료된 workspace 작업(archive)을 회고 리포트로 증류해 brain(사용자의 개인 지식베이스 repo)의 raw/ 에 전달하는 스킬.
  'brain 리포트', 'brain에 전달', 'brain 아카이빙', '회고 리포트 만들어', '완료 내용 brain으로 보내줘', 'brain-report' 등
  완료된 작업을 지식베이스에 기록하려는 표현에 사용한다. 보통 /close 이후에 호출한다."
---

# /brain-report — 완료 작업 회고 리포트 → brain 전달

`workspace/archive/{N}_{slug}/` 의 plan.md + handoff.md + 커밋 히스토리를 증류해
회고 리포트 1개 파일을 만들고, brain 의 `raw/` 에 떨어뜨린다.
이후 wiki 반영은 brain 세션의 `/ingest` 가 담당한다 (이 스킬은 wiki 를 건드리지 않는다).

## 전제 조건

- 현재 작업 디렉토리가 대상 프로젝트 루트
- `workspace/archive/` 에 close 된 작업 폴더가 1개 이상 존재 (없으면 `/close` 먼저 안내)
- brain 이 없는 환경(팀원 등)이면 Step 3 에서 정상 종료

## 워크플로우

### Step 1: 대상 archive 선택

`workspace/archive/` 의 폴더 목록을 확인한다.
- 기본값: 번호가 가장 큰 (= 가장 최근) 폴더
- 사용자가 특정 작업을 지정하면 해당 폴더
- archive 가 비어 있고 `workspace/plan.md` 만 있으면: "아직 close 전입니다. `/close` 를 먼저 진행할까요?" 안내

선택한 폴더의 `plan.md` + `handoff.md` 를 읽는다 (읽기만 — archive 불변 원칙).

### Step 2: 커밋 히스토리 수집

- 1차: `handoff.md` 의 commit log 섹션 활용
- 보강: `git log --oneline` 으로 해당 작업의 commit-name prefix (plan.md 의 `commit-name`) 가 들어간 커밋을 grep

### Step 3: brain 루트 해석 (하드코딩 금지)

brain 경로는 환경마다 다르므로 다음 순서로 해석한다:

1. 사용자 글로벌 설정(`~/.claude/CLAUDE.md`)에 brain 경로 선언이 있으면 그 경로에서 brain 루트를 도출
2. 없으면 사용자에게 brain 루트 경로를 질문
3. "brain 없음" 응답이면 → "brain 미사용 환경으로 판단, 리포트 생성을 건너뜁니다" 안내 후 종료

도출한 루트는 실제 존재 여부를 확인한다 (`ls <brain-root>`).

### Step 4: drop 위치 런타임 발견 (경로 가정 금지)

brain 의 raw/ 하위 구조는 그때그때 바뀔 수 있으므로 **고정 경로를 가정하지 않는다**:

1. `ls <brain-root>/raw/` 로 현재 1차 폴더 구조 확인 (예: work / learning / interest)
2. 작업 성격에 맞는 폴더 아래에서 동일 프로젝트 서브폴더가 이미 있는지 확인
   (예: `raw/work/<project-slug>/` — 있으면 재사용, 없으면 생성 제안)
3. 최종 drop 경로를 사용자에게 제시하고 **확인 후** 진행

### Step 5: 회고 리포트 작성

파일명: `<drop-path>/YYYY-MM-DD-<slug>-retrospective.md`

리포트 구조 (plan.md + handoff.md + 커밋을 증류 — 복붙 금지):

```markdown
# <프로젝트/작업명> 회고 리포트

- 기간: <시작일> ~ <종료일>
- 대상 repo: <repo 경로 또는 이름>
- archive: workspace/archive/{N}_{slug}/

## 목표
(plan.md 의 요구사항 요약 2~4줄)

## 결과
(Phase·Task 별 완료 내역 — 무엇이 만들어졌는지)

## 주요 설계 결정
(handoff.md 의 결정 사항 — 왜 그렇게 했는지 포함)

## 교훈 · 재발 방지
(막혔던 지점, 다시 하면 다르게 할 것, 함정)

## 커밋 히스토리 요약
(주요 커밋 5~15개 — hash + 한 줄 설명)

## 다음 액션 후보
(후속 작업·개선 아이디어 — 없으면 "없음")
```

**작성 전 초안을 사용자에게 보여주고 확인받는다** — 다른 repo(brain)에 쓰는 작업이므로 반드시 승인 후 Write.

### Step 6: 완료 안내

```
✅ 회고 리포트 생성 완료

경로: <brain-root>/raw/.../<파일명>

다음 단계 (brain 세션에서):
  /ingest 실행 → 새 파일로 자동 감지되어 요약·인터뷰·wiki 반영이 진행됩니다.
```

## 주의사항

- 🔒 brain 의 기존 파일은 **일절 수정하지 않는다** — 이 스킬은 raw/ 에 새 파일 1개 추가만 한다
- 🔒 wiki/ 디렉토리는 건드리지 않는다 — wiki 반영은 `/ingest` 의 책임 (요약→인터뷰→scope 분류 규율 유지)
- 🔒 `workspace/archive/` 안의 파일은 읽기만 한다 (불변 원칙)
- 리포트는 증류본이다 — plan.md/handoff.md 원문 복붙 금지, 핵심만 구조화
- 같은 archive 에 대한 리포트가 이미 존재하면 (파일명 grep) 덮어쓰기 전 사용자 확인

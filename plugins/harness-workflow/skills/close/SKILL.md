---
name: close
description: "workspace/ 의 작업이 완료되었을 때 plan.md + handoff.md 를 archive/ 로 이동하고 brain 아카이빙을 안내하는 스킬.
  '작업 완료', '클로즈', 'close', '아카이브해줘', '다 끝났어' 등을 요청할 때 사용한다."
---

# /close — 작업 완료 + archive 이동

`workspace/plan.md` + `workspace/handoff.md` 를 `workspace/archive/{N}_{slug}/` 로 이동하고
brain 아카이빙 경로를 안내한다.

## 전제 조건

- 현재 작업 디렉토리가 대상 프로젝트 루트
- `workspace/plan.md` 가 존재

## 워크플로우

### Step 1: 완료 여부 확인

`workspace/plan.md` 의 모든 Task 체크박스(`- [x]`)를 확인한다.
미완료 Task(`- [ ]`) 가 있으면:
→ "아직 완료되지 않은 Task {N}건이 있습니다. 그래도 close 할까요?" 확인

### Step 2: archive 번호 결정

`workspace/archive/` 의 기존 폴더 수를 확인해 다음 번호를 결정한다.
- 비어있으면 `1_`
- `1_*` 있으면 `2_`
- N개 있으면 `{N+1}_`

### Step 3: slug 확인

`workspace/plan.md` 의 `project name` 필드에서 slug를 가져온다.
없으면 사용자에게 확인.

### Step 4: archive 이동

`workspace/archive/{N}_{slug}/` 폴더 생성 후
`workspace/plan.md`, `workspace/handoff.md` 를 해당 폴더로 이동.

### Step 5: handoff 최종 업데이트

이동 전 `handoff.md` 의 `마지막 수정일` 과 `완료 Phase` 를 업데이트한다.

### Step 6: brain 아카이빙 안내

```
✅ archive 완료

이동 경로: workspace/archive/{N}_{slug}/

brain 아카이빙 (선택):
  의미 있는 결정이나 교훈은 brain 에 기록을 권장합니다.
  - 중요 설계 결정 → brain/wiki/analyses/ 또는 concepts/
  - 재발 방지 사항 → brain 운영자에게 ingest 요청

workspace/ 상태:
  plan.md, handoff.md 이동 완료.
  다음 작업 시 /plan 으로 새로 시작하세요.
```

## 주의사항

- archive 이동 전 반드시 사용자 최종 확인
- `workspace/archive/` 안의 파일은 수정하지 않는다 (불변 원칙)

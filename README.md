# juno agent skills

개인용 Claude Code Agent 및 Skill 모음 저장소입니다.

이 저장소는 Claude Code의 **플러그인 마켓플레이스(Plugin Marketplace)** 규격에 맞춰 구성되어 있습니다.
(`.claude-plugin/marketplace.json` 및 `plugins/*` 폴더 구조)

---

## 📦 포함된 플러그인

### 1. [harness-workflow](./plugins/harness-workflow)
프로젝트 로컬 `workspace/` 디렉토리를 기반으로 개발 사이클을 자동화하는 하네스(Harness) 워크플로우 플러그인입니다.
**plan → TDD (test-coder/coder/verifier) → close → brain-report** 흐름을 강제하여 안정적인 코드 작성을 돕습니다.

*   **포함된 Skill**
    *   `/plan`: 요구사항을 분석하여 `workspace/` 디렉토리를 초기화하고 개발 계획(`plan.md`)을 작성합니다.
    *   `/work`: `plan.md`에 명시된 Task를 순차적으로 1개씩 TDD 사이클(Red ➔ Green ➔ Verify ➔ Refactor)로 자동 진행하며, 단계별 커밋(Test, Code, Refactor)을 수행합니다.
    *   `/close`: 작업이 완료되면 `workspace/` 내 작업 파일을 `archive/` 폴더로 보관 및 관리하고 회고 작성을 유도합니다.
    *   `/brain-report`: 완료된 작업 히스토리를 요약하여 세컨드 브레인(Second Brain)인 `brain`의 `raw/` 경로로 리포트를 전달합니다.
*   **포함된 Agent**
    *   `test-coder`: Red 단계에서 실패하는 테스트 코드를 작성합니다.
    *   `coder`: Green 단계에서 테스트를 통과하기 위한 최소한의 기능 코드를 작성합니다.
    *   `verifier`: 구현 코드를 검증하고 Read-only 리포트를 작성합니다.

> [!NOTE]
> `harness-workflow` 의 Refactor 단계에서는 Claude Code 내장 `simplify` skill을 사용하므로, 추가적인 설치가 필요하지 않습니다.

---

## 📂 저장소 구조

```text
juno-agent-skills/
├── .claude-plugin/
│   └── marketplace.json       # 마켓플레이스 메타데이터 설정 파일
├── plugins/
│   └── harness-workflow/      # Harness Workflow 플러그인 폴더
│       ├── README.md          # 플러그인 상세 적용 가이드
│       ├── agents/            # 플러그인 전용 Agent 정의 (coder, test-coder, verifier)
│       └── skills/            # 플러그인 전용 Skill 정의 (plan, work, close, brain-report)
└── README.md                  # 본 가이드 파일
```

---

## 🚀 설치 방법

Claude Code 터미널 세션 내부에서 다음 슬래시 명령어를 실행하여 마켓플레이스를 추가하고 플러그인을 설치합니다.

### 1) 마켓플레이스 추가

*   **원격(GitHub) 저장소로 추가:**
    ```bash
    /plugin marketplace add juno-choi/juno-agent-skills
    ```

*   **로컬 디렉토리 경로로 추가** (로컬에서 개발 및 테스트 시 유용):
    ```bash
    /plugin marketplace add /path/to/juno-agent-skills
    ```

### 2) 플러그인 설치

```bash
/plugin install harness-workflow@juno-agent-skills
```

또는 인터랙티브 GUI 메뉴를 통해 설치할 수 있습니다:
```bash
/plugin
```
➔ `Browse marketplaces` ➔ `juno-agent-skills` 선택 ➔ `harness-workflow` 플러그인 선택 ➔ `Install` 실행.

### 3) 설치 확인

```bash
/plugin marketplace list
/plugin
```
설치된 플러그인 목록에 `harness-workflow`가 정상적으로 표시되는지 확인합니다.

---

## 🔄 업데이트 및 삭제

*   **마켓플레이스 최신화 (업데이트):**
    ```bash
    /plugin marketplace update juno-agent-skills
    ```
*   **플러그인 제거 (삭제):**
    ```bash
    /plugin uninstall harness-workflow
    ```
*   **마켓플레이스 등록 해제:**
    ```bash
    /plugin marketplace remove juno-agent-skills
    ```

---

## 💡 참고 사항

> [!IMPORTANT]
> 로컬 디렉토리 경로와 GitHub 원격 경로를 동시에 등록할 경우 마켓플레이스 이름(`juno-agent-skills`)이 충돌할 수 있으므로, 반드시 하나의 방식만 선택하여 사용해 주세요.

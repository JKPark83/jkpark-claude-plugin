# 출처와 라이선스

obs-html의 다이어그램 규칙, 페이지 템플릿, 검증 절차는 아래 공개 스킬을 참고해 만들었다.
오프라인에서 보는 한국어 Obsidian 문서에 맞게 옮기고 줄였다. 원본 코드를 그대로 복사하지 않았고,
원본이 쓰는 CDN(Mermaid·Chart.js·웹폰트)도 쓰지 않는다.

| 원본 | 라이선스 | 가져온 것 |
|---|---|---|
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | MIT | 편집형 다이어그램 철학, 노드 종류 위계, 커넥터 규칙, 복잡도 예산, 안티패턴 → `diagram-design.md` |
| [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) | MIT | 반응형 목차·스크롤 스파이, 넘침 방지, 비교 패널·접기 패턴 → `html-template.md`, `assets/template.html` |
| [anthropics/skills — frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | Apache-2.0 | 먼저 설계하고 나중에 비평하는 흐름, AI 티 목록 → `html-template.md` |
| [ferdinandobons/diagram-creator-skill](https://github.com/ferdinandobons/diagram-creator-skill) | — | 다이어그램 타입 선택 아이디어 일부 |

한글 라벨 폭 산식, `check_html.py`, `snap.sh`는 이 저장소에서 새로 작성했다.

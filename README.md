# 연속실험 근무 스케줄 (10/11 11:00 ~ 10/19 18:00)

- `roster.html` — 웹 페이지 원본: 불가 시간 제출 / 근무표 / 관리(소유자만) 탭. 그룹(A/B/C)은 소유자만 읽을 수 있는 저장소(`admin/groups`)에만 있고 참가자 화면·공개 근무표에는 나오지 않음
  - 게시 주소: https://claude.ai/artifact/Uw5CQUFMgYBG899HzYeVYV (관리 탭 바로가기: `#admin`, 근무표: `#schedule`)
- `schedule.py` — 같은 배치 규칙을 쓰는 오프라인 생성기. `UNAVAILABLE`을 채우고 `python3 schedule.py` 실행 → `schedule.md`, `schedule.csv`

배치 규칙: 각 조는 A 1명 + B/C 1명, 불가 시간 제외, 최소 휴식 16시간,
근무 횟수·시간·새벽·밤 횟수를 고르게 나누고, 같은 짝은 되도록 반복하지 않으며 B/C가 번갈아 들어감.

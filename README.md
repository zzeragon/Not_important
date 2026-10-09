# 연속실험 근무 스케줄 (10/11 11:00 ~ 10/19 18:00)

- `roster.html` — 웹 페이지 원본: 불가 시간 제출 / 근무표 / 관리(소유자만) 탭. 그룹(A/B/C)은 소유자만 읽을 수 있는 저장소(`admin/groups`)에만 있고 참가자 화면·공개 근무표에는 나오지 않음
  - 게시 주소: https://claude.ai/artifact/Uw5CQUFMgYBG899HzYeVYV (관리 탭 바로가기: `#admin`, 근무표: `#schedule`)
- `schedule.py` — 같은 배치 규칙을 쓰는 오프라인 생성기. `UNAVAILABLE`을 채우고 `python3 schedule.py` 실행 → `schedule.md`, `schedule.csv`

배치 규칙: 각 조는 A 1명 + B/C 1명, 불가 시간 제외, 최소 휴식 16시간,
근무 횟수·시간·새벽·밤 횟수를 고르게 나누고, 같은 짝은 되도록 반복하지 않으며 B/C가 번갈아 들어감.

## 오프라인 방식 (로그인 불필요)
- `offline/불가시간_조사.html` — 참가자에게 보내는 파일. 이름·불가 시간을 고르면 `AVAIL:` 코드가 담긴 결과를 복사하거나 .txt로 저장
- `offline/근무표_관리.html` — 관리자 전용(그룹 정보 포함). 받은 메시지/파일을 넣고 자동 배치·수정·카톡용 복사·CSV·백업
- 두 파일은 `python3 offline/src/build.py` 로 `roster.html`의 스타일·배치 엔진을 넣어 생성

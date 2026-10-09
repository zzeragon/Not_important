"""연속실험 근무 스케줄 생성기.

- 실험기간: 2026-10-11(일) 11:00 ~ 2026-10-19(월) 18:00
- 근무조: 낮(09:00~18:00), 밤(18:00~01:30), 새벽(01:30~09:00)
- 2인 1조: A그룹 1명 + (B그룹 또는 C그룹) 1명

개인 일정은 UNAVAILABLE 에 적고 `python3 schedule.py` 를 다시 실행하면
schedule.md / schedule.csv 가 새로 만들어진다.
"""

import csv
import math
import random
from collections import Counter
from datetime import datetime, timedelta

START = datetime(2026, 10, 11, 11, 0)
END = datetime(2026, 10, 19, 18, 0)

GROUP_A = ["이동근", "이상호", "박진영", "김영상", "장형준"]
GROUP_B = ["뚜안앵", "린", "김소연", "박찬수"]
GROUP_C = ["김용국", "신우찬", "이민준", "앵덕"]

# 근무 불가 시간: 이름 -> [(시작, 끝), ...]  ("MM-DD HH:MM" 형식)
# 해당 시간과 조금이라도 겹치는 근무조에는 배정되지 않는다.
# 예) "김소연": [("10-13 09:00", "10-13 18:00")],
UNAVAILABLE = {
}

# 한 사람의 근무 사이 최소 휴식 시간(시간)
MIN_REST_HOURS = 16

SEED = 2026
ITERATIONS = 200_000

WEEKDAYS = "월화수목금토일"


def parse(s):
    return datetime.strptime(f"{START.year}-{s}", "%Y-%m-%d %H:%M")


def build_shifts():
    """(이름, 시작, 끝) 목록. 실험 시작/종료 시각에 맞춰 첫·마지막 조를 자른다."""
    shifts = []
    day = START.replace(hour=0, minute=0) - timedelta(days=1)
    while day <= END:
        for name, s, e in (("새벽", (1, 30), (9, 0)), ("낮", (9, 0), (18, 0)),
                           ("밤", (18, 0), (25, 30))):
            st = day + timedelta(hours=s[0], minutes=s[1])
            en = day + timedelta(hours=e[0], minutes=e[1])
            st, en = max(st, START), min(en, END)
            if st < en:
                shifts.append((name, st, en))
        day += timedelta(days=1)
    return shifts


SHIFTS = build_shifts()
PARTNERS = GROUP_B + GROUP_C
N = len(SHIFTS)


def blocked(person, i):
    _, st, en = SHIFTS[i]
    return any(parse(a) < en and st < parse(b) for a, b in UNAVAILABLE.get(person, []))


def hours(i):
    return (SHIFTS[i][2] - SHIFTS[i][1]).total_seconds() / 3600


def cost(a_sched, p_sched):
    c = 0.0
    for sched, people in ((a_sched, GROUP_A), (p_sched, PARTNERS)):
        for i, p in enumerate(sched):
            if blocked(p, i):
                c += 1e6
        last = {}
        for i, p in enumerate(sched):
            if p in last:
                rest = (SHIFTS[i][1] - SHIFTS[last[p]][2]).total_seconds() / 3600
                if rest < MIN_REST_HOURS:
                    c += 1e5
            last[p] = i
        # 인원별 근무 횟수 / 시간 / 새벽조 / 밤조 균등
        cnt = Counter(sched)
        hrs = Counter()
        dawn = Counter()
        night = Counter()
        for i, p in enumerate(sched):
            hrs[p] += hours(i)
            if SHIFTS[i][0] == "새벽":
                dawn[p] += 1
            elif SHIFTS[i][0] == "밤":
                night[p] += 1
        for metric, w in ((cnt, 1000), (hrs, 10), (dawn, 200), (night, 100)):
            mean = sum(metric.values()) / len(people)
            c += w * sum((metric[p] - mean) ** 2 for p in people)
    # 같은 짝 반복 최소화
    pairs = Counter(zip(a_sched, p_sched))
    c += 50 * sum(v - 1 for v in pairs.values() if v > 1)
    # B조/C조가 번갈아 들어가도록
    for i in range(1, N):
        if (p_sched[i] in GROUP_B) == (p_sched[i - 1] in GROUP_B):
            c += 5
    return c


def initial():
    # 순환 배치: 차단·휴식 조건이 없으면 이것만으로도 거의 최적
    a = [GROUP_A[i % len(GROUP_A)] for i in range(N)]
    order = [x for pair in zip(GROUP_B, GROUP_C) for x in pair]
    p = [order[i % len(order)] for i in range(N)]
    return a, p


def solve():
    rng = random.Random(SEED)
    a, p = initial()
    cur = cost(a, p)
    best = (cur, a[:], p[:])
    temp0 = 500.0
    for it in range(ITERATIONS):
        temp = temp0 * (1 - it / ITERATIONS) + 1e-3
        sched, people = (a, GROUP_A) if rng.random() < 0.5 else (p, PARTNERS)
        i = rng.randrange(N)
        if rng.random() < 0.5:
            j = rng.randrange(N)
            sched[i], sched[j] = sched[j], sched[i]
            undo = (lambda s=sched, x=i, y=j: s.__setitem__(
                slice(None), _swap(s, x, y)))
        else:
            old = sched[i]
            sched[i] = rng.choice(people)
            undo = (lambda s=sched, k=i, v=old: s.__setitem__(k, v))
        new = cost(a, p)
        if new <= cur or rng.random() < math.exp((cur - new) / temp):
            cur = new
            if cur < best[0]:
                best = (cur, a[:], p[:])
        else:
            undo()
    return best


def _swap(s, i, j):
    t = s[:]
    t[i], t[j] = t[j], t[i]
    return t


def fmt(dt):
    return f"{dt.month}/{dt.day}({WEEKDAYS[dt.weekday()]}) {dt:%H:%M}"


def group_of(p):
    return "A" if p in GROUP_A else "B" if p in GROUP_B else "C"


def write(a, p, score):
    rows = []
    for i, (name, st, en) in enumerate(SHIFTS):
        rows.append([i + 1, name, fmt(st), fmt(en), f"{hours(i):g}",
                     a[i], p[i], f"A+{group_of(p[i])}"])

    with open("schedule.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["#", "조", "시작", "종료", "시간", "A그룹", "B/C그룹", "조합"])
        w.writerows(rows)

    lines = ["# 연속실험 근무 스케줄", "",
             f"- 기간: {fmt(START)} ~ {fmt(END)}",
             "- 근무조: 낮 09:00~18:00 / 밤 18:00~01:30 / 새벽 01:30~09:00",
             f"- 최소 휴식: {MIN_REST_HOURS}시간", ""]
    if score >= 1e5:
        lines += ["> ⚠️ 모든 조건을 만족하는 배치를 찾지 못했습니다. "
                  "근무 불가 시간 또는 MIN_REST_HOURS 를 확인하세요.", ""]
    lines += ["## 근무표", "",
              "| # | 조 | 시작 | 종료 | 시간 | A그룹 | B/C그룹 | 조합 |",
              "|---|---|---|---|---|---|---|---|"]
    lines += ["| " + " | ".join(map(str, r)) + " |" for r in rows]

    lines += ["", "## 개인별 요약", "",
              "| 이름 | 그룹 | 횟수 | 총 시간 | 낮 | 밤 | 새벽 | 근무 일정 |",
              "|---|---|---|---|---|---|---|---|"]
    for person in GROUP_A + PARTNERS:
        sched = a if person in GROUP_A else p
        idx = [i for i, x in enumerate(sched) if x == person]
        kinds = Counter(SHIFTS[i][0] for i in idx)
        when = ", ".join(f"{SHIFTS[i][1].month}/{SHIFTS[i][1].day} {SHIFTS[i][0]}"
                         for i in idx)
        lines.append(f"| {person} | {group_of(person)} | {len(idx)} | "
                     f"{sum(hours(i) for i in idx):g} | {kinds['낮']} | "
                     f"{kinds['밤']} | {kinds['새벽']} | {when} |")

    with open("schedule.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    score, a, p = solve()
    write(a, p, score)

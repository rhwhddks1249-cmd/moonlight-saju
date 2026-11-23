# -*- coding: utf-8 -*-
"""연애운 / 궁합: today_fortune.py 의 십성 구조를 재사용한다."""
import datetime
import hashlib
from today_fortune import (STEMS, ELEMENTS, normalize_stem,
                           ten_god, day_pillar)

# 천간합: 갑기, 을경, 병신, 정임, 무계
STEM_HAP = {(0, 5), (1, 6), (2, 7), (3, 8), (4, 9)}
# 오행 상생(목화토금수 순서) / 상극
def _elem_rel(a, b):
    d = (b - a) % 5
    return {0: "같은 기운", 1: "내가 생하는 관계", 4: "나를 생하는 관계",
            2: "내가 극하는 관계", 3: "나를 극하는 관계"}[d]

LOVE_GODS = {"남": ("정재", "편재"), "여": ("정관", "편관")}

def _hash(*parts):
    return hashlib.sha256("|".join(map(str, parts)).encode()).digest()[0]

def love_today(day_stem, gender, today=None):
    me = normalize_stem(day_stem)
    if me is None:
        raise ValueError("일간을 확인할 수 없습니다.")
    d = today or datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))).date()
    _, s_idx, _ = day_pillar(d)
    god = ten_god(me, s_idx)
    score = 3
    if god in LOVE_GODS.get(gender, ()):
        score += 1
    if tuple(sorted((me, s_idx))) in STEM_HAP:
        score += 1
    score = max(1, min(5, score + (_hash(STEMS[me], d.isoformat()) % 3) - 1))
    return {"date": d.isoformat(), "ten_god": god, "stars": score}

def compatibility(stem_a, stem_b):
    a, b = normalize_stem(stem_a), normalize_stem(stem_b)
    if a is None or b is None:
        raise ValueError("일간을 확인할 수 없습니다.")
    score = 60
    hap = tuple(sorted((a, b))) in STEM_HAP
    rel = _elem_rel(a // 2, b // 2)
    if hap:
        score += 25
    if rel in ("나를 생하는 관계", "내가 생하는 관계"):
        score += 15
    elif rel == "같은 기운":
        score += 5
    elif rel == "나를 극하는 관계":
        score -= 10
    return {
        "a": STEMS[a], "b": STEMS[b],
        "a_to_b": ten_god(a, b), "b_to_a": ten_god(b, a),
        "element_relation": rel,
        "stem_hap": hap,
        "score": max(30, min(100, score)),
    }
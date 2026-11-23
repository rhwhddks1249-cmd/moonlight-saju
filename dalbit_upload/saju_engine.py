# -*- coding: utf-8 -*-
"""
saju_engine.py
정밀 만세력 천문 절기 계산 및 사주팔자 심층 분석 엔진
- 12절기 절입시각(Jean Meeus 천문 알고리즘) 정밀 계산
- 년주, 월주(절기 기준), 일주(율리우스일), 시주(조자시/야자시 보정) 산출
- 십성(육친), 오행 점수 분포, 신강·신약 판별
- 억부/조후 용신 및 희신, 기신 도출
- 대운(순행/역행, 대운수, 10년 주기 간지) 산출
- 당해 세운(올해 세운) 분석
- 음력/양력 상호 변환 지원 (korean_lunar_calendar 연동)
"""

import math
import datetime
from korean_lunar_calendar import KoreanLunarCalendar

# 10천간
GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
GAN_KR = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
# 오행: 목(0), 목(0), 화(1), 화(1), 토(2), 토(2), 금(3), 금(3), 수(4), 수(4)
GAN_ELEM = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
GAN_ELEM_NAME = ['목', '목', '화', '화', '토', '토', '금', '금', '수', '수']
# 음양 (+1: 양, -1: 음)
GAN_YIN_YANG = [1, -1, 1, -1, 1, -1, 1, -1, 1, -1]

# 12지지
JI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
JI_KR = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']
# 본기(정기) 천간 인덱스
# 子(癸:9), 丑(己:5), 寅(甲:0), 卯(乙:1), 辰(戊:4), 巳(丙:2), 午(丁:3), 未(己:5), 申(庚:6), 酉(辛:7), 戌(戊:4), 亥(壬:8)
JI_MAIN_GAN = [9, 5, 0, 1, 4, 2, 3, 5, 6, 7, 4, 8]
JI_ELEM = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4] # 수, 토, 목, 목, 토, 화, 화, 토, 금, 금, 토, 수
JI_ELEM_NAME = ['수', '토', '목', '목', '토', '화', '화', '토', '금', '금', '토', '수']
JI_YIN_YANG = [-1, -1, 1, -1, 1, 1, -1, -1, 1, -1, 1, 1]

# 지장간 (여기, 중기, 정기)
# (간_idx, 일수)
HIDDEN_GANS = {
    0: [('壬', '임', 8, 10), ('癸', '계', 9, 20)],                               # 子: 임10 계20
    1: [('癸', '계', 9, 9),  ('辛', '신', 7, 3),  ('己', '기', 5, 18)],        # 丑: 계9 신3 기18
    2: [('戊', '무', 4, 7),  ('丙', '병', 2, 7),  ('甲', '갑', 0, 16)],        # 寅: 무7 병7 갑16
    3: [('甲', '갑', 0, 10), ('乙', '을', 1, 20)],                               # 卯: 갑10 을20
    4: [('乙', '을', 1, 9),  ('癸', '계', 9, 3),  ('戊', '무', 4, 18)],        # 辰: 을9 계3 무18
    5: [('戊', '무', 4, 7),  ('庚', '경', 6, 7),  ('丙', '병', 2, 16)],        # 巳: 무7 경7 병16
    6: [('丙', '병', 2, 10), ('己', '기', 5, 9),  ('丁', '정', 3, 11)],        # 午: 병10 기9 정11
    7: [('丁', '정', 3, 9),  ('乙', '을', 1, 3),  ('己', '기', 5, 18)],        # 未: 정9 을3 기18
    8: [('戊', '무', 4, 7),  ('壬', '임', 8, 7),  ('庚', '경', 6, 16)],        # 申: 무7 임7 경16
    9: [('庚', '경', 6, 10), ('辛', '신', 7, 20)],                               # 酉: 경10 신20
    10: [('辛', '신', 7, 9), ('丁', '정', 3, 3),  ('戊', '무', 4, 18)],        # 戌: 신9 정3 무18
    11: [('戊', '무', 4, 7), ('甲', '갑', 0, 7),  ('壬', '임', 8, 16)]         # 亥: 무7 갑7 임16
}

# 12운성 명칭
UNSUNG_NAMES = ['장생', '목욕', '관대', '건록', '제왕', '쇠', '병', '사', '묘', '절', '태', '양']
# 10천간 장생 위치 (시작 지지 idx, 방향 +1순행/-1역행)
CHANG_SAENG = {
    0: (11, 1),   # 甲: 亥(11), +1
    1: (6, -1),   # 乙: 午(6), -1
    2: (2, 1),    # 丙: 寅(2), +1
    3: (9, -1),   # 丁: 酉(9), -1
    4: (2, 1),    # 戊: 寅(2), +1
    5: (9, -1),   # 己: 酉(9), -1
    6: (5, 1),    # 庚: 巳(5), +1
    7: (0, -1),   # 辛: 子(0), -1
    8: (8, 1),    # 壬: 申(8), +1
    9: (3, -1),   # 癸: 卯(3), -1
}

ELEMENT_NAMES = ['목', '화', '토', '금', '수']
ELEMENT_HANJA = ['木', '火', '土', '金', '水']
ELEMENT_COLORS = {
    '목': {'name': '청(靑)', 'color': '#22c55e', 'bg': 'rgba(34, 197, 94, 0.15)', 'border': '#16a34a'},
    '화': {'name': '적(赤)', 'color': '#ef4444', 'bg': 'rgba(239, 68, 68, 0.15)', 'border': '#dc2626'},
    '토': {'name': '황(黃)', 'color': '#eab308', 'bg': 'rgba(234, 179, 8, 0.15)', 'border': '#ca8a04'},
    '금': {'name': '백(白)', 'color': '#94a3b8', 'bg': 'rgba(148, 163, 184, 0.15)', 'border': '#cbd5e1'},
    '수': {'name': '흑(黑)', 'color': '#3b82f6', 'bg': 'rgba(59, 130, 246, 0.15)', 'border': '#2563eb'}
}

# 60갑자 일주론 데이터 (대표 특성 요약)
ILJU_DATA = {
    '甲子': {'title': '지혜와 자존심이 돋보이는 푸른 쥐', 'char': '총명하고 인정이 많으나 내면의 고집과 학구열이 강하며 명예를 중시합니다.'},
    '甲戌': {'title': '신뢰와 실속을 중시하는 푸른 개', 'char': '책임감이 강하고 활동적이며 재물 관리에 능하고 리더십이 뛰어납니다.'},
    '甲申': {'title': '재주와 결단력이 넘치는 푸른 원숭이', 'char': '두뇌 회전이 빠르고 결단력이 있으며 개혁적인 성향을 보입니다.'},
    '甲午': {'title': '열정과 추진력의 푸른 말', 'char': '화려한 재능과 언변을 지녔으며 직관력이 뛰어나고 진취적입니다.'},
    '甲辰': {'title': '포부와 배포가 당당한 푸른 용', 'char': '스케일이 크고 독립심이 강하며 현실적인 성취욕이 매우 높습니다.'},
    '甲寅': {'title': '당당한 기상과 우직함의 푸른 호랑이', 'char': '자존심과 뚝심이 있으며 남에게 굽히지 않는 대장부의 기질을 가집니다.'},

    '乙丑': {'title': '인내와 근면으로 자수성가하는 소', 'char': '어려운 환경에서도 끈기 있게 꽃을 피워내는 강한 생활력의 소유자입니다.'},
    '乙亥': {'title': '감수성과 예술성이 풍부한 돼지', 'char': '정이 많고 지혜로우며 타인을 배려하는 따뜻함과 예술적 감각이 돋보입니다.'},
    '乙酉': {'title': '섬세하고 예리한 감각의 닭', 'char': '정확하고 원칙적이며 내면에 단단한 칼을 품은 듯한 집중력이 있습니다.'},
    '乙未': {'title': '다정다감하고 실속 있는 양', 'char': '사교적이고 친화력이 뛰어나며 현실적인 안정을 추구하는 실속파입니다.'},
    '乙巳': {'title': '화려한 매력과 사교성의 뱀', 'char': '표현력이 풍부하고 매력적이며 사람의 마음을 사로잡는 재치가 있습니다.'},
    '乙卯': {'title': '생명력과 친화력의 토끼', 'char': '유연하면서도 외유내강형으로 자신만의 영역을 꾸준히 넓혀갑니다.'},

    '丙子': {'title': '밝고 단정한 빛의 쥐', 'char': '예의 바르고 공명정대하며 맑은 영감과 감수성을 지니고 있습니다.'},
    '丙戌': {'title': '신의와 충직함의 붉은 개', 'char': '따뜻한 마음과 의리를 지녔으며 다재다능하고 정열적으로 일에 몰두합니다.'},
    '丙申': {'title': '기민하고 다재다능한 붉은 원숭이', 'char': '센스가 넘치고 수완이 좋으며 재물운과 사교운이 활발합니다.'},
    '丙午': {'title': '태양처럼 강렬한 에너지를 뿜는 말', 'char': '극도의 열정과 카리스마를 지녔으며 솔직담백하고 폭발적인 추진력이 있습니다.'},
    '丙辰': {'title': '너그러운 도량과 변화무쌍한 용', 'char': '포용력이 넓고 지혜로우며 새로운 분야에 도전하는 열망이 큽니다.'},
    '丙寅': {'title': '희망과 생기를 불어넣는 붉은 호랑이', 'char': '순수하고 진취적이며 주변 사람들에게 활력과 영감을 주는 리더입니다.'},

    '丁丑': {'title': '은은한 촛불처럼 따뜻한 소', 'char': '신중하고 묵묵히 헌신하며 실속과 안정을 차곡차곡 쌓아 올립니다.'},
    '丁亥': {'title': '온화하고 귀티가 흐르는 돼지', 'char': '성품이 곧고 바르며 대인관계가 원만하고 천을귀인의 복록이 깃듭니다.'},
    '丁酉': {'title': '정밀한 안목과 귀금속의 닭', 'char': '미적 감각이 탁월하고 결단력이 빠르며 경제적 감각이 매우 발달했습니다.'},
    '丁未': {'title': '따뜻한 온기와 은근한 고집의 양', 'char': '다정하지만 속으로는 굳은 신념을 지니고 한 우물을 깊이 팝니다.'},
    '丁巳': {'title': '열정과 집념으로 타오르는 뱀', 'char': '목표를 향해 거침없이 전진하며 뚝심과 승부욕이 대단히 강합니다.'},
    '丁卯': {'title': '섬세한 손재주와 학문의 토끼', 'char': '상상력과 아이디어가 풍부하며 감성적이고 감각적인 영역에 능합니다.'},

    '戊子': {'title': '묵직한 산속의 옹달샘을 품은 쥐', 'char': '겉은 묵직하나 속은 셈이 밝고 알뜰하며 은근한 재복을 누립니다.'},
    '戊戌': {'title': '거대한 산맥의 웅장함을 지닌 개', 'char': '신의와 정직의 대명사로 타인에게 깊은 신뢰감을 주는 큰 그릇입니다.'},
    '戊申': {'title': '재주와 낙천성을 겸비한 원숭이', 'char': '성격이 원만하고 식견이 넓으며 다재다능하여 어디서나 환영받습니다.'},
    '戊午': {'title': '화산처럼 웅장한 기개의 말', 'char': '강한 자존심과 주관을 가졌으며 한번 결심한 일은 끝까지 밀어붙입니다.'},
    '戊辰': {'title': '생명력을 품은 드넓은 평원의 용', 'char': '대범하고 끈기가 있으며 현실적인 안목과 경영 능력이 탁월합니다.'},
    '戊寅': {'title': '위엄과 용맹의 황금 호랑이', 'char': '카리스마와 리더십이 뛰어나며 조직이나 집단을 이끄는 데 천부적입니다.'},

    '己丑': {'title': '기름진 옥토처럼 비옥한 소', 'char': '성실하고 끈기 있으며 묵묵히 자신의 길을 걸어가 큰 결실을 맺습니다.'},
    '己亥': {'title': '순수함과 지혜를 품은 돼지', 'char': '성격이 부드럽고 유연하며 타인과의 융합력이 뛰어나고 복이 많습니다.'},
    '己酉': {'title': '정갈하고 명민한 황금 닭', 'char': '깔끔하고 청결하며 자기 관리가 철저하고 손재주나 말솜씨가 좋습니다.'},
    '己未': {'title': '뚝심과 자립심이 돋보이는 양', 'char': '고집과 자존심이 세지만 한번 맺은 인연을 소중히 지키는 충성파입니다.'},
    '己巳': {'title': '총명함과 열정이 깃든 뱀', 'char': '지적 호기심이 왕성하고 수완이 좋으며 변화에 대처하는 능력이 뛰어납니다.'},
    '己卯': {'title': '예민하고 섬세한 감각의 토끼', 'char': '직관력이 발달했고 눈치가 빠르며 예술이나 기획 분야에서 두각을 보입니다.'},

    '庚子': {'title': '맑은 물에 씻긴 백색 원석의 쥐', 'char': '두뇌가 명석하고 언변이 뛰어나며 비판적 안목과 예술성이 훌륭합니다.'},
    '庚戌': {'title': '강직한 정의감의 하얀 개', 'char': '의리가 넘치고 불의를 참지 못하며 괴강의 강력한 추진력을 발휘합니다.'},
    '庚申': {'title': '단단한 쇠처럼 굴하지 않는 원숭이', 'char': '자신감과 배포가 당당하며 강한 자립심으로 스스로 운명을 개척합니다.'},
    '庚午': {'title': '단련된 명검의 백마', 'char': '예의 바르고 품격이 있으며 조직 내에서 규율과 명예를 중시합니다.'},
    '庚辰': {'title': '변혁과 영웅적 기상의 하얀 용', 'char': '포부가 원대하고 카리스마가 넘치며 큰 역경도 당당히 돌파해 냅니다.'},
    '庚寅': {'title': '진취적이고 결단력 있는 백호', 'char': '역마의 기운으로 분주히 움직이며 현실적인 재물 감각과 결단력이 돋보입니다.'},

    '辛丑': {'title': '흙 속에서 갈고닦은 보석의 소', 'char': '인내심과 집중력이 대단하며 묵묵히 실력을 갈고닦아 만개하는 대기만성형입니다.'},
    '辛亥': {'title': '맑은 물에 씻긴 눈부신 보석의 돼지', 'char': '지혜롭고 다정다감하며 말과 표현에 세련미가 넘쳐 인기가 많습니다.'},
    '辛酉': {'title': '결벽에 가까운 순수함과 예리한 보석의 닭', 'char': '깔끔하고 자존심이 대단히 높으며 완벽주의적 성향으로 전문성을 이룹니다.'},
    '辛未': {'title': '온화함 속에 단단함을 감춘 양', 'char': '차분하고 정중하지만 내면에는 날카로운 분별력과 자립심을 품고 있습니다.'},
    '辛巳': {'title': '빛나는 광채와 품격의 뱀', 'char': '단정하고 품위가 있으며 공사 구분이 확실하고 처세술이 뛰어납니다.'},
    '辛卯': {'title': '섬세한 감수성과 순발력의 토끼', 'char': '손재주가 좋고 감각이 예민하며 부지런히 움직여 재물을 취하는 민첩함이 있습니다.'},

    '壬子': {'title': '광활한 대해의 도도한 기상을 지닌 쥐', 'char': '스케일이 크고 지혜가 깊으며 양인(羊刃)의 강한 카리스마와 주관을 지닙니다.'},
    '壬戌': {'title': '충직하고 포용력 넓은 검은 개', 'char': '신중하고 믿음직스러우며 풍부한 상식과 깊은 속내를 지닌 실속파입니다.'},
    '壬申': {'title': '샘솟는 지혜와 다재다능한 원숭이', 'char': '임기응변이 뛰어나고 학문과 예술에 재능이 있으며 모방과 응용에 능합니다.'},
    '壬午': {'title': '열정과 지혜가 교차하는 흑마', 'char': '감성이 풍부하고 예의가 바르며 비밀이 없고 재물운과 연애운이 순탄합니다.'},
    '壬辰': {'title': '깊은 바다를 다스리는 흑룡', 'char': '야망이 크고 배포가 두둑하며 카리스마와 지략으로 대업을 도모합니다.'},
    '壬寅': {'title': '지혜와 식복이 넘치는 흑호', 'char': '성격이 호탕하고 베풀기를 좋아하며 재주와 표현력이 좋아 복록이 많습니다.'},

    '癸丑': {'title': '혹한을 견디며 봄을 준비하는 소', 'char': '인내심과 근성이 남다르며 겉으로는 조용하지만 내면의 폭발적 에너지가 있습니다.'},
    '癸亥': {'title': '넓은 바다처럼 모든 것을 품는 돼지', 'char': '지혜가 깊고 이해심이 넓으며 통찰력과 직관력이 매우 뛰어납니다.'},
    '癸酉': {'title': '바위틈에서 솟아나는 맑은 샘물의 닭', 'char': '두뇌가 총명하고 학문과 예술을 사랑하며 깔끔하고 단아한 품격을 지닙니다.'},
    '癸未': {'title': '마른 대지에 내리는 단비 같은 양', 'char': '성실하고 헌신적이며 현실적인 감각과 자제력을 바탕으로 성취를 이룹니다.'},
    '癸巳': {'title': '총명함과 재복을 겸비한 흑사', 'char': '처세술이 뛰어나고 재물 감각이 발달했으며 천을귀인의 도움을 자주 받습니다.'},
    '癸卯': {'title': '새싹을 적시는 봄비의 토끼', 'char': '순수하고 귀여운 매력이 넘치며 창의력과 예술성, 식복이 가득합니다.'}
}


# ==========================================
# 천문 알고리즘: Jean Meeus 태양 황경 정밀 계산
# ==========================================
def solar_longitude_from_jd(jd):
    """Julian Date로부터 태양의 시황경(Apparent Solar Longitude) 계산 (오차 15분 미만)"""
    T = (jd - 2451545.0) / 36525.0
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T**2
    M = 357.52911 + 35999.05029 * T - 0.0001537 * T**2
    M_rad = math.radians(M)
    C = ((1.914602 - 0.004817 * T - 0.000014 * T**2) * math.sin(M_rad) +
         (0.019993 - 0.000101 * T) * math.sin(2 * M_rad) +
         0.000289 * math.sin(3 * M_rad))
    # 광행차 보정 약 -20.47초 (0.00569도)
    sun_true_lon = (L0 + C - 0.00569) % 360
    return sun_true_lon

def dt_to_jd_utc(dt_kst):
    """KST(UTC+9) datetime을 UTC Julian Date로 변환"""
    dt_utc = dt_kst - datetime.timedelta(hours=9)
    year, month, day = dt_utc.year, dt_utc.month, dt_utc.day
    hour, minute, second = dt_utc.hour, dt_utc.minute, dt_utc.second + dt_utc.microsecond / 1e6
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return jdn + (hour - 12) / 24.0 + minute / 1440.0 + second / 86400.0

def jd_to_dt_kst(jd):
    """UTC Julian Date를 KST datetime으로 변환"""
    jd_kst = jd + 9.0 / 24.0
    Z = int(jd_kst + 0.5)
    F = (jd_kst + 0.5) - Z
    if Z < 2299161:
        A = Z
    else:
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - int(alpha / 4)
    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)
    day = B - D - int(30.6001 * E)
    month = E - 1 if E < 14 else E - 13
    year = C - 4716 if month > 2 else C - 4715
    frac_day = F
    hour = int(frac_day * 24)
    minute = int((frac_day * 24 - hour) * 60)
    second = int(((frac_day * 24 - hour) * 60 - minute) * 60)
    return datetime.datetime(year, month, day, hour, minute, second)

def get_term_time(year, target_lon, approx_m, approx_d):
    """이분법으로 특정 절기의 정확한 절입 시각(KST) 탐색"""
    center = datetime.datetime(year, approx_m, approx_d, 12, 0)
    jd_low = dt_to_jd_utc(center - datetime.timedelta(days=6))
    jd_high = dt_to_jd_utc(center + datetime.timedelta(days=6))
    for _ in range(60):
        jd_mid = (jd_low + jd_high) / 2.0
        lon = solar_longitude_from_jd(jd_mid)
        diff = (lon - target_lon + 180) % 360 - 180
        if diff < 0:
            jd_low = jd_mid
        else:
            jd_high = jd_mid
    return jd_to_dt_kst((jd_low + jd_high) / 2.0)

def get_year_terms(saju_year):
    """
    사주 연도의 12절기 목록 (입춘부터 다음해 입춘까지)
    월지의 시작점이 되는 절(節) 12개
    """
    return [
        ('입춘', get_term_time(saju_year, 315, 2, 4), 2),    # 寅月
        ('경칩', get_term_time(saju_year, 345, 3, 6), 3),    # 卯月
        ('청명', get_term_time(saju_year, 15,  4, 5), 4),    # 辰月
        ('입하', get_term_time(saju_year, 45,  5, 6), 5),    # 巳月
        ('망종', get_term_time(saju_year, 75,  6, 6), 6),    # 午月
        ('소서', get_term_time(saju_year, 105, 7, 7), 7),    # 未月
        ('입추', get_term_time(saju_year, 135, 8, 8), 8),    # 申月
        ('백로', get_term_time(saju_year, 165, 9, 8), 9),    # 酉月
        ('한로', get_term_time(saju_year, 195, 10, 8), 10),  # 戌月
        ('입동', get_term_time(saju_year, 225, 11, 7), 11),  # 亥月
        ('대설', get_term_time(saju_year, 255, 12, 7), 0),   # 子月
        ('소한', get_term_time(saju_year + 1, 285, 1, 6), 1),# 丑月
        ('다음해 입춘', get_term_time(saju_year + 1, 315, 2, 4), 2)
    ]


# ==========================================
# 십성(육친) 계산 함수
# ==========================================
def get_ten_god(me_gan_idx, target_gan_idx):
    """
    일간(me_gan_idx) 대비 대상 천간(target_gan_idx)의 십성 산출
    비견, 겁재, 식신, 상관, 편재, 정재, 편관, 정관, 편인, 정인
    """
    me_elem = GAN_ELEM[me_gan_idx]
    target_elem = GAN_ELEM[target_gan_idx]
    
    me_yy = GAN_YIN_YANG[me_gan_idx]
    target_yy = GAN_YIN_YANG[target_gan_idx]
    same_yy = (me_yy == target_yy)
    
    relation = (target_elem - me_elem) % 5
    if relation == 0:
        return '비견' if same_yy else '겁재'
    elif relation == 1:
        return '식신' if same_yy else '상관'
    elif relation == 2:
        return '편재' if same_yy else '정재'
    elif relation == 3:
        return '편관' if same_yy else '정관'
    elif relation == 4:
        return '편인' if same_yy else '정인'
    return '비견'

def get_12_unsung(gan_idx, ji_idx):
    """천간과 지지의 12운성 산출"""
    start_ji, direction = CHANG_SAENG[gan_idx]
    diff = (ji_idx - start_ji) * direction % 12
    return UNSUNG_NAMES[diff]


# ==========================================
# 사주 만세력 메인 분석 클래스
# ==========================================
class SajuAnalyzer:
    def __init__(self, name="방문자", gender="male", birth_dt=None, has_hour=True, is_lunar=False, is_leap=False):
        self.name = name.strip() or "귀하"
        self.gender = gender # 'male' or 'female'
        self.has_hour = has_hour
        self.is_lunar = is_lunar
        self.is_leap = is_leap
        
        # 날짜 처리
        if is_lunar:
            # 음력을 양력으로 변환
            cal = KoreanLunarCalendar()
            cal.setLunarDate(birth_dt.year, birth_dt.month, birth_dt.day, is_leap)
            solar_iso = cal.SolarIsoFormat() # 'YYYY-MM-DD'
            sy, sm, sd = map(int, solar_iso.split('-'))
            self.solar_dt = datetime.datetime(sy, sm, sd, birth_dt.hour, birth_dt.minute)
            self.lunar_str = f"음력 {birth_dt.year}년 {birth_dt.month}월 {birth_dt.day}일" + (" (윤달)" if is_leap else " (평달)")
        else:
            self.solar_dt = birth_dt
            cal = KoreanLunarCalendar()
            cal.setSolarDate(birth_dt.year, birth_dt.month, birth_dt.day)
            self.lunar_str = f"음력 {cal.lunarYear}년 {cal.lunarMonth}월 {cal.lunarDay}일" + (" (윤달)" if cal.isIntercalation else " (평달)")
            
    def analyze(self):
        dt = self.solar_dt
        y = dt.year
        
        # 1. 사주 연도(입춘 기준) 결정
        spring_this = get_term_time(y, 315, 2, 4)
        if dt < spring_this:
            saju_year = y - 1
        else:
            spring_next = get_term_time(y + 1, 315, 2, 4)
            if dt >= spring_next:
                saju_year = y + 1
            else:
                saju_year = y
                
        # 2. 년주 계산
        year_gan_idx = (saju_year - 4) % 10
        year_ji_idx = (saju_year - 4) % 12
        
        # 3. 월주 및 절기 구간 계산
        terms = get_year_terms(saju_year)
        month_offset = 0
        prev_term = terms[0]
        next_term = terms[1]
        
        for i in range(12):
            t_start = terms[i][1]
            t_end = terms[i+1][1]
            if t_start <= dt < t_end:
                month_offset = i
                prev_term = terms[i]
                next_term = terms[i+1]
                break
                
        month_ji_idx = terms[month_offset][2]
        # 오호둔월법
        start_month_gan = ((year_gan_idx % 5) * 2 + 2) % 10
        month_gan_idx = (start_month_gan + month_offset) % 10
        
        # 4. 일주 계산 (율리우스일 JDN)
        # 23:30 넘는 경우 야자시 적용: 현대 만세력 기준 당일 일진 유지 또는 익일 시진 보정
        a = (14 - dt.month) // 12
        y_calc = dt.year + 4800 - a
        m_calc = dt.month + 12 * a - 3
        jdn = dt.day + (153 * m_calc + 2) // 5 + 365 * y_calc + y_calc // 4 - y_calc // 100 + y_calc // 400 - 32045
        day_gan_idx = (jdn + 9) % 10
        day_ji_idx = (jdn + 1) % 12
        
        # 5. 시주 계산
        if self.has_hour:
            total_minutes = dt.hour * 60 + dt.minute
            # 한국 표준시 30분 보정 (동경 135도 기준 23:30 ~ 01:29の子時)
            hour_ji_idx = ((total_minutes + 30) % 1440) // 120
            # 오서둔시법
            start_hour_gan = ((day_gan_idx % 5) * 2) % 10
            hour_gan_idx = (start_hour_gan + hour_ji_idx) % 10
        else:
            hour_ji_idx = None
            hour_gan_idx = None
            
        # 6. 대운 계산
        # 남양여음: 순행, 남음여양: 역행
        is_yang_year = (year_gan_idx % 2 == 0)
        is_forward = (self.gender == 'male' and is_yang_year) or (self.gender == 'female' and not is_yang_year)
        
        if is_forward:
            diff_days = max(0.1, (next_term[1] - dt).total_seconds() / 86400.0)
            daeun_dir_text = "순행(順行)"
        else:
            diff_days = max(0.1, (dt - prev_term[1]).total_seconds() / 86400.0)
            daeun_dir_text = "역행(逆行)"
            
        daeun_num = max(1, min(10, round(diff_days / 3.0)))
        
        # 7. 사주 기둥 데이터 구조화
        pillars = self._build_pillars(year_gan_idx, year_ji_idx, month_gan_idx, month_ji_idx, 
                                     day_gan_idx, day_ji_idx, hour_gan_idx, hour_ji_idx)
                                     
        # 8. 오행 분포 및 점수
        elements_stat = self._calc_elements(pillars, day_gan_idx, month_ji_idx, day_ji_idx)
        
        # 9. 신강 / 신약 분석
        strength = self._calc_strength(elements_stat, day_gan_idx, month_ji_idx, day_ji_idx, pillars)
        
        # 10. 용신 / 희신 / 기신 도출
        yongsin = self._determine_yongsin(day_gan_idx, month_ji_idx, strength, elements_stat)
        
        # 11. 대운 리스트 (10개 대운)
        daeun_list = self._build_daeun_list(month_gan_idx, month_ji_idx, is_forward, daeun_num, day_gan_idx)
        
        # 12. 올해 세운(2026 丙午년 등) 분석
        seun = self._calc_seun(day_gan_idx, yongsin)
        
        # 13. 일주론 및 종합 해설
        day_pillar_key = f"{GAN[day_gan_idx]}{JI[day_ji_idx]}"
        ilju_info = ILJU_DATA.get(day_pillar_key, {
            'title': f'{GAN_KR[day_gan_idx]}{JI_KR[day_ji_idx]} 일주',
            'char': '자신만의 독창적인 가치관과 뚜렷한 개성을 바탕으로 인생의 길을 열어갑니다.'
        })
        
        # 종합 결과 JSON 구조화
        result = {
            "meta": {
                "version": "1.0.0",
                "engine": "Antigravity Precision Saju Engine",
                "calculated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "user_info": {
                "name": self.name,
                "gender": self.gender,
                "gender_kr": "남성" if self.gender == "male" else "여성",
                "solar_datetime": dt.strftime("%Y년 %m월 %d일 %H시 %M분"),
                "solar_date_iso": dt.strftime("%Y-%m-%d %H:%M"),
                "lunar_str": self.lunar_str,
                "has_hour": self.has_hour,
                "current_year": datetime.datetime.now().year,
                "user_age": datetime.datetime.now().year - dt.year + 1,
                "term_info": {
                    "prev_term": f"{prev_term[0]} ({prev_term[1].strftime('%m월 %d일 %H:%M')})",
                    "next_term": f"{next_term[0]} ({next_term[1].strftime('%m월 %d일 %H:%M')})"
                }
            },
            "four_pillars": pillars,
            "day_master": {
                "gan": GAN[day_gan_idx],
                "gan_kr": GAN_KR[day_gan_idx],
                "element": GAN_ELEM_NAME[day_gan_idx],
                "element_hanja": ELEMENT_HANJA[GAN_ELEM[day_gan_idx]],
                "yin_yang": "양(陽)" if GAN_YIN_YANG[day_gan_idx] == 1 else "음(陰)",
                "color_info": ELEMENT_COLORS[GAN_ELEM_NAME[day_gan_idx]],
                "ilju_name": f"{day_pillar_key} ({GAN_KR[day_gan_idx]}{JI_KR[day_ji_idx]}) 일주",
                "ilju_title": ilju_info['title'],
                "ilju_char": ilju_info['char']
            },
            "five_elements": elements_stat,
            "strength": strength,
            "yongsin": yongsin,
            "daeun": {
                "daeun_number": daeun_num,
                "direction": daeun_dir_text,
                "direction_desc": f"{'양' if is_yang_year else '음'}년생 {'남성' if self.gender == 'male' else '여성'}으로 월주 기준 {daeun_dir_text}합니다. {daeun_num}세마다 대운이 바뀝니다.",
                "timeline": daeun_list
            },
            "seun": seun,
            "comprehensive": self._build_comprehensive(pillars, strength, yongsin, ilju_info, day_gan_idx)
        }
        
        return result
        
    def _build_pillars(self, y_g, y_j, m_g, m_j, d_g, d_j, h_g, h_j):
        """사주 4주 8자 세부 정보 생성"""
        def format_pillar(g_idx, j_idx, is_day=False):
            if g_idx is None or j_idx is None:
                return {
                    "is_known": False,
                    "gan": "時", "ji": "柱", "gan_kr": "시", "ji_kr": "주",
                    "gan_elem": "미상", "ji_elem": "미상",
                    "gan_elem_color": "#64748b", "ji_elem_color": "#64748b",
                    "gan_ten_god": "-", "ji_ten_god": "-",
                    "unsung": "-",
                    "hidden_gans": []
                }
            
            g_elem = GAN_ELEM_NAME[g_idx]
            j_elem = JI_ELEM_NAME[j_idx]
            main_j_gan = JI_MAIN_GAN[j_idx]
            
            # 지장간 포맷
            h_list = []
            for h_hanja, h_kr, h_g_idx, days in HIDDEN_GANS[j_idx]:
                h_tg = get_ten_god(d_g, h_g_idx)
                h_list.append({
                    "hanja": h_hanja,
                    "kr": h_kr,
                    "element": GAN_ELEM_NAME[h_g_idx],
                    "ten_god": h_tg,
                    "days": days
                })
                
            return {
                "is_known": True,
                "gan": GAN[g_idx],
                "ji": JI[j_idx],
                "gan_kr": GAN_KR[g_idx],
                "ji_kr": JI_KR[j_idx],
                "gan_elem": g_elem,
                "ji_elem": j_elem,
                "gan_elem_hanja": ELEMENT_HANJA[GAN_ELEM[g_idx]],
                "ji_elem_hanja": ELEMENT_HANJA[JI_ELEM[j_idx]],
                "gan_elem_color": ELEMENT_COLORS[g_elem]['color'],
                "ji_elem_color": ELEMENT_COLORS[j_elem]['color'],
                "gan_ten_god": "일간(我)" if is_day else get_ten_god(d_g, g_idx),
                "ji_ten_god": get_ten_god(d_g, main_j_gan),
                "unsung": get_12_unsung(d_g, j_idx),
                "hidden_gans": h_list
            }
            
        return {
            "hour": format_pillar(h_g, h_j),
            "day": format_pillar(d_g, d_j, is_day=True),
            "month": format_pillar(m_g, m_j),
            "year": format_pillar(y_g, y_j)
        }

    def _calc_elements(self, pillars, d_g, m_j, d_j):
        """오행 분포 및 가중치 점수 계산"""
        counts = {'목': 0, '화': 0, '토': 0, '금': 0, '수': 0}
        total_chars = 0
        
        # 1) 단순 개수 산출
        for p_name in ['year', 'month', 'day', 'hour']:
            p = pillars[p_name]
            if p['is_known']:
                counts[p['gan_elem']] += 1
                counts[p['ji_elem']] += 1
                total_chars += 2
                
        percentages = {k: round((v / total_chars) * 100, 1) if total_chars else 0 for k, v in counts.items()}
        
        # 2) 명리학 세력 점수 (100점 만점)
        # 월지 30, 일지 15, 년지 10, 시지 10, 일간 10, 월간 10, 시간 10, 년간 15 (시주 미상시 비례 환산)
        raw_scores = {'목': 0, '화': 0, '토': 0, '금': 0, '수': 0}
        weights = {
            'month_ji': 30,
            'day_ji': 15,
            'year_ji': 10,
            'hour_ji': 10 if pillars['hour']['is_known'] else 0,
            'day_gan': 10,
            'month_gan': 10,
            'hour_gan': 10 if pillars['hour']['is_known'] else 0,
            'year_gan': 15 if not pillars['hour']['is_known'] else 5
        }
        
        # 월지
        raw_scores[pillars['month']['ji_elem']] += weights['month_ji']
        # 일지
        raw_scores[pillars['day']['ji_elem']] += weights['day_ji']
        # 년지
        raw_scores[pillars['year']['ji_elem']] += weights['year_ji']
        # 일간
        raw_scores[pillars['day']['gan_elem']] += weights['day_gan']
        # 월간
        raw_scores[pillars['month']['gan_elem']] += weights['month_gan']
        # 년간
        raw_scores[pillars['year']['gan_elem']] += weights['year_gan']
        # 시주
        if pillars['hour']['is_known']:
            raw_scores[pillars['hour']['ji_elem']] += weights['hour_ji']
            raw_scores[pillars['hour']['gan_elem']] += weights['hour_gan']
        else:
            # 80점 만점을 100점으로 정규화
            total_curr = sum(raw_scores.values())
            for k in raw_scores:
                raw_scores[k] = round((raw_scores[k] / total_curr) * 100, 1)

        # 레이더 차트 데이터
        radar_labels = ['목(Wood)', '화(Fire)', '토(Earth)', '금(Metal)', '수(Water)']
        radar_keys = ['목', '화', '토', '금', '수']
        radar_values = [raw_scores[k] for k in radar_keys]
        
        sorted_elems = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
        strongest = sorted_elems[0][0]
        weakest = sorted_elems[-1][0]
        
        # 해설 텍스트 생성
        eval_parts = []
        for k in radar_keys:
            cnt = counts[k]
            if cnt >= 3:
                eval_parts.append(f"{k}({cnt}개) 기운이 매우 왕성하여 주도적 성향을 이룹니다.")
            elif cnt == 0:
                eval_parts.append(f"{k}(0개) 기운이 결핍되어 있어 후천적인 보완이 필요합니다.")
        if not eval_parts:
            eval_parts.append("오행이 조화롭게 안배되어 있어 성품이 원만하고 균형 감각이 뛰어납니다.")
            
        return {
            "counts": counts,
            "percentages": percentages,
            "scores": raw_scores,
            "radar": {
                "labels": radar_labels,
                "keys": radar_keys,
                "values": radar_values,
                "max_value": max(radar_values) if max(radar_values) > 30 else 40
            },
            "strongest": strongest,
            "weakest": weakest,
            "description": " ".join(eval_parts)
        }

    def _calc_strength(self, elements_stat, d_g, m_j, d_j, pillars):
        """
        신강(身强) · 신약(身弱) 정밀 분석
        득령(得令), 득지(得地), 득세(得勢) 판별
        """
        my_elem = GAN_ELEM_NAME[d_g]
        parent_elem = ELEMENT_NAMES[(GAN_ELEM[d_g] - 1) % 5] # 인성(나를 생하는 오행)
        ally_elems = [my_elem, parent_elem] # 비겁 + 인성
        
        # 1. 득령 여부 (월지가 비겁 또는 인성인가)
        month_ji_elem = pillars['month']['ji_elem']
        deung_ryeong = month_ji_elem in ally_elems
        
        # 2. 득지 여부 (일지가 비겁 또는 인성인가)
        day_ji_elem = pillars['day']['ji_elem']
        deung_ji = day_ji_elem in ally_elems
        
        # 3. 아군 점수 합산 (비겁 점수 + 인성 점수)
        scores = elements_stat['scores']
        ally_score = round(scores[my_elem] + scores[parent_elem], 1)
        enemy_score = round(100.0 - ally_score, 1)
        
        # 4. 득세 여부
        deung_se = ally_score >= 45.0
        
        # 5. 상태 분류
        if ally_score >= 75:
            status = "극신강 (極身强)"
            status_code = "extreme_strong"
            desc = "일간의 세력이 매우 막강하여 자존심과 주관이 하늘을 찌르며, 독립심과 개척 정신이 탁월합니다."
        elif ally_score >= 56:
            status = "신강 (身强)"
            status_code = "strong"
            desc = "일간의 힘이 든든하여 추진력과 리더십이 뛰어나며, 어려운 역경도 당당하게 돌파할 수 있는 기운을 갖추었습니다."
        elif ally_score >= 48:
            status = "중화신강 (中和身强)"
            status_code = "neutral_strong"
            desc = "일간의 힘과 주변 세력이 조화를 이루며 약간의 주도력을 겸비하여 가장 이상적인 균형을 유지하고 있습니다."
        elif ally_score >= 42:
            status = "중화신약 (中和身弱)"
            status_code = "neutral_weak"
            desc = "외부 환경과의 조화가 부드러우며 유연하고 협력적인 태도로 원만한 대인관계를 이끌어냅니다."
        elif ally_score >= 26:
            status = "신약 (身弱)"
            status_code = "weak"
            desc = "일간의 세력이 다소 부드럽고 섬세하여, 타인의 조력과 든든한 학문/귀인의 지원을 받을 때 큰 성취를 이룹니다."
        else:
            status = "극신약 (極身弱)"
            status_code = "extreme_weak"
            desc = "일간이 소모되기 쉬운 환경이므로 무리한 단독 진행보다는 신뢰할 수 있는 동료나 전문가의 협업이 필수적입니다."
            
        return {
            "status": status,
            "status_code": status_code,
            "ally_score": ally_score,
            "enemy_score": enemy_score,
            "deung_ryeong": deung_ryeong,
            "deung_ji": deung_ji,
            "deung_se": deung_se,
            "description": desc,
            "factors": [
                {"name": "득령 (得令)", "achieved": deung_ryeong, "desc": "월지의 기운을 얻었는가 (계절적 지지)"},
                {"name": "득지 (得地)", "achieved": deung_ji, "desc": "일지의 뿌리를 얻었는가 (자신의 터전)"},
                {"name": "득세 (得勢)", "achieved": deung_se, "desc": "사주 전반의 아군(인성·비겁) 세력 확보 여부"}
            ]
        }

    def _determine_yongsin(self, d_g, m_j, strength, elements_stat):
        """
        억부용신 및 조후용신 판별
        용신, 희신, 기신, 행운의 요소 추천
        """
        my_idx = GAN_ELEM[d_g]
        my_elem = ELEMENT_NAMES[my_idx]
        
        # 5개 오행 관계:
        # my: 비겁, my+1: 식상, my+2: 재성, my+3: 관성, my+4: 인성
        bigeob = my_elem
        siksang = ELEMENT_NAMES[(my_idx + 1) % 5]
        jaeseong = ELEMENT_NAMES[(my_idx + 2) % 5]
        gwanseong = ELEMENT_NAMES[(my_idx + 3) % 5]
        inseong = ELEMENT_NAMES[(my_idx + 4) % 5]
        
        status_code = strength['status_code']
        scores = elements_stat['scores']
        
        # 억부용신 로직
        if "strong" in status_code:
            # 신강: 기운을 덜어내거나 다스려야 함
            if scores[bigeob] > scores[inseong]:
                primary_elem = siksang
                sec_elem = jaeseong
                primary_type = "식상 (설기 - 재능 발휘)"
                sec_type = "재성 (희신 - 결실)"
                reason = "비겁의 넘치는 기운을 식상으로 유쾌하게 발산하고 재물로 결실을 맺는 식신생재가 최적입니다."
            else:
                primary_elem = jaeseong
                sec_elem = gwanseong
                primary_type = "재성 (극인 - 현실적 결실)"
                sec_type = "관성 (희신 - 명예와 규율)"
                reason = "인성의 과도한 생각을 재성으로 다스려 현실적인 실행력과 성과를 창출합니다."
            harmful_elem = inseong
        else:
            # 신약: 나를 돕거나 생해야 함
            strongest_enemy = max([siksang, jaeseong, gwanseong], key=lambda e: scores[e])
            if strongest_enemy == gwanseong:
                primary_elem = inseong
                sec_elem = bigeob
                primary_type = "인성 (살인상생 - 지혜와 학문)"
                sec_type = "비겁 (희신 - 동료의 조력)"
                reason = "강한 관성의 압박을 인성의 학문과 자격, 지혜로 승화시키는 살인상생의 구조가 길합니다."
            elif strongest_enemy == jaeseong:
                primary_elem = bigeob
                sec_elem = inseong
                primary_type = "비겁 (득재 - 주체성과 연대)"
                sec_type = "인성 (희신 - 지혜의 보충)"
                reason = "과도한 재다신약을 극복하기 위해 비겁의 든든한 주체성과 동료의 힘을 빌리는 것이 최선입니다."
            else:
                primary_elem = inseong
                sec_elem = bigeob
                primary_type = "인성 (파도극제 - 내실 강화)"
                sec_type = "비겁 (희신 - 체력과 근기)"
                reason = "과다한 식상의 에너지 소모를 인성의 자제력과 사색으로 보충하여 중심을 잡습니다."
            harmful_elem = siksang if strongest_enemy == siksang else gwanseong

        # 조후용신 (월지 기준)
        # 겨울(해자축: 11, 0, 1) -> 火
        # 여름(사오미: 5, 6, 7) -> 水
        johu_elem = None
        johu_desc = ""
        if m_j in [11, 0, 1]:
            johu_elem = "화"
            johu_desc = "한겨울의 차가운 사주이므로 따뜻한 태양과 모닥불 같은 火 기운이 조후용신으로 긴요합니다."
        elif m_j in [5, 6, 7]:
            johu_elem = "수"
            johu_desc = "뜨거운 한여름의 사주이므로 대지를 적셔주는 시원한 水 기운이 조후용신으로 생명수가 됩니다."
        else:
            johu_desc = "온화한 환절기에 태어나 기후가 조화로우므로 억부용신의 작용이 더욱 두드러집니다."

        # 행운의 팁
        lucky_map = {
            '목': {'colors': ['초록색', '에메랄드', '연두색'], 'numbers': [3, 8], 'dirs': ['동쪽'], 'items': '나무 화분, 원목 소품, 서적'},
            '화': {'colors': ['빨간색', '주황색', '코랄핑크'], 'numbers': [2, 7], 'dirs': ['남쪽'], 'items': '조명, 향초, 화려한 패션 소품'},
            '토': {'colors': ['황토색', '베이지', '브라운'], 'numbers': [5, 10], 'dirs': ['중앙', '남서쪽'], 'items': '도자기, 도금 액세서리, 스톤웨어'},
            '금': {'colors': ['흰색', '은색', '그레이'], 'numbers': [4, 9], 'dirs': ['서쪽'], 'items': '메탈 시계, 실버 주얼리, 깔끔한 정장'},
            '수': {'colors': ['검정색', '네이비', '감청색'], 'numbers': [1, 6], 'dirs': ['북쪽'], 'items': '분수대, 수조, 해양/수분 관련 소품'}
        }
        
        p_lucky = lucky_map[primary_elem]
        s_lucky = lucky_map[sec_elem]
        
        return {
            "primary": {
                "element": primary_elem,
                "element_hanja": ELEMENT_HANJA[ELEMENT_NAMES.index(primary_elem)],
                "type": primary_type,
                "color_info": ELEMENT_COLORS[primary_elem],
                "reason": reason
            },
            "secondary": {
                "element": sec_elem,
                "element_hanja": ELEMENT_HANJA[ELEMENT_NAMES.index(sec_elem)],
                "type": sec_type,
                "color_info": ELEMENT_COLORS[sec_elem]
            },
            "harmful": {
                "element": harmful_elem,
                "element_hanja": ELEMENT_HANJA[ELEMENT_NAMES.index(harmful_elem)],
                "type": "기신(忌神)",
                "color_info": ELEMENT_COLORS[harmful_elem],
                "reason": f"{harmful_elem} 기운이 과도해지면 균형이 깨지기 쉬우므로 과욕을 경계해야 합니다."
            },
            "johu": {
                "element": johu_elem,
                "desc": johu_desc
            },
            "lucky": {
                "colors": p_lucky['colors'] + [s_lucky['colors'][0]],
                "numbers": p_lucky['numbers'] + [s_lucky['numbers'][0]],
                "directions": p_lucky['dirs'] + [s_lucky['dirs'][0]],
                "items": p_lucky['items']
            }
        }

    def _build_daeun_list(self, m_g, m_j, is_forward, daeun_num, d_g):
        """10개 대운 타임라인 리스트 생성 및 현재 대운 태깅"""
        now_year = datetime.datetime.now().year
        user_birth_year = self.solar_dt.year
        current_korean_age = now_year - user_birth_year + 1
        
        daeun_list = []
        step = 1 if is_forward else -1
        
        curr_g = m_g
        curr_j = m_j
        
        # 10개 대운 생성
        for i in range(10):
            curr_g = (curr_g + step) % 10
            curr_j = (curr_j + step) % 12
            
            start_age = daeun_num + i * 10
            end_age = start_age + 9
            
            g_elem = GAN_ELEM_NAME[curr_g]
            j_elem = JI_ELEM_NAME[curr_j]
            main_j_gan = JI_MAIN_GAN[curr_j]
            
            tg_gan = get_ten_god(d_g, curr_g)
            tg_ji = get_ten_god(d_g, main_j_gan)
            
            is_active = (start_age <= current_korean_age <= end_age)
            
            theme = self._get_daeun_theme(tg_gan, tg_ji)
            
            daeun_list.append({
                "index": i + 1,
                "start_age": start_age,
                "end_age": end_age,
                "age_display": f"{start_age} ~ {end_age}세",
                "gan": GAN[curr_g],
                "ji": JI[curr_j],
                "gan_kr": GAN_KR[curr_g],
                "ji_kr": JI_KR[curr_j],
                "ganji_str": f"{GAN[curr_g]}{JI[curr_j]} ({GAN_KR[curr_g]}{JI_KR[curr_j]})",
                "gan_elem": g_elem,
                "ji_elem": j_elem,
                "gan_elem_color": ELEMENT_COLORS[g_elem]['color'],
                "ji_elem_color": ELEMENT_COLORS[j_elem]['color'],
                "ten_god_gan": tg_gan,
                "ten_god_ji": tg_ji,
                "unsung": get_12_unsung(d_g, curr_j),
                "is_active": is_active,
                "theme": theme
            })
            
        return daeun_list

    def _get_daeun_theme(self, tg_gan, tg_ji):
        """대운 10년 테마 해석 문구"""
        pair = (tg_gan, tg_ji)
        if '식신' in pair or '상관' in pair:
            if '편재' in pair or '정재' in pair:
                return "식상생재(食傷生財) 대운: 창의적 재능과 활동이 큰 재물과 결실로 이어지는 황금기"
            return "식상(食傷) 대운: 새로운 분야에 도전하고 자신의 재능과 전문성을 널리 알리는 도약기"
        elif '정관' in pair or '편관' in pair:
            if '정인' in pair or '편인' in pair:
                return "관인상생(官印相生) 대운: 사회적 명예와 지위가 격상되고 든든한 인정과 결실을 얻는 시기"
            return "관성(官星) 대운: 무거운 책임감과 리더십을 발휘하며 공적인 성과를 일구는 전환기"
        elif '정재' in pair or '편재' in pair:
            return "재성(財星) 대운: 자산의 증식과 현실적인 기반 마련, 활발한 경제 활동의 호황기"
        elif '정인' in pair or '편인' in pair:
            return "인성(印星) 대운: 학문, 자격증 취득, 내면의 성찰과 지적 자산이 축적되는 성숙기"
        elif '비견' in pair or '겁재' in pair:
            return "비겁(比劫) 대운: 주체적인 독립심이 고양되고 든든한 동료와 함께 새로운 판을 짜는 시기"
        return "변화와 성장의 대운: 삶의 새로운 국면을 맞이하여 균형을 다져가는 시기"

    def _calc_seun(self, d_g, yongsin):
        """올해 세운(2026 丙午년 등) 정밀 분석"""
        now = datetime.datetime.now()
        year = now.year # 2026
        
        # 년 간지
        y_gan = (year - 4) % 10
        y_ji = (year - 4) % 12
        
        g_elem = GAN_ELEM_NAME[y_gan]
        j_elem = JI_ELEM_NAME[y_ji]
        main_j_gan = JI_MAIN_GAN[y_ji]
        
        tg_gan = get_ten_god(d_g, y_gan)
        tg_ji = get_ten_god(d_g, main_j_gan)
        
        # 일간과의 조화 및 용신과의 조화
        p_elem = yongsin['primary']['element']
        is_harmonious = (g_elem == p_elem or j_elem == p_elem)
        
        # 세운별 맞춤 스토리
        year_names = {2024: "갑진(甲辰)년", 2025: "을사(乙巳)년", 2026: "병오(丙午)년", 2027: "정미(丁未)년"}
        curr_name = year_names.get(year, f"{GAN_KR[y_gan]}{JI_KR[y_ji]}년")
        
        overall = (f"{year}년 {curr_name}은 천간의 {tg_gan}({GAN[y_gan]})와 지지의 {tg_ji}({JI[y_ji]}) 기운이 "
                   f"강력하게 작용하는 해입니다. "
                   + ("용신의 기운과 부합하여 바라던 목표를 성취하고 귀인의 조력을 얻기 유리한 호운입니다." if is_harmonious
                      else "적극적인 도전 속에서도 실속을 챙기고 무리한 확장을 경계하는 지혜가 빛을 발하는 시기입니다."))
                      
        wealth = f"재물 면에서는 {tg_gan}의 기운으로 인해 계획성 있는 지출과 장기적 투자가 길하며, 충동적 소비를 줄이면 알짜 자산이 형성됩니다."
        career = f"직업/학업 면에서는 {tg_ji}의 영향으로 전문성과 책임감이 돋보이며, 주변의 신뢰를 바탕으로 한 단계 도약할 수 있는 기회가 찾아옵니다."
        relation = "인간관계에서는 솔직하면서도 품격 있는 태도가 호감을 불러일으키며, 귀인과의 인연이 열리는 계기가 됩니다."
        health = f"{j_elem} 오행의 기운이 강해지므로 평소 무리하지 않는 수면 습관과 균형 잡힌 식단을 유지하는 것이 활력의 원천입니다."
        
        return {
            "year": year,
            "ganji": f"{GAN[y_gan]}{JI[y_ji]} ({GAN_KR[y_gan]}{JI_KR[y_ji]})",
            "gan": GAN[y_gan],
            "ji": JI[y_ji],
            "gan_kr": GAN_KR[y_gan],
            "ji_kr": JI_KR[y_ji],
            "elem_gan": g_elem,
            "elem_ji": j_elem,
            "elem_gan_color": ELEMENT_COLORS[g_elem]['color'],
            "elem_ji_color": ELEMENT_COLORS[j_elem]['color'],
            "ten_god_gan": tg_gan,
            "ten_god_ji": tg_ji,
            "is_harmonious": is_harmonious,
            "overall": overall,
            "wealth": wealth,
            "career": career,
            "relation": relation,
            "health": health
        }

    def _build_comprehensive(self, pillars, strength, yongsin, ilju_info, d_g):
        """종합 심층 풀이 및 라이프 가이드"""
        my_elem = GAN_ELEM_NAME[d_g]
        keywords = [
            f"{my_elem}의 본원",
            ilju_info['title'].split()[0],
            strength['status'].split()[0],
            f"{yongsin['primary']['element']} 용신"
        ]
        
        life_advice = (
            f"귀하는 {ilju_info['title']}의 성정을 타고나 기본적으로 {ilju_info['char']} "
            f"현재 사주의 기운은 {strength['status']} 상태이며, 가장 소중한 에너지는 "
            f"{yongsin['primary']['element']} ({yongsin['primary']['type']})입니다. "
            f"이를 일상생활에서 적극적으로 활용하여 자신만의 확고한 강점을 꽃피우시기 바랍니다."
        )
        
        return {
            "keywords": keywords,
            "life_advice": life_advice,
            "recommendation": f"행운의 색상인 {', '.join(yongsin['lucky']['colors'])}을 코디에 활용하고, "
                             f"행운의 숫자 {', '.join(map(str, yongsin['lucky']['numbers']))}와 "
                             f"{', '.join(yongsin['lucky']['directions'])} 방향을 생활 동선에 접목해보세요."
        }

/**
 * app.js
 * 사주명리 만세력 심층 분석 웹앱 프론트엔드 스크립트
 * - 순수 JS (Vanilla JS), 외부 라이브러리 및 CDN 완전 무의존
 * - 1.5초 신비로운 오행 로딩 연출
 * - 순수 SVG 방사형 오행 Radar 차트 렌더러
 * - 구조화된 JSON 데이터 뷰어 및 다운로더
 */

let currentAnalysisResult = null;

// 페이지 로드 시 초기화
document.addEventListener("DOMContentLoaded", () => {
    initDateSelects();
    initTimeSelects();
    setDefaultValues();
    ensureInitialView();
});

// ESC 키로 JSON 모달 닫기 지원
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        const modal = document.getElementById("json-modal");
        if (modal && !modal.classList.contains("hidden")) {
            modal.classList.add("hidden");
        }
    }
});

// 처음 열면 입력 화면이 맨 위에 확실히 보이게 보장 및 JSON 모달 숨김
function ensureInitialView() {
    const inputStep = document.getElementById("step-input");
    const loadingStep = document.getElementById("step-loading");
    const resultStep = document.getElementById("step-result");
    const jsonModal = document.getElementById("json-modal");

    if (inputStep) {
        inputStep.classList.remove("hidden");
        inputStep.classList.add("active");
    }
    if (loadingStep) loadingStep.classList.add("hidden");
    if (resultStep) resultStep.classList.add("hidden");
    if (jsonModal) jsonModal.classList.add("hidden");

    window.scrollTo({ top: 0, left: 0, behavior: "instant" });
}

// 1. 생년월일 드롭다운 초기화
function initDateSelects() {
    const yearSelect = document.getElementById("birth-year");
    const monthSelect = document.getElementById("birth-month");
    const daySelect = document.getElementById("birth-day");

    // 1920년부터 2030년까지
    const currentYear = new Date().getFullYear();
    for (let y = currentYear; y >= 1920; y--) {
        const opt = document.createElement("option");
        opt.value = y;
        opt.textContent = `${y}년`;
        yearSelect.appendChild(opt);
    }

    // 1월 ~ 12월
    for (let m = 1; m <= 12; m++) {
        const opt = document.createElement("option");
        opt.value = m;
        opt.textContent = `${m}월`;
        monthSelect.appendChild(opt);
    }

    // 일 수 갱신 리스너
    yearSelect.addEventListener("change", updateDays);
    monthSelect.addEventListener("change", updateDays);
    updateDays();
}

function updateDays() {
    const year = parseInt(document.getElementById("birth-year").value) || 1995;
    const month = parseInt(document.getElementById("birth-month").value) || 5;
    const daySelect = document.getElementById("birth-day");
    const selectedDay = parseInt(daySelect.value) || 20;

    const daysInMonth = new Date(year, month, 0).getDate();
    daySelect.innerHTML = "";

    for (let d = 1; d <= daysInMonth; d++) {
        const opt = document.createElement("option");
        opt.value = d;
        opt.textContent = `${d}일`;
        daySelect.appendChild(opt);
    }

    if (selectedDay <= daysInMonth) {
        daySelect.value = selectedDay;
    } else {
        daySelect.value = daysInMonth;
    }
}

// 2. 시간 드롭다운 초기화
function initTimeSelects() {
    const hourSelect = document.getElementById("birth-hour");
    const minSelect = document.getElementById("birth-minute");

    // 0 ~ 23시
    for (let h = 0; h < 24; h++) {
        const opt = document.createElement("option");
        opt.value = h;
        const padH = String(h).padStart(2, "0");
        opt.textContent = `${padH}시`;
        hourSelect.appendChild(opt);
    }

    // 0 ~ 59분 (5분 단위 우선 또는 1분 단위)
    for (let m = 0; m < 60; m++) {
        const opt = document.createElement("option");
        opt.value = m;
        const padM = String(m).padStart(2, "0");
        opt.textContent = `${padM}분`;
        minSelect.appendChild(opt);
    }
}

// 기본값 설정 (1995년 5월 20일 14시 30분)
function setDefaultValues() {
    document.getElementById("birth-year").value = 1995;
    document.getElementById("birth-month").value = 5;
    updateDays();
    document.getElementById("birth-day").value = 20;
    document.getElementById("birth-hour").value = 14;
    document.getElementById("birth-minute").value = 30;
}

// 예시 데이터 자동 입력
function fillSampleData() {
    const samples = [
        { name: "이지은", gender: "female", year: 1993, month: 5, day: 16, hour: 13, min: 20 },
        { name: "권지용", gender: "male", year: 1988, month: 8, day: 18, hour: 20, min: 0 },
        { name: "김태형", gender: "male", year: 1995, month: 12, day: 30, hour: 6, min: 15 },
        { name: "박보검", gender: "male", year: 1993, month: 6, day: 16, hour: 11, min: 45 }
    ];
    const picked = samples[Math.floor(Math.random() * samples.length)];
    
    document.getElementById("user-name").value = picked.name;
    const genderRadios = document.getElementsByName("gender");
    for (let r of genderRadios) {
        if (r.value === picked.gender) r.checked = true;
    }
    document.getElementById("birth-year").value = picked.year;
    document.getElementById("birth-month").value = picked.month;
    updateDays();
    document.getElementById("birth-day").value = picked.day;
    document.getElementById("birth-hour").value = picked.hour;
    document.getElementById("birth-minute").value = picked.min;
    
    // 시간 체크 해제
    const unkTime = document.getElementById("unknown-time");
    if (unkTime.checked) {
        unkTime.checked = false;
        toggleUnknownTime();
    }
}

// 양력 / 음력 토글
function toggleCalType() {
    const calTypes = document.getElementsByName("cal_type");
    let isLunar = false;
    for (let c of calTypes) {
        if (c.checked && c.value === "lunar") isLunar = true;
    }
    const leapBox = document.getElementById("leap-month-box");
    if (isLunar) {
        leapBox.classList.remove("hidden");
    } else {
        leapBox.classList.add("hidden");
        document.getElementById("is-leap-month").checked = false;
    }

    // 탭 스타일 갱신
    document.querySelectorAll(".calendar-type-selector .tab-btn").forEach(btn => {
        const input = btn.querySelector("input");
        if (input.checked) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });
}

// 시간 모름 토글
function toggleUnknownTime() {
    const isUnknown = document.getElementById("unknown-time").checked;
    const timeInputs = document.getElementById("time-inputs");
    if (isUnknown) {
        timeInputs.style.opacity = "0.35";
        timeInputs.style.pointerEvents = "none";
    } else {
        timeInputs.style.opacity = "1";
        timeInputs.style.pointerEvents = "auto";
    }
}

// ========================================================
// 분석 제출 및 신비로운 로딩 시퀀스 (약 1.5초)
// ========================================================
async function handleAnalyzeSubmit(e) {
    e.preventDefault();

    const name = document.getElementById("user-name").value.trim() || "귀하";
    const gender = document.querySelector('input[name="gender"]:checked').value;
    const calType = document.querySelector('input[name="cal_type"]:checked').value;
    const isLunar = (calType === "lunar");
const isLeap = isLunar && (document.getElementById("is-leap-month")?.checked || false);


    const year = parseInt(document.getElementById("birth-year").value);
    
    const month = parseInt(document.getElementById("birth-month").value);
    const day = parseInt(document.getElementById("birth-day").value);
    const unknownTime = document.getElementById("unknown-time")?.checked || false;


    const hour = unknownTime ? 12 : parseInt(document.getElementById("birth-hour").value);
    const minute = unknownTime ? 0 : parseInt(document.getElementById("birth-minute").value);

    const payload = {
        name,
        gender,
        year,
        month,
        day,
        hour,
        minute,
        has_hour: !unknownTime,
        is_lunar: isLunar,
        is_leap: isLeap
    };

    // 1) 화면 전환: 입력 -> 로딩
    document.getElementById("step-input").classList.add("hidden");
    const loadingSection = document.getElementById("step-loading");
    loadingSection.classList.remove("hidden");

    // 2) 백엔드 API 요청 시작
    const apiPromise = fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    }).then(res => {
        if (!res.ok) throw new Error("분석 중 오류가 발생했습니다.");
        return res.json();
    });

    // 3) 신비로운 1.5초 로딩 시퀀스 연출
    const statusText = document.getElementById("loading-status-text");
    const progressFill = document.getElementById("loading-progress-fill");

    statusText.textContent = "천문학적 태양 황경 24절기 절입 시각 대조 중...";
    progressFill.style.width = "25%";

    await delay(500);
    statusText.textContent = "사주 4주 8자 음양오행 에너지 및 십성 추출 중...";
    progressFill.style.width = "65%";

    await delay(500);
    statusText.textContent = "신강·신약 판별 및 억부·조후 용신, 10년 대운 도출 중...";
    progressFill.style.width = "90%";

    await delay(500);
    progressFill.style.width = "100%";

    try {
        const result = await apiPromise;
        currentAnalysisResult = result;

        // 4) 로딩 -> 결과 화면 전환
        loadingSection.classList.add("hidden");
        document.getElementById("step-result").classList.remove("hidden");
        window.scrollTo({ top: 0, behavior: "smooth" });

        // 5) 결과 화면 렌더링
        renderResult(result);
    } catch (err) {
        alert("사주 분석에 실패했습니다: " + err.message);
        goToInput();
    }
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function goToInput() {
    document.getElementById("step-result").classList.add("hidden");
    document.getElementById("step-loading").classList.add("hidden");
    document.getElementById("step-input").classList.remove("hidden");
    window.scrollTo({ top: 0, behavior: "smooth" });
}

// ========================================================
// 결과 화면 렌더링
// ========================================================
function renderResult(data) {
    // 1. 프로필 요약
    const user = data.user_info;
    const dm = data.day_master;
    document.getElementById("res-user-name").textContent = `${user.name} 님의 사주명식`;
    document.getElementById("res-gender-badge").textContent = user.gender_kr;
    document.getElementById("res-age-badge").textContent = `${user.user_age}세 (${user.birth_year || user.solar_datetime.split('년')[0]}년생)`;
    document.getElementById("res-solar-dt").textContent = `양력: ${user.solar_datetime}`;
    document.getElementById("res-lunar-dt").textContent = user.lunar_str;
    document.getElementById("res-prev-term").textContent = `이전 절기: ${user.term_info.prev_term}`;
    document.getElementById("res-next-term").textContent = `다음 절기: ${user.term_info.next_term}`;

    document.getElementById("res-day-hanja").textContent = dm.gan;
    document.getElementById("res-day-hanja").style.color = dm.color_info.color;
    document.getElementById("res-ilju-title").textContent = dm.ilju_name;
    document.getElementById("res-ilju-sub").textContent = dm.ilju_title;

    // 2. 사주 4주 원국표
    const pillars = data.four_pillars;
    renderPillarCell("hour", pillars.hour);
    renderPillarCell("day", pillars.day);
    renderPillarCell("month", pillars.month);
    renderPillarCell("year", pillars.year);

    // 3. 오행 통계 & 순수 SVG Radar 차트
    renderFiveElements(data.five_elements);

    // 4. 신강 · 신약 분석
    renderStrength(data.strength);

    // 5. 용신 · 희신 & 개운 가이드
    renderYongsin(data.yongsin);

    // 6. 10년 대운 타임라인
    renderDaeun(data.daeun);

    // 7. 올해 세운 카드
    renderSeun(data.seun);

    // 8. 종합 심층 조언
    renderComprehensive(data.comprehensive);
}

// 기둥별 렌더링 헬퍼
function renderPillarCell(pName, pData) {
    const ganElem = document.getElementById(`p-${pName}-gan`);
    const jiElem = document.getElementById(`p-${pName}-ji`);
    const ganKr = document.getElementById(`p-${pName}-gan-kr`);
    const jiKr = document.getElementById(`p-${pName}-ji-kr`);
    const ganTg = document.getElementById(`p-${pName}-gan-tg`);
    const jiTg = document.getElementById(`p-${pName}-ji-tg`);
    const ganEBadge = document.getElementById(`p-${pName}-gan-elem`);
    const jiEBadge = document.getElementById(`p-${pName}-ji-elem`);
    const unsung = document.getElementById(`p-${pName}-unsung`);
    const hiddenList = document.getElementById(`p-${pName}-hidden-list`);

    if (!pData.is_known) {
        ganElem.textContent = "時";
        jiElem.textContent = "柱";
        ganKr.textContent = "시";
        jiKr.textContent = "주";
        ganTg.textContent = "미상";
        jiTg.textContent = "미상";
        ganEBadge.textContent = "미상";
        jiEBadge.textContent = "미상";
        unsung.textContent = "-";
        hiddenList.innerHTML = `<span style="color:#64748b;">시간 정보 없음</span>`;
        return;
    }

    ganElem.textContent = pData.gan;
    ganElem.style.color = pData.gan_elem_color;
    jiElem.textContent = pData.ji;
    jiElem.style.color = pData.ji_elem_color;

    ganKr.textContent = pData.gan_kr;
    jiKr.textContent = pData.ji_kr;

    ganTg.textContent = pData.gan_ten_god;
    jiTg.textContent = pData.ji_ten_god;

    ganEBadge.textContent = `${pData.gan_elem}(${pData.gan_elem_hanja})`;
    ganEBadge.style.background = pData.gan_elem_color + "25";
    ganEBadge.style.color = pData.gan_elem_color;

    jiEBadge.textContent = `${pData.ji_elem}(${pData.ji_elem_hanja})`;
    jiEBadge.style.background = pData.ji_elem_color + "25";
    jiEBadge.style.color = pData.ji_elem_color;

    unsung.textContent = pData.unsung;

    // 지장간 목록
    hiddenList.innerHTML = "";
    pData.hidden_gans.forEach(h => {
        const item = document.createElement("div");
        item.className = "h-item";
        item.innerHTML = `
            <span>${h.hanja} (${h.kr})</span>
            <span style="color:var(--text-muted);">${h.ten_god} · ${h.days}일</span>
        `;
        hiddenList.appendChild(item);
    });
}

// ========================================================++
// 오행 통계 & 완전 오프라인 순수 SVG Radar 차트 렌더러
// ========================================================
function renderFiveElements(elemData) {
    // 1) 텍스트 및 막대 바
    document.getElementById("res-strongest-elem").textContent = `${elemData.strongest} 기운`;
    document.getElementById("res-weakest-elem").textContent = `${elemData.weakest} 기운`;
    document.getElementById("res-elem-desc").textContent = elemData.description;

    const barsWrap = document.getElementById("element-bars");
    barsWrap.innerHTML = "";

    const elemColorMap = {
        '목': { color: '#22c55e', hanja: '木', name: '목(Wood)' },
        '화': { color: '#ef4444', hanja: '火', name: '화(Fire)' },
        '토': { color: '#eab308', hanja: '土', name: '토(Earth)' },
        '금': { color: '#cbd5e1', hanja: '金', name: '금(Metal)' },
        '수': { color: '#3b82f6', hanja: '水', name: '수(Water)' }
    };

    for (let k of ['목', '화', '토', '금', '수']) {
        const count = elemData.counts[k];
        const pct = elemData.percentages[k];
        const score = elemData.scores[k];
        const info = elemColorMap[k];

        const row = document.createElement("div");
        row.className = "elem-bar-row";
        row.innerHTML = `
            <div class="elem-bar-header">
                <span style="font-weight:700; color:${info.color};">${info.hanja} ${info.name}</span>
                <span style="color:var(--text-muted);">${count}글자 (${pct}%) · <strong style="color:#fff;">${score}점</strong></span>
            </div>
            <div class="elem-bar-track">
                <div class="elem-bar-fill" style="width:${Math.min(100, score * 2)}%; background:${info.color};"></div>
            </div>
        `;
        barsWrap.appendChild(row);
    }

    // 2) 순수 SVG Radar 차트 그리기
    drawSvgRadarChart(elemData.scores);
}

function drawSvgRadarChart(scores) {
    const svg = document.getElementById("radar-svg");
    svg.innerHTML = "";

    const cx = 200;
    const cy = 180;
    const maxRadius = 110;
    const keys = ['목', '화', '토', '금', '수'];
    const labels = ['木 목', '火 화', '土 토', '金 금', '水 수'];
    const colors = ['#22c55e', '#ef4444', '#eab308', '#cbd5e1', '#3b82f6'];
    const n = keys.length;

    // 각도: 상단(-90도)부터 시계방향 72도 간격
    const angles = [];
    for (let i = 0; i < n; i++) {
        angles.push(-Math.PI / 2 + (2 * Math.PI * i) / n);
    }

    // 배경 정오각형 그리드 (3단계: 33%, 66%, 100%)
    const levels = [0.33, 0.66, 1.0];
    levels.forEach(level => {
        let pts = [];
        for (let i = 0; i < n; i++) {
            const r = maxRadius * level;
            const x = cx + r * Math.cos(angles[i]);
            const y = cy + r * Math.sin(angles[i]);
            pts.push(`${x},${y}`);
        }
        const poly = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
        poly.setAttribute("points", pts.join(" "));
        poly.setAttribute("fill", "none");
        poly.setAttribute("stroke", "rgba(255, 255, 255, 0.08)");
        poly.setAttribute("stroke-width", "1");
        svg.appendChild(poly);
    });

    // 방사형 축 선 & 라벨
    for (let i = 0; i < n; i++) {
        const x2 = cx + maxRadius * Math.cos(angles[i]);
        const y2 = cy + maxRadius * Math.sin(angles[i]);

        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", cx);
        line.setAttribute("y1", cy);
        line.setAttribute("x2", x2);
        line.setAttribute("y2", y2);
        line.setAttribute("stroke", "rgba(255, 255, 255, 0.1)");
        line.setAttribute("stroke-width", "1");
        svg.appendChild(line);

        // 라벨 위치
        const lx = cx + (maxRadius + 24) * Math.cos(angles[i]);
        const ly = cy + (maxRadius + 24) * Math.sin(angles[i]);

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", lx);
        text.setAttribute("y", ly + 4);
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("fill", colors[i]);
        text.setAttribute("font-size", "12");
        text.setAttribute("font-weight", "bold");
        text.textContent = labels[i];
        svg.appendChild(text);
    }

    // 데이터 다각형 포인트 계산
    // 점수 만점 기준 약 50점을 100% 반지름으로 스케일링 (최대값 보정)
    const maxScore = Math.max(...Object.values(scores), 40);
    const dataPoints = [];
    for (let i = 0; i < n; i++) {
        const val = scores[keys[i]] || 0;
        const ratio = Math.min(1.0, Math.max(0.08, val / maxScore));
        const r = maxRadius * ratio;
        const x = cx + r * Math.cos(angles[i]);
        const y = cy + r * Math.sin(angles[i]);
        dataPoints.push({ x, y, val, color: colors[i] });
    }

    // 데이터 다각형 채우기
    const dataPoly = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
    dataPoly.setAttribute("points", dataPoints.map(p => `${p.x},${p.y}`).join(" "));
    dataPoly.setAttribute("fill", "rgba(245, 158, 11, 0.3)");
    dataPoly.setAttribute("stroke", "#f59e0b");
    dataPoly.setAttribute("stroke-width", "2.5");
    svg.appendChild(dataPoly);

    // 각 꼭짓점 원형 포인트 및 점수 텍스트
    dataPoints.forEach(p => {
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", p.x);
        circle.setAttribute("cy", p.y);
        circle.setAttribute("r", "4");
        circle.setAttribute("fill", "#fff");
        circle.setAttribute("stroke", p.color);
        circle.setAttribute("stroke-width", "2");
        svg.appendChild(circle);

        const scoreText = document.createElementNS("http://www.w3.org/2000/svg", "text");
        scoreText.setAttribute("x", p.x);
        scoreText.setAttribute("y", p.y - 8);
        scoreText.setAttribute("text-anchor", "middle");
        scoreText.setAttribute("fill", "#fef08a");
        scoreText.setAttribute("font-size", "10");
        scoreText.setAttribute("font-weight", "bold");
        scoreText.textContent = `${p.val}점`;
        svg.appendChild(scoreText);
    });
}

// ========================================================
// 4. 신강 · 신약 분석 렌더링
// ========================================================
function renderStrength(strData) {
    document.getElementById("res-strength-badge").textContent = strData.status;
    document.getElementById("res-strength-desc").textContent = strData.description;

    // 스펙트럼 포인터 위치
    const pointer = document.getElementById("spectrum-pointer");
    const scoreVal = Math.max(0, Math.min(100, strData.ally_score));
    pointer.style.left = `${scoreVal}%`;
    document.getElementById("pointer-score").textContent = `${scoreVal}점 (인비)`;

    // 득령 / 득지 / 득세 카드
    const grid = document.getElementById("factors-grid");
    grid.innerHTML = "";

    strData.factors.forEach(f => {
        const card = document.createElement("div");
        card.className = `factor-card ${f.achieved ? 'achieved' : ''}`;
        card.innerHTML = `
            <div class="factor-name">${f.name}</div>
            <span class="factor-tag ${f.achieved ? 'yes' : 'no'}">${f.achieved ? '성취 (O)' : '미달 (X)'}</span>
            <div class="factor-desc">${f.desc}</div>
        `;
        grid.appendChild(card);
    });
}

// ========================================================
// 5. 용신 · 희신 & 개운 가이드 렌더링
// ========================================================
function renderYongsin(yData) {
    const p = yData.primary;
    const s = yData.secondary;
    const h = yData.harmful;
    const j = yData.johu;

    document.getElementById("y-primary-elem").textContent = `${p.element} (${p.element_hanja})`;
    document.getElementById("y-primary-elem").style.color = p.color_info.color;
    document.getElementById("y-primary-type").textContent = p.type;
    document.getElementById("y-primary-reason").textContent = p.reason;

    document.getElementById("y-secondary-elem").textContent = `${s.element} (${s.element_hanja})`;
    document.getElementById("y-secondary-elem").style.color = s.color_info.color;
    document.getElementById("y-secondary-type").textContent = s.type;

    document.getElementById("y-johu-desc").textContent = j.desc;
    document.getElementById("y-harmful-elem").textContent = `${h.element} (${h.element_hanja}) - ${h.reason}`;

    // 행운 요소
    const lk = yData.lucky;
    document.getElementById("lucky-colors").textContent = lk.colors.join(", ");
    document.getElementById("lucky-numbers").textContent = lk.numbers.join(", ");
    document.getElementById("lucky-dirs").textContent = lk.directions.join(", ");
    document.getElementById("lucky-items").textContent = lk.items;
}

// ========================================================
// 6. 10년 대운 타임라인 렌더링
// ========================================================
function renderDaeun(daeunData) {
    document.getElementById("daeun-summary-info").textContent =
        `대운수: ${daeunData.daeun_number} · ${daeunData.direction} · ${daeunData.direction_desc}`;

    const timeline = document.getElementById("daeun-timeline");
    timeline.innerHTML = "";

    daeunData.timeline.forEach(d => {
        const card = document.createElement("div");
        card.className = `daeun-card ${d.is_active ? 'active' : ''}`;
        card.onclick = () => alert(`[${d.age_display} 대운]\n간지: ${d.ganji_str}\n십성: 천간 ${d.ten_god_gan} / 지지 ${d.ten_god_ji}\n12운성: ${d.unsung}\n\n해설: ${d.theme}`);

        card.innerHTML = `
            ${d.is_active ? '<div class="current-badge">★ 현재 대운</div>' : ''}
            <div class="d-age">${d.age_display}</div>
            <div class="d-ganji">
                <span style="color:${d.gan_elem_color}">${d.gan}</span><span style="color:${d.ji_elem_color}">${d.ji}</span>
            </div>
            <div class="d-tg">${d.ten_god_gan} · ${d.ten_god_ji}</div>
            <div class="d-unsung">${d.unsung}</div>
        `;
        timeline.appendChild(card);
    });
}

// ========================================================
// 7. 올해 세운 렌더링
// ========================================================
function renderSeun(seunData) {
    document.getElementById("seun-title-year").textContent = `${seunData.year}년 ${seunData.ganji} 운세 흐름`;
    document.getElementById("seun-ganji").textContent = `${seunData.gan}${seunData.ji}`;
    document.getElementById("seun-kr").textContent = `(${seunData.gan_kr}${seunData.ji_kr}년)`;
    document.getElementById("seun-tg-tag").textContent = `천간: ${seunData.ten_god_gan} / 지지: ${seunData.ten_god_ji}`;
    document.getElementById("seun-overall").textContent = seunData.overall;

    document.getElementById("seun-wealth").textContent = seunData.wealth;
    document.getElementById("seun-career").textContent = seunData.career;
    document.getElementById("seun-relation").textContent = seunData.relation;
    document.getElementById("seun-health").textContent = seunData.health;
}

// ========================================================
// 8. 종합 심층 조언 렌더링
// ========================================================
function renderComprehensive(compData) {
    const kwWrap = document.getElementById("res-keywords");
    kwWrap.innerHTML = "";
    compData.keywords.forEach(kw => {
        const pill = document.createElement("span");
        pill.className = "kw-pill";
        pill.textContent = `#${kw}`; 
        kwWrap.appendChild(pill);
    });

    document.getElementById("res-life-advice").textContent = compData.life_advice;
    document.getElementById("res-recommendation").textContent = compData.recommendation;
}

// ========================================================
// JSON 모달 및 다운로드
// ========================================================
function openJsonModal() {
    if (!currentAnalysisResult) return;
    const jsonStr = JSON.stringify(currentAnalysisResult, null, 2);
    document.getElementById("json-code-view").textContent = jsonStr;
    document.getElementById("json-modal").classList.remove("hidden");
}

function closeJsonModal(e) {
    if (e && e.target !== e.currentTarget && !e.target.classList.contains("modal-close-btn")) return;
    document.getElementById("json-modal").classList.add("hidden");
}

function copyJsonToClipboard() {
    if (!currentAnalysisResult) return;
    const jsonStr = JSON.stringify(currentAnalysisResult, null, 2);
    navigator.clipboard.writeText(jsonStr).then(() => {
        alert("JSON 데이터가 클립보드에 복사되었습니다!");
    }).catch(() => {
        alert("클립보드 복사에 실패했습니다.");
    });
}

function downloadJsonFile() {
    if (!currentAnalysisResult) return;
    const jsonStr = JSON.stringify(currentAnalysisResult, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const name = currentAnalysisResult.user_info.name || "saju";
    const date = new Date().toISOString().slice(0, 10);
    a.href = url;
    a.download = `saju_analysis_${name}_${date}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

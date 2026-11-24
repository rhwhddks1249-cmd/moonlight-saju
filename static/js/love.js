/* 달빛사주 연애운·궁합 (추가 기능 / 기존 코드는 건드리지 않음) */
(function () {
  'use strict';
  var STEMS = ['갑','을','병','정','무','기','경','신','임','계'];
  var ELEM = ['목','화','토','금','수'];
  var BASE = Date.UTC(1949, 9, 1); // 1949-10-01 = 갑자일

  function todayStemIdx() {
    var n = new Date();
    var t = Date.UTC(n.getFullYear(), n.getMonth(), n.getDate());
    var days = Math.round((t - BASE) / 86400000);
    return ((days % 10) + 10) % 10;
  }
  function rel(a, b) { // 상대(b)가 나(a)에게 어떤 관계인지
    if ((a % 5 === b % 5) && false) return 0;
    if (Math.abs(a - b) === 5) return 'hap';
    var ea = Math.floor(a / 2), eb = Math.floor(b / 2);
    var d = (eb - ea + 5) % 5;
    return d; // 0 같음 1 내가 생함 2 내가 극함 3 나를 극함 4 나를 생함
  }
  function isLoveGod(a, b, gender) {
    var ea = Math.floor(a / 2), eb = Math.floor(b / 2);
    var d = (eb - ea + 5) % 5;
    return gender === 'M' ? d === 2 : d === 3;
  }
  var TXT = {
    hap: ['천간합', '서로 끌어당기는 인연이에요. 자연스럽게 마음이 통해요.', 90],
    1: ['내가 챙겨 주는 관계', '내가 더 베푸는 편이에요. 고마움을 말로 표현해 달라고 해 보세요.', 76],
    4: ['나를 채워 주는 관계', '상대가 나를 편안하게 감싸 줘요. 기대는 만큼 고마움도 전하세요.', 80],
    0: ['닮은 관계', '말이 잘 통하는 친구 같은 사이예요. 고집이 부딪히지 않게 양보하세요.', 70],
    2: ['내가 이끄는 관계', '내가 주도하는 사이예요. 밀어붙이지 말고 의견을 먼저 물어보세요.', 64],
    3: ['긴장감 있는 관계', '설렘과 부딪힘이 함께 와요. 말투를 부드럽게 하면 좋아져요.', 62]
  };
  function compat(a, b, g) {
    var r = rel(a, b), t = TXT[r], s = t[2];
    if (isLoveGod(a, b, g)) s += 8;
    return { score: Math.min(s, 98), name: t[0], text: t[1], love: isLoveGod(a, b, g) };
  }
  function todayLove(a, g) {
    var t = todayStemIdx(), r = rel(a, t), s, msg;
    if (r === 'hap') { s = 5; msg = '마음이 통하는 날이에요. 먼저 연락해 보세요.'; }
    else if (isLoveGod(a, t, g)) { s = 5; msg = '이성에게 매력이 돋보이는 날이에요. 약속을 잡기 좋아요.'; }
    else if (r === 4) { s = 4; msg = '따뜻한 위로를 받는 날이에요. 편하게 대화하세요.'; }
    else if (r === 1) { s = 3; msg = '내가 더 챙기게 되는 날이에요. 부담 갖지 마세요.'; }
    else if (r === 0) { s = 3; msg = '무난한 날이에요. 자기 시간을 즐기세요.'; }
    else { s = 2; msg = '말실수가 나기 쉬워요. 차분하게 말하세요.'; }
    return { stem: STEMS[t], star: s, msg: msg };
  }
  function opts(sel) {
    return STEMS.map(function (s, i) { return '<option value="' + i + '"' + (i === sel ? ' selected' : '') + '>' + s + '</option>'; }).join('');
  }
  function guessStem() {
    try {
      var m = (document.body.innerText || '').match(/나의 일간\s*([갑을병정무기경신임계])/);
      if (m) return STEMS.indexOf(m[1]);
    } catch (e) {}
    return 0;
  }
  function stars(n) { return '★★★★★'.slice(0, n) + '☆☆☆☆☆'.slice(0, 5 - n); }

  function build() {
    if (document.getElementById('love-compat-card')) return;
    var box = document.createElement('div');
    box.id = 'love-compat-card';
    box.style.cssText = 'margin:24px auto;padding:20px;max-width:900px;border-radius:18px;background:rgba(60,30,110,.55);border:1px solid rgba(255,200,120,.35);color:#fff;font-size:15px;line-height:1.6;';
    box.innerHTML =
      '<div style="font-size:20px;font-weight:700;color:#ffc857;margin-bottom:10px">💕 연애운 · 궁합</div>' +
      '<div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:12px">' +
      '<label>나의 일간 <select id="lc-me" style="padding:6px;border-radius:8px">' + opts(guessStem()) + '</select></label>' +
      '<label>성별 <select id="lc-g" style="padding:6px;border-radius:8px"><option value="M">남성</option><option value="F">여성</option></select></label>' +
      '<label>상대 일간 <select id="lc-you" style="padding:6px;border-radius:8px">' + opts(5) + '</select></label>' +
      '<button id="lc-go" type="button" style="padding:8px 16px;border:0;border-radius:10px;background:#ffb347;color:#2a1450;font-weight:700;cursor:pointer">궁합 보기</button></div>' +
      '<div id="lc-out"></div>' +
      '<div style="margin-top:10px;font-size:12px;opacity:.75">※ 재미로 보는 참고용이에요. 상대의 일간은 상대 사주 결과의 일간(甲 등)을 넣어 주세요.</div>';
    var host = document.getElementById('step-result') || document.body;
    host.appendChild(box);
    document.getElementById('lc-go').onclick = run;
    run();
  }
  function run() {
    var a = +document.getElementById('lc-me').value;
    var b = +document.getElementById('lc-you').value;
    var g = document.getElementById('lc-g').value;
    var t = todayLove(a, g), c = compat(a, b, g);
    document.getElementById('lc-out').innerHTML =
      '<div style="padding:12px;border-radius:12px;background:rgba(0,0,0,.25);margin-bottom:10px"><b style="color:#ffc857">오늘의 연애운</b> ' +
      '<span style="color:#ffd76a">' + stars(t.star) + '</span><br>오늘은 ' + t.stem + '일(日)이에요. ' + t.msg + '</div>' +
      '<div style="padding:12px;border-radius:12px;background:rgba(0,0,0,.25)"><b style="color:#ffc857">' + STEMS[a] + '(' + ELEM[Math.floor(a/2)] + ') × ' + STEMS[b] + '(' + ELEM[Math.floor(b/2)] + ') 궁합</b> ' +
      '<span style="color:#ffd76a">' + c.score + '점</span><br><b>' + c.name + '</b> · ' + c.text +
      (c.love ? '<br>💘 내 연애 인연의 기운(' + (g === 'M' ? '재성' : '관성') + ')에 해당하는 상대예요.' : '') + '</div>';
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build); else build();
})();

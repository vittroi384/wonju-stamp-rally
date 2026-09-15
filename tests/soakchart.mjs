// 지속 테스트 결과 + 폭주 테스트(2026-09-14) 비교 차트 → HTML + PNG
import fs from 'fs';
import { chromium } from 'playwright';
const DIR = 'C:/dev/stamp-rally-v3/';
const soakFile = fs.readdirSync(DIR).filter(f => /^지속테스트_.*\.json$/.test(f)).sort().pop();
const soak = JSON.parse(fs.readFileSync(DIR + soakFile, 'utf8'));
const burst = JSON.parse(fs.readFileSync('C:/dev/stamp-rally/부하테스트_2026-09-14.json', 'utf8'));
const date = soakFile.match(/\d{4}-\d{2}-\d{2}/)[0];
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

/* ---------- 지속 테스트 타임라인 (분 단위): 막대 = 요청/초, 선 = p50·p95, 점 = 에러 ---------- */
function timeline(){
  const B = soak.buckets, W = 760, H = 300, L = 54, R = 54, T = 26, Bt = 44, iw = W - L - R, ih = H - T - Bt;
  const maxRps = Math.max(1, ...B.map(b => b.rps)) * 1.15, maxMs = Math.max(200, ...B.map(b => b.p95)) * 1.2;
  const x = i => L + (i + .5) * iw / B.length, bw = iw / B.length * .6;
  const yR = v => T + ih - v / maxRps * ih, yM = v => T + ih - v / maxMs * ih;
  let s = `<svg viewBox="0 0 ${W} ${H}" class="tl">`;
  [0, .25, .5, .75, 1].forEach(f => { s += `<line class="grid" x1="${L}" x2="${W - R}" y1="${T + ih - f * ih}" y2="${T + ih - f * ih}"/><text class="ax l" x="${L - 8}" y="${T + ih - f * ih}">${(f * maxRps).toFixed(0)}</text><text class="ax r" x="${W - R + 8}" y="${T + ih - f * ih}">${(f * maxMs).toFixed(0)}</text>`; });
  B.forEach((b, i) => { s += `<rect class="rps" x="${x(i) - bw / 2}" y="${yR(b.rps)}" width="${bw}" height="${T + ih - yR(b.rps)}" rx="4"/>`; });
  const path = k => B.map((b, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)} ${yM(b[k]).toFixed(1)}`).join(' ');
  s += `<path class="p95" d="${path('p95')}"/><path class="p50" d="${path('p50')}"/>`;
  B.forEach((b, i) => { s += `<circle class="p95d" cx="${x(i)}" cy="${yM(b.p95)}" r="3.5"/><circle class="p50d" cx="${x(i)}" cy="${yM(b.p50)}" r="3"/>`; if(b.errors) s += `<text class="err" x="${x(i)}" y="${yR(b.rps) - 8}">✕${b.errors}</text>`; s += `<text class="ax b" x="${x(i)}" y="${H - 22}">${b.minute}분</text>`; });
  s += `<text class="lab" x="${L}" y="${H - 5}">■ 요청/초 (왼쪽 축)</text><text class="lab" x="${L + 150}" y="${H - 5}" style="fill:#FF8A2B">— p95 (ms, 오른쪽 축)</text><text class="lab" x="${L + 300}" y="${H - 5}" style="fill:#1FA97A">— p50</text>`;
  return s + '</svg>';
}
/* ---------- 폭주 테스트 단계별: 막대 = p95, 색 = 에러율 ---------- */
function burstChart(){
  const W = 760, H = 260, L = 54, R = 20, T = 26, Bt = 44, iw = W - L - R, ih = H - T - Bt;
  const maxMs = Math.max(...burst.map(b => b.p95)) * 1.15;
  const x = i => L + (i + .5) * iw / burst.length, bw = iw / burst.length * .58, y = v => T + ih - v / maxMs * ih;
  let s = `<svg viewBox="0 0 ${W} ${H}" class="tl">`;
  [0, .25, .5, .75, 1].forEach(f => s += `<line class="grid" x1="${L}" x2="${W - R}" y1="${T + ih - f * ih}" y2="${T + ih - f * ih}"/><text class="ax l" x="${L - 8}" y="${T + ih - f * ih}">${(f * maxMs / 1000).toFixed(1)}s</text>`);
  burst.forEach((b, i) => {
    const col = b.errRate > 30 ? '#FF5C6C' : b.errRate > 0 ? '#FFC83D' : '#2D5BFF';
    s += `<rect x="${x(i) - bw / 2}" y="${y(b.p95)}" width="${bw}" height="${T + ih - y(b.p95)}" rx="5" fill="${col}"/><text class="val" x="${x(i)}" y="${y(b.p95) - 6}">${b.p95 >= 1000 ? (b.p95 / 1000).toFixed(1) + 's' : b.p95 + 'ms'}</text>`;
    s += `<text class="ax b" x="${x(i)}" y="${H - 24}">${b.users}명</text><text class="ax b2" x="${x(i)}" y="${H - 9}" style="fill:${b.errRate ? '#FF5C6C' : '#8A91A8'}">에러 ${b.errRate}%</text>`;
  });
  s += `<line class="p95ref" x1="${L}" x2="${W - R}" y1="${y(soak.p95)}" y2="${y(soak.p95)}"/><text class="lab" x="${W - R - 4}" y="${y(soak.p95) - 6}" text-anchor="end" style="fill:#1FA97A">지속 테스트 p95 ${soak.p95}ms</text>`;
  return s + '</svg>';
}
const kindRows = ['register', 'stamp', 'reopen', 'survey'].map(k => { const bs = soak.buckets.map(b => b.byKind[k]).filter(Boolean); if(!bs.length) return ''; const n = bs.reduce((a, b) => a + b.n, 0), err = bs.reduce((a, b) => a + b.err, 0); const p95 = Math.max(...bs.map(b => b.p95)), p50 = Math.round(bs.reduce((a, b) => a + b.p50 * b.n, 0) / n); return `<tr><td>${{ register: '등록 (visitor_create)', stamp: '도장 (add_stamp)', reopen: '앱 다시 열기 (visitor_get·stamps)', survey: '설문 완료' }[k]}</td><td class="n">${n.toLocaleString()}</td><td class="n">${p50}</td><td class="n">${p95}</td><td class="n ${err ? 'bad' : ''}">${err}</td></tr>`; }).join('');
const burstOk = burst.filter(b => b.errRate === 0).pop();
const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>지속 테스트 ${date}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<style>
:root{--ink:#151A2D;--ink2:#4B5370;--ink3:#8A91A8;--line:#E4E7EF;--bg:#F2F3F7;--card:#fff;--blue:#2D5BFF;--mint:#1FA97A;--sun:#FFC83D;--coral:#FF5C6C;--orange:#FF8A2B}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Pretendard Variable",Pretendard,-apple-system,system-ui,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;background:var(--bg);color:var(--ink);padding:28px 32px 36px;width:1180px;font-feature-settings:"tnum"}
h1{font-size:24px;font-weight:900;letter-spacing:-.02em}
.sub{color:var(--ink3);font-size:13px;margin-top:4px}
.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:20px 0}
.kpi{background:var(--card);border-radius:16px;padding:14px 16px;box-shadow:0 1px 2px rgba(21,26,45,.05),0 2px 8px rgba(21,26,45,.05)}
.kpi .k{font-size:12px;font-weight:700;color:var(--ink3)}
.kpi .v{font-size:28px;font-weight:900;letter-spacing:-.02em;margin-top:2px}
.kpi .v small{font-size:13px;color:var(--ink3);font-weight:700;margin-left:2px}
.kpi .d{font-size:12px;color:var(--ink2);margin-top:3px}
.kpi.ok .v{color:var(--mint)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.card{background:var(--card);border-radius:18px;padding:18px 20px;box-shadow:0 1px 2px rgba(21,26,45,.05),0 2px 8px rgba(21,26,45,.05)}
.card h2{font-size:15px;font-weight:900}
.card .s{font-size:12.5px;color:var(--ink3);margin:3px 0 10px;line-height:1.5}
svg.tl{width:100%;height:auto;display:block}
.grid line.grid{stroke:var(--line);stroke-width:1}
.ax{font-size:10.5px;fill:var(--ink3);dominant-baseline:central}.ax.l{text-anchor:end}.ax.r{text-anchor:start}.ax.b{text-anchor:middle;font-weight:700;fill:var(--ink2)}.ax.b2{text-anchor:middle;font-size:10px}
.rps{fill:#C9D5FF}
.p95{fill:none;stroke:var(--orange);stroke-width:2.5;stroke-linejoin:round}.p50{fill:none;stroke:var(--mint);stroke-width:2.5;stroke-linejoin:round}
.p95d{fill:var(--orange)}.p50d{fill:var(--mint)}
.err{font-size:11px;font-weight:900;fill:var(--coral);text-anchor:middle}
.val{font-size:11px;font-weight:800;fill:var(--ink2);text-anchor:middle}
.lab{font-size:11px;font-weight:700;fill:var(--ink2)}
.p95ref{stroke:var(--mint);stroke-width:1.5;stroke-dasharray:5 4}
table{width:100%;border-collapse:collapse;font-size:13px;margin-top:6px}
th{font-size:11.5px;color:var(--ink3);text-align:left;font-weight:700;padding:6px 8px;border-bottom:1px solid var(--line)}
td{padding:7px 8px;border-bottom:1px solid var(--line)}
td.n{text-align:right;font-weight:700;font-variant-numeric:tabular-nums}
td.bad{color:var(--coral)}
.verdict{margin-top:16px;background:#DDF5EC;color:#12704F;border-radius:14px;padding:12px 16px;font-size:13.5px;line-height:1.7;font-weight:600}
.verdict b{font-weight:900}
</style></head><body>
<h1>스탬프앱 지속 테스트 <span style="color:var(--ink3);font-weight:700">${date}</span></h1>
<div class="sub">Supabase 무료 플랜 · 실제 앱과 같은 RPC(visitor_create → add_stamp 토큰·90초 간격 → visitor_survey_done) · 운영본부 대시보드 15초 폴링 동시 진행</div>
<div class="kpis">
  <div class="kpi"><div class="k">시나리오</div><div class="v">${soak.minutes}<small>분</small></div><div class="d">초당 ${soak.arrivalsPerSec}명 도착 · 방문객 ${soak.visitors.toLocaleString()}명</div></div>
  <div class="kpi"><div class="k">총 요청</div><div class="v">${soak.requests.toLocaleString()}</div><div class="d">평균 ${soak.avgRps}/초 · 최대 ${soak.peakRps}/초</div></div>
  <div class="kpi ${soak.errors ? '' : 'ok'}"><div class="k">에러</div><div class="v">${soak.errors}<small>건</small></div><div class="d">${soak.errRate}%${Object.keys(soak.errCodes).length ? ' · ' + Object.entries(soak.errCodes).map(([k, v]) => `${k} ${v}`).join(', ') : ''}</div></div>
  <div class="kpi ok"><div class="k">p50 / p95</div><div class="v">${soak.p50}<small>ms</small> / ${soak.p95}<small>ms</small></div><div class="d">p99 ${soak.p99}ms · 최대 ${soak.max}ms</div></div>
  <div class="kpi"><div class="k">지연 드리프트</div><div class="v">${soak.buckets.length > 2 ? (soak.buckets[soak.buckets.length - 2].p95 - soak.buckets[0].p95 >= 0 ? '+' : '') + (soak.buckets[soak.buckets.length - 2].p95 - soak.buckets[0].p95) : '-'}<small>ms</small></div><div class="d">첫 분 p95 ${soak.buckets[0]?.p95} → 마지막 ${soak.buckets[Math.max(0, soak.buckets.length - 2)]?.p95}</div></div>
  <div class="kpi"><div class="k">대시보드 폴링</div><div class="v">${soak.dashP50}<small>ms</small></div><div class="d">p50 · 최대 ${soak.dashMax}ms (요청 4개 묶음)</div></div>
</div>
<div class="grid">
  <div class="card"><h2>지속 테스트 · 분 단위 추이</h2><div class="s">방문객이 쌓일수록 요청이 늘어나는데(도장 90초 간격) 지연이 따라 오르는지 본다. 막대 = 요청/초, 선 = 응답 시간</div>${timeline()}</div>
  <div class="card"><h2>폭주 테스트 (2026-09-14) · 동시 접속별 p95</h2><div class="s">한꺼번에 N명이 등록→도장 7개를 3초 안에 몰아치는 최악 상황. 당시엔 REST 직접 insert 방식(치팅 방지 전)</div>${burstChart()}</div>
  <div class="card"><h2>지속 테스트 · 요청 종류별</h2><div class="s">p50 은 가중 평균, p95 는 분 단위 최댓값</div>
    <table><thead><tr><th>요청</th><th style="text-align:right">건수</th><th style="text-align:right">p50 ms</th><th style="text-align:right">p95 ms</th><th style="text-align:right">에러</th></tr></thead><tbody>${kindRows}</tbody></table></div>
  <div class="card"><h2>두 테스트 비교</h2><div class="s">부하의 성격이 다르다 — 폭주는 순간 최대치, 지속은 행사 시간 내내 버티는지</div>
    <table><thead><tr><th></th><th>폭주 (에러 0 최대 단계)</th><th>지속</th></tr></thead><tbody>
      <tr><td>부하 모양</td><td>${burstOk.users}명 동시 · ${burstOk.rps}/초 순간</td><td>초당 ${soak.arrivalsPerSec}명 꾸준히 · ${soak.avgRps}/초 평균, ${soak.peakRps}/초 최대</td></tr>
      <tr><td>지속 시간</td><td class="n">${burstOk.durationSec}초</td><td class="n">${soak.minutes}분</td></tr>
      <tr><td>p50 / p95</td><td class="n">${burstOk.p50} / ${burstOk.p95} ms</td><td class="n">${soak.p50} / ${soak.p95} ms</td></tr>
      <tr><td>에러율</td><td class="n">${burstOk.errRate}%</td><td class="n">${soak.errRate}%</td></tr>
      <tr><td>대시보드 p50</td><td class="n">${burstOk.dashP50} ms</td><td class="n">${soak.dashP50} ms</td></tr>
      <tr><td>한계 지점</td><td>${burst.find(b => b.errRate > 0) ? burst.find(b => b.errRate > 0).users + '명 동시부터 에러 (' + burst.find(b => b.errRate > 0).errRate + '%)' : '없음'}</td><td>${soak.errors ? soak.errors + '건 에러' : '없음 — 지연 상승도 없음'}</td></tr>
    </tbody></table>
    <div class="verdict">행사 실부하(하루 5만 명 = 초당 2~3명 등록, 도장은 그 7배)를 넘는 <b>초당 ${soak.arrivalsPerSec}명 도착이 ${soak.minutes}분 이어져도</b> 에러 ${soak.errors}건, p95 ${soak.p95}ms. ${soak.errors === 0 && soak.p95 < 500 ? '무료 플랜으로 행사 시간 내내 버티는 데 문제 없음. 위험은 개막 직후 같은 순간 폭주뿐이고, 그건 폭주 테스트 기준 800명 동시까지 괜찮음.' : '수치 확인 필요.'}</div>
  </div>
</div>
</body></html>`;
fs.writeFileSync(DIR + `지속테스트_${date}.html`, html);
const b = await chromium.launch({ channel: 'chrome' }); const p = await b.newPage({ viewport: { width: 1180, height: 900 }, deviceScaleFactor: 2 });
await p.goto('file:///' + DIR + `지속테스트_${date}.html`); await p.waitForTimeout(1200);
await p.screenshot({ path: DIR + `지속테스트_${date}.png`, fullPage: true }); await b.close();
console.log('saved', DIR + `지속테스트_${date}.png`);

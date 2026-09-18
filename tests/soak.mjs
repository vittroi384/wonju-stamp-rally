// 지속(soak) 테스트: 행사 당일처럼 방문객이 꾸준히 들어와 등록→(걷기)→도장 7개(서버 90초 간격 준수)→설문 완료 를 반복.
// 폭주 테스트(load.mjs, 2026-09-14)가 "한꺼번에 N명"이었다면 이건 "N분 동안 초당 r명"이 계속 들어오는 상황. 1분 단위로 지연·에러를 기록.
// 사용: node soak.mjs [분=10] [초당 도착=4] [이름 접두어=지속]    결과: ../지속테스트_YYYY-MM-DD.json
// ★ 끝나도 테스트 데이터는 지우지 않음(실서버 전체 삭제 금지). 관리자 › 데이터 › 전부 삭제로 정리
import { writeFileSync } from 'node:fs';
const U = 'https://YOUR-PROJECT.supabase.co', K = 'YOUR_SUPABASE_ANON_KEY';
const PW = process.env.ADMIN_PW; if(!PW){ console.error('ADMIN_PW 환경변수에 관리자 비번 넣고 실행:  $env:ADMIN_PW="비번"; node tests/파일.mjs'); process.exit(1); }
const H = { apikey: K, Authorization: `Bearer ${K}`, 'Content-Type': 'application/json' };
const MIN = +(process.argv[2] || 10), RATE = +(process.argv[3] || 4), PREFIX = process.argv[4] || '지속', GOAL = 7, GAP = 92;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const rnd = (a, b) => a + Math.random() * (b - a);
const samples = []; const T0 = Date.now();

async function call(kind, path, body, timeout = 20000){
  const t0 = performance.now(); const ac = new AbortController(); const tm = setTimeout(() => ac.abort(), timeout);
  try{
    const r = await fetch(`${U}/rest/v1/${path}`, { method: body ? 'POST' : 'GET', headers: H, body: body ? JSON.stringify(body) : undefined, signal: ac.signal });
    const txt = await r.text(); const ms = performance.now() - t0;
    let j = null; try{ j = txt ? JSON.parse(txt) : null; }catch(e){}
    const expected = !r.ok && /TOO_FAST|BAD_TOKEN/.test(txt);   // 서버 규칙에 걸린 건 에러가 아니라 정상 거절
    samples.push({ kind, ms, status: r.status, t: Date.now() - T0, ok: r.ok || expected, msg: r.ok ? '' : (j?.message || txt).slice(0, 80) });
    return { ok: r.ok, status: r.status, body: j };
  }catch(e){ samples.push({ kind, ms: performance.now() - t0, status: 0, t: Date.now() - T0, ok: false, msg: e.name }); return { ok: false, status: 0, body: null }; }
  finally{ clearTimeout(tm); }
}
const rpc = (kind, fn, body) => call(kind, 'rpc/' + fn, body);

const toks = Object.fromEntries((await rpc('setup', 'admin_booth_tokens', { pw: PW })).body.map(r => [r.booth_id, r.token]));
const BOOTHS = Object.keys(toks).filter(k => /^b\d+$/.test(k));
console.log('booths', BOOTHS.length, '| duration', MIN, 'min | arrivals', RATE, '/s');

let spawning = true, active = 0, finished = 0, spawned = 0;
async function visitor(i){
  active++;
  try{
    const v = await rpc('register', 'visitor_create', { nm: PREFIX + i, school: '테스트초', grade: '초' + (1 + i % 6), gender: i % 2 ? '남' : '여' });
    const vid = v.body?.[0]?.id; if(!vid) return;
    const picked = new Set(); let n = 0;
    await sleep(rnd(15000, 45000));   // 첫 부스까지 걷기
    while(n < GOAL && spawning){
      let bid; do{ bid = BOOTHS[Math.floor(Math.random() * BOOTHS.length)]; }while(picked.has(bid)); picked.add(bid);
      const r = await rpc('stamp', 'add_stamp', { vid, bid, tok: toks[bid] });
      if(r.ok) n++;
      if(Math.random() < .15){ await rpc('reopen', 'visitor_get', { vid }); await rpc('reopen', 'visitor_stamps', { vid }); }   // 앱 다시 열기
      await sleep(rnd(GAP * 1000, GAP * 1000 + 30000));   // 서버 간격(90초) + 체험 시간
    }
    if(n >= GOAL) await rpc('survey', 'visitor_survey_done', { vid });
  }finally{ active--; finished++; }
}
// 운영본부 대시보드 15초 폴링 (기본 모드: 뷰 + RPC 4개)
async function dashboard(){   // 운영 대시보드 2대가 15초마다 admin_dashboard 1개씩
  const t0 = performance.now();
  await Promise.all([rpc('dash', 'admin_dashboard', { pw: PW }), rpc('dash', 'admin_dashboard', { pw: PW })]);
  return performance.now() - t0;
}
const pct = (a, p) => { if(!a.length) return 0; const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; };

const tasks = []; const dashTimes = [];
const poller = (async () => { while(spawning){ dashTimes.push({ t: Date.now() - T0, ms: await dashboard() }); await sleep(15000); } })();
const reporter = setInterval(() => {
  const m = Math.floor((Date.now() - T0) / 60000), win = samples.filter(s => s.t > Date.now() - T0 - 60000 && s.kind !== 'dash');
  const ok = win.filter(s => s.ok).map(s => s.ms);
  console.log(`[${m}m] active ${active} spawned ${spawned} done ${finished} | last 60s: ${win.length} req (${(win.length / 60).toFixed(1)}/s) p50 ${pct(ok, .5).toFixed(0)} p95 ${pct(ok, .95).toFixed(0)} err ${win.length - ok.length}`);
}, 60000);

// 도착: 초당 RATE 명을 고르게
const endAt = T0 + MIN * 60000;
while(Date.now() < endAt){ tasks.push(visitor(spawned++)); await sleep(1000 / RATE); }
spawning = false; console.log('도착 종료 → 진행 중인 방문객 마무리(최대 60초)');
await Promise.race([Promise.all(tasks), sleep(60000)]); await poller; clearInterval(reporter);

// 집계: 1분 버킷
const buckets = [];
for(let m = 0; m < MIN + 1; m++){
  const w = samples.filter(s => s.t >= m * 60000 && s.t < (m + 1) * 60000 && s.kind !== 'dash' && s.kind !== 'setup'); if(!w.length) continue;
  const ok = w.filter(s => s.ok), lat = ok.map(s => s.ms);
  const byKind = {}; for(const k of ['register', 'stamp', 'reopen', 'survey']){ const s = w.filter(x => x.kind === k), o = s.filter(x => x.ok).map(x => x.ms); if(s.length) byKind[k] = { n: s.length, err: s.length - o.length, p50: +pct(o, .5).toFixed(0), p95: +pct(o, .95).toFixed(0) }; }
  const d = dashTimes.filter(x => x.t >= m * 60000 && x.t < (m + 1) * 60000).map(x => x.ms);
  buckets.push({ minute: m, requests: w.length, rps: +(w.length / 60).toFixed(2), errors: w.length - ok.length, p50: +pct(lat, .5).toFixed(0), p95: +pct(lat, .95).toFixed(0), max: +Math.max(0, ...lat).toFixed(0), dashP50: +pct(d, .5).toFixed(0), dashMax: +Math.max(0, ...d).toFixed(0), byKind });
}
const all = samples.filter(s => s.kind !== 'dash' && s.kind !== 'setup'), errs = all.filter(s => !s.ok), errCodes = {};
errs.forEach(e => { const k = (e.status || 'net') + ' ' + e.msg; errCodes[k] = (errCodes[k] || 0) + 1; });
const okLat = all.filter(s => s.ok).map(s => s.ms);
const summary = { date: new Date().toISOString(), minutes: MIN, arrivalsPerSec: RATE, visitors: spawned, finishedVisitors: finished, requests: all.length, errors: errs.length, errRate: +(100 * errs.length / all.length).toFixed(2), errCodes,
  p50: +pct(okLat, .5).toFixed(0), p95: +pct(okLat, .95).toFixed(0), p99: +pct(okLat, .99).toFixed(0), max: +Math.max(...okLat).toFixed(0), avgRps: +(all.length / (MIN * 60)).toFixed(1), peakRps: Math.max(...buckets.map(b => b.rps)),
  dashP50: +pct(dashTimes.map(x => x.ms), .5).toFixed(0), dashMax: +Math.max(0, ...dashTimes.map(x => x.ms)).toFixed(0), buckets };
const out = `C:/dev/stamp-rally-v3/지속테스트_${new Date().toISOString().slice(0, 10)}_${MIN}분_${RATE}ps.json`;
writeFileSync(out, JSON.stringify(summary, null, 1));
console.log(JSON.stringify({ ...summary, buckets: undefined }));
console.log('saved', out);
console.log(`테스트 데이터(${PREFIX}0~${spawned - 1}) 는 남겨둠 — 관리자 › 데이터 › 전부 삭제로 정리`);

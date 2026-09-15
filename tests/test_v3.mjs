// v3 회귀 테스트: 설문 자기신고 강화(A안 타이머 · B안 ?survey 복귀 · 탭 동기화) + 관리자 행사 설정 + 운영 대시보드
// 실서버(Supabase) 사용. 시작·끝에 admin_reset 으로 테스트 데이터 정리, settings 는 원래 값으로 복원.
import { chromium } from 'playwright';
const DIR = 'C:/dev/stamp-rally-v3/', OUT = DIR + 'tests/out/';
const APP = 'file:///' + DIR + '원주축전_스탬프앱_3.html', DASH = 'file:///' + DIR + '운영대시보드.html';
const U = 'https://YOUR-PROJECT.supabase.co', K = 'YOUR_SUPABASE_ANON_KEY', PW = '1234';
const H = { apikey: K, Authorization: `Bearer ${K}`, 'Content-Type': 'application/json' };
const rpc = async (fn, body) => { const r = await fetch(`${U}/rest/v1/rpc/${fn}`, { method: 'POST', headers: H, body: JSON.stringify(body) }); const t = await r.text(); if(!r.ok) throw new Error(fn + ' ' + r.status + ' ' + t); return t ? JSON.parse(t) : null; };
const rest = async p => (await fetch(`${U}/rest/v1/${p}`, { headers: H })).json();
import fs from 'fs'; fs.mkdirSync(OUT, { recursive: true });

const fails = [], errs = [];
const check = (name, ok, extra = '') => { console.log((ok ? '  ✓ ' : '  ✗ ') + name + (extra ? ' — ' + extra : '')); if(!ok) fails.push(name); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

// 0. 준비
const settings0 = (await rest('settings?id=eq.1&select=data'))[0]?.data || null;
await rpc('admin_reset', { pw: PW });
const toks = Object.fromEntries((await rpc('admin_booth_tokens', { pw: PW })).map(r => [r.booth_id, r.token]));
console.log('booth tokens', Object.keys(toks).length);

const b = await chromium.launch({ channel: 'chrome' });
const mobile = async () => { const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true }); const p = await ctx.newPage(); wire(p, 'mobile'); return { ctx, p }; };
const wire = (p, tag) => { p.on('pageerror', e => errs.push(tag + ': ' + e.message)); p.on('console', m => { if(m.type() === 'error' && !/net::|Failed to load resource|ERR_/.test(m.text())) errs.push(tag + ' console: ' + m.text()); }); };
const register = async (p, name) => {
  await p.evaluate(() => location.hash = '#/register'); await p.waitForSelector('#rLevel');
  await p.click('#rLevel button[data-l="중"]'); await p.click('#rGrade button[data-n="2"]');
  await p.fill('#rSchool', '원주중학교'); await p.fill('#rName', name); await p.click('#rGender button[data-g="남"]'); await p.check('#rConsent');
  await p.click('#rGo'); await p.waitForFunction(() => S.me && S.me.id); return p.evaluate(() => S.me.id);
};
const stampViaAdmin = async (vid, ids) => { for(const id of ids) await rpc('admin_add_stamp', { pw: PW, vid, bid: id }); };
const setTok = (p, n, t) => p.evaluate(([n, t]) => qrTok.set(n, t), [n, t]);

// ---------------------------------------------------------------- 1. A안: 타이머
console.log('\n[1] 완주 → 설문 타이머(A안)');
{
  const { ctx, p } = await mobile();
  await p.goto(APP); await p.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
  const vid = await register(p, '김하늘');
  await setTok(p, '7', toks['b7']);   // 앱으로 첫 도장 (서버 add_stamp: 토큰 검사). 이후 6개는 관리자 수동 도장 — 90초 간격 검사를 피하려고
  await p.evaluate(() => location.hash = '#/stamp/7'); await p.waitForFunction(() => /체험 완료/.test(document.body.innerText), null, { timeout: 10000 });
  check('앱에서 7번 도장', await p.evaluate(() => S.myStamps.length === 1));
  await stampViaAdmin(vid, ['b1', 'b2', 'b3', 'b4', 'b5', 'b6']);
  await p.reload(); await p.waitForFunction(() => S.myStamps.length === 7);
  await p.evaluate(() => location.hash = '#/'); await sleep(400);
  check('홈 카드 완주 표시', await p.evaluate(() => /완주/.test($('.stampcard').textContent)));
  await p.screenshot({ path: OUT + '1_done.png' });
  await p.evaluate(() => { CONFIG.surveyMinSec = 3; CONFIG.surveyUrl = 'https://example.com/form'; CONFIG.surveyCodeField = 'entry.999'; });
  await p.evaluate(() => location.hash = '#/my'); await p.waitForSelector('#svDone');
  check('처음엔 다 했어요 비활성', await p.evaluate(() => $('#svDone').disabled && /먼저/.test($('#svHint').textContent)));
  await p.evaluate(() => { window.__opened = []; window.open = u => { window.__opened.push(u); return null; }; });
  await p.click('#svOpen'); await sleep(700);
  const opened = await p.evaluate(() => window.__opened);
  check('설문 링크에 코드 미리 채움', /entry\.999=[A-Z0-9]{6}$/.test(opened[0] || ''), opened[0]);
  check('카운트다운 표시', await p.evaluate(() => $('#svDone').disabled && /초 뒤/.test($('#svHint').textContent)), await p.evaluate(() => $('#svHint').textContent));
  await p.evaluate(() => $('#svDone').click()); await sleep(300);   // playwright click 은 활성화될 때까지 기다리므로 DOM 클릭으로
  check('시간 전 클릭은 무시', await p.evaluate(() => !S.me.surveyAt));
  await p.screenshot({ path: OUT + '1_countdown.png' });
  await p.waitForFunction(() => !$('#svDone').disabled, null, { timeout: 6000 });
  check('3초 후 활성화', true);
  await p.reload(); await p.waitForFunction(() => S.me && S.myStamps.length === 7);
  await p.evaluate(() => { CONFIG.surveyMinSec = 3; CONFIG.surveyUrl = 'https://example.com/form'; });
  await p.evaluate(() => location.hash = '#/my'); await p.waitForSelector('#svDone');
  check('새로고침 후에도 열어본 시각 유지', await p.evaluate(() => S.surveyOpenAt > 0 && !$('#svDone').disabled));
  await p.click('#svDone'); await p.waitForSelector('#myQr', { timeout: 8000 });
  check('교환권 열림', true);
  await p.screenshot({ path: OUT + '1_voucher.png' });
  const v = await rpc('visitor_get', { vid });
  check('서버 survey_done_at 기록', !!v[0]?.survey_done_at);
  await ctx.close();
}

// ---------------------------------------------------------------- 2. B안: ?survey 복귀 + 탭 동기화
console.log('\n[2] ?survey 복귀 링크(B안) + 다른 탭 동기화');
{
  const { ctx, p } = await mobile();
  await p.goto(APP); await p.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
  const vid = await register(p, '이서준');
  // 완주 전 ?survey → 완료되면 안 됨
  await p.goto(APP + '?survey'); await p.waitForFunction(() => S.me && location.hash === '#/my');
  await sleep(500);
  check('완주 전 ?survey 는 무시', await p.evaluate(() => !S.me.surveyAt));
  await stampViaAdmin(vid, ['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7']);
  await p.reload(); await p.waitForFunction(() => S.myStamps.length === 7 && document.querySelector('#main')); await p.evaluate(() => location.hash = '#/my'); await p.waitForSelector('#svDone');   // replaceState 로 ?survey 가 이미 지워져 있어 goto 는 해시 이동만 됨 → reload
  check('완주 후 설문 대기 화면', await p.evaluate(() => S.myStamps.length === 7 && !S.me.surveyAt));
  // 다른 탭(구글폼 확인 메시지 링크로 열린 탭)에서 ?survey
  const p2 = await ctx.newPage(); wire(p2, 'tab2');
  await p2.goto(APP + '?survey'); await p2.waitForSelector('#myQr', { timeout: 10000 });
  check('?survey 탭에서 자동 완료 → 교환권', true);
  await p2.screenshot({ path: OUT + '2_return_tab.png' });
  await p.bringToFront(); await p.waitForSelector('#myQr', { timeout: 8000 }).catch(() => {});
  check('원래 탭도 교환권으로 바뀜(storage/visibility)', await p.evaluate(() => !!$('#myQr') && !!S.me.surveyAt));
  await ctx.close();
}

// ---------------------------------------------------------------- 3. 관리자 행사 설정 필드
console.log('\n[3] 관리자 › 행사 설정 (설문 최소 시간·코드 항목)');
{
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }); const p = await ctx.newPage(); wire(p, 'admin');
  await p.goto(APP); await p.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
  await p.evaluate(() => location.hash = '#/admin'); await p.waitForSelector('#pw');
  await p.fill('#pw', PW); await p.keyboard.press('Enter'); await p.waitForFunction(() => S.admin); await p.waitForSelector('.stats');
  await p.evaluate(() => location.hash = '#/admin/event'); await p.waitForSelector('#evSurveySec');
  await p.screenshot({ path: OUT + '3_event_form.png', fullPage: true });
  await p.fill('#evSurveySec', '45'); await p.fill('#evSurveyField', 'entry.123456'); await p.fill('#evSurvey', 'https://forms.gle/test');
  await p.click('#evSave'); await sleep(1500);
  const s = (await rest('settings?id=eq.1&select=data'))[0].data;
  check('settings 에 surveyMinSec/surveyCodeField 저장', s.surveyMinSec === 45 && s.surveyCodeField === 'entry.123456', JSON.stringify({ a: s.surveyMinSec, b: s.surveyCodeField }));
  await p.fill('#evSurveyField', 'bad id!'); await p.click('#evSave'); await sleep(400);
  check('잘못된 항목 ID 거부', await p.evaluate(() => /entry/.test($('#toast').textContent)));
  // 새 폰에서 설정 반영되는지
  const { ctx: c2, p: m } = await mobile(); await m.goto(APP); await m.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main')); await sleep(500);
  check('방문객 폰에 surveyMinSec 45 반영', await m.evaluate(() => CONFIG.surveyMinSec === 45 && CONFIG.surveyCodeField === 'entry.123456'));
  await c2.close(); await ctx.close();
}

// ---------------------------------------------------------------- 4. 운영 대시보드
console.log('\n[4] 운영 대시보드');
{
  const ctx = await b.newContext({ viewport: { width: 1600, height: 1000 } }); const p = await ctx.newPage(); wire(p, 'dash');
  await p.goto(DASH); await p.waitForSelector('#pw');
  await p.fill('#pw', 'wrong'); await p.click('#pwGo'); await p.waitForFunction(() => $('#pwErr').textContent.length > 0, null, { timeout: 8000 });
  check('틀린 비번 거부', await p.evaluate(() => /달라요/.test($('#pwErr').textContent)));
  await p.fill('#pw', PW); await p.click('#pwGo');
  await p.waitForFunction(() => !$('#dash').hidden && $('#kpis').children.length > 0, null, { timeout: 20000 });
  await sleep(800);
  const basic = await p.evaluate(() => D.basic);
  console.log('  mode:', basic ? '기본(SQL 9절 전)' : 'admin_dashboard');
  const kpi = await p.evaluate(() => [...$('#kpis').querySelectorAll('.kpi')].map(k => k.querySelector('.k').textContent + '=' + k.querySelector('.v').textContent));
  console.log('  KPI', kpi.join(' | '));
  check('등록 2명·완주 2명 집계', /등록 방문객=2/.test(kpi[0]) && /완주=2/.test(kpi[3]));
  check('지도에 부스 95개', await p.evaluate(() => $$('#mapwrap .bt').length) === 95, String(await p.evaluate(() => $$('#mapwrap .bt').length)));
  check('붐비는 부스 목록 있음', await p.evaluate(() => $('#hot .row') != null));
  check('조용한 부스 목록 있음', await p.evaluate(() => /도장 없음/.test($('#quiet').textContent)));
  await p.screenshot({ path: OUT + '4_dashboard.png', fullPage: true });
  await p.setViewportSize({ width: 420, height: 900 }); await sleep(300); await p.screenshot({ path: OUT + '4_dashboard_mobile.png', fullPage: true });
  await p.evaluate(() => $('#logout').click()); await sleep(200);
  check('로그아웃 → 로그인 화면', await p.evaluate(() => !$('#login').hidden));
  await ctx.close();
}

// ---------------------------------------------------------------- 정리
await rpc('admin_reset', { pw: PW });
if(settings0) await rpc('admin_save_settings', { pw: PW, data: settings0 });
await b.close();
console.log('\nERRORS', errs.length ? errs : 'none');
console.log('FAILS', fails.length ? fails : 'none');
process.exit(fails.length || errs.length ? 1 : 0);

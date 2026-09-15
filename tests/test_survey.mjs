// 앱 내 설문 테스트 (로컬 모드 복사본 — 서버 SQL 9절 실행 전이라 로컬 DB 로 흐름 검증)
import { chromium } from 'playwright';
import fs from 'fs';
const DIR = 'C:/dev/stamp-rally-v3/', OUT = DIR + 'tests/out/';
const src = fs.readFileSync(DIR + '원주축전_스탬프앱_3.html', 'utf8');
fs.writeFileSync(DIR + 'tests/_local.html', src.replace("supabaseUrl: 'https://YOUR-PROJECT.supabase.co'", "supabaseUrl: ''").replace("supabaseAnonKey: 'YOUR_SUPABASE_ANON_KEY'", "supabaseAnonKey: ''").replace(/\.\/qrcode\.min\.js|\.\/jsQR\.js/g, m => '..' + m.slice(1)));
const APP = 'file:///' + DIR + 'tests/_local.html';
const fails = [], errs = [];
const check = (name, ok, extra = '') => { console.log((ok ? '  ✓ ' : '  ✗ ') + name + (extra ? ' — ' + extra : '')); if(!ok) fails.push(name); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const b = await chromium.launch({ channel: 'chrome' });
const wire = (p, tag) => { p.on('pageerror', e => errs.push(tag + ': ' + e.message)); p.on('console', m => { if(m.type() === 'error' && !/net::|Failed to load resource|ERR_/.test(m.text())) errs.push(tag + ' console: ' + m.text()); }); };

console.log('[1] 방문객: 완주 → 앱 내 설문 → 교환권 (로컬 모드)');
const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
const p = await ctx.newPage(); wire(p, 'mobile');
await p.goto(APP); await p.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
check('로컬 모드', await p.evaluate(() => DB === LocalDB));
await p.evaluate(() => location.hash = '#/register'); await p.waitForSelector('#rLevel');
await p.click('#rLevel button[data-l="초"]'); await p.click('#rGrade button[data-n="4"]');
await p.fill('#rSchool', '단구초'); await p.fill('#rName', '박지우'); await p.click('#rGender button[data-g="여"]'); await p.check('#rConsent');
await p.click('#rGo'); await p.waitForFunction(() => S.me && S.me.id);
// 완주 전 #/survey 는 내 스탬프로
await p.evaluate(() => location.hash = '#/survey'); await sleep(400);
check('완주 전 #/survey → 내 스탬프로 돌려보냄', await p.evaluate(() => location.hash === '#/my'));
// 로컬 DB 에 도장 7개 직접 (간격 검사 우회: 로컬 데이터에 넣고 다시 읽음)
await p.evaluate(async () => { const d = await LocalDB._all(); ['b3', 'b12', 'b25', 'b40', 'b58', 'b70', 'b81'].forEach((bid, i) => d.stamps.push({ id: uuid(), visitorId: S.me.id, boothId: bid, at: Date.now() - (7 - i) * 120000 })); await LocalDB._save(d); S.myStamps = await DB.stampsOf(S.me.id); });
await p.evaluate(() => route()); await sleep(300);   // 해시가 이미 #/my 라 다시 그리기
check('앱 내 설문 모드 버튼', await p.evaluate(() => surveyMode() === 'app' && /설문 참여하고 교환권 받기/.test($('.voucher').textContent)));
await p.evaluate(() => location.hash = '#/survey'); await p.waitForSelector('#svSubmit');
check('문항 7개 렌더', await p.evaluate(() => $$('.sv-q').length === 7));
check('부스 칩 = 내 도장 7개', await p.evaluate(() => $$('.sv-chip').length === 7));
await p.click('#svSubmit'); await sleep(300);
check('미답변 제출 막힘', await p.evaluate(() => $$('.sv-q.bad').length === 6 && !S.me.surveyAt), await p.evaluate(() => $('#toast').textContent));
await p.evaluate(() => $$('.sv-q')[0].querySelector('.sv-scale button[data-v="4"]').click());
await p.evaluate(() => $$('.sv-chip')[2].click());
await p.evaluate(() => { const el = $$('.sv-q')[2]; el.querySelectorAll('.sv-opt')[0].click(); el.querySelectorAll('.sv-opt')[3].click(); });
await p.evaluate(() => $$('.sv-q')[3].querySelectorAll('.sv-opt')[1].click());
await p.evaluate(() => $$('.sv-q')[4].querySelectorAll('.sv-opt')[0].click());
await p.evaluate(() => $$('.sv-q')[5].querySelectorAll('.sv-opt')[0].click());
await p.fill('.sv-q textarea', '재밌었어요! 화장실이 좀 멀어요');
check('진행 표시 6/6', await p.evaluate(() => $('#svCnt').textContent === '6 / 6 답변'));
await p.click('#svSubmit'); await p.waitForSelector('#myQr', { timeout: 5000 });
check('제출 → 교환권', await p.evaluate(() => !!S.me.surveyAt));
const saved = await p.evaluate(async () => (await LocalDB._all()).surveys);
check('응답 저장 형식', saved.length === 1 && saved[0].answers.overall === 4 && saved[0].answers.best === '25' && saved[0].answers.why.length === 2 && /화장실/.test(saved[0].answers.free), JSON.stringify(saved[0]?.answers));
await p.evaluate(() => location.hash = '#/survey'); await sleep(300);
check('제출 후 #/survey 재진입 막힘', await p.evaluate(() => location.hash === '#/my'));

console.log('[2] 관리자 › 설문 탭 (문항 편집·결과·CSV, 로컬)');
const a = await ctx.newPage(); wire(a, 'admin'); await a.setViewportSize({ width: 1280, height: 900 });   // 로컬 모드 데이터는 컨텍스트(localStorage)별 → 방문객과 같은 컨텍스트
await a.goto(APP); await a.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
await a.evaluate(() => location.hash = '#/admin'); await a.waitForSelector('#pw'); await a.fill('#pw', '1234'); await a.keyboard.press('Enter'); await a.waitForFunction(() => S.admin); await a.waitForSelector('.stats');
await a.evaluate(() => location.hash = '#/admin/survey'); await a.waitForSelector('#sqSave');
check('문항 편집기 7개', await a.evaluate(() => $$('#sqList [data-i]').length === 7));
await a.click('#sqAdd'); await a.waitForFunction(() => $$('#sqList [data-i]').length === 8);
await a.fill('#sqList [data-i="7"] [data-f=title]', '점심은 어디서 먹었나요?'); await a.dispatchEvent('#sqList [data-i="7"] [data-f=title]', 'change');
await a.fill('#sqList [data-i="7"] [data-f=opts]', '집에서 싸옴\n매점\n안 먹음'); await a.dispatchEvent('#sqList [data-i="7"] [data-f=opts]', 'change');
await a.click('#sqSave'); await sleep(500);
check('저장 → SURVEY 8개', await a.evaluate(() => SURVEY.length === 8 && SURVEY[7].opts.length === 3), await a.evaluate(() => JSON.stringify(SURVEY[7])));
await a.click('#sqLoad'); await sleep(500);
check('결과 집계 렌더', await a.evaluate(() => /응답 <b>1<\/b>명/.test($('#sqRes').innerHTML) && /평균/.test($('#sqRes').textContent) && /화장실/.test($('#sqRes').textContent)));
const dl = a.waitForEvent('download'); await a.click('#sqCsv'); const file = await dl; const csv = fs.readFileSync(await file.path(), 'utf8');
check('CSV 헤더·행', /제출시각,학교,학년,학년군,성별,오늘 축전은/.test(csv) && /단구초,초4,초고,여,4,25,직접 만들어서 \| 신기한 걸 봐서/.test(csv), csv.split('\n')[1]?.slice(0, 120));
// 방문객 화면에 문항 8개 반영 (설정이 로컬 저장소에 있으므로 새 페이지에서)
const p3 = await ctx.newPage(); wire(p3, 'mobile2');
await p3.goto(APP); await p3.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
check('설문 링크 있으면 외부 모드', await p3.evaluate(() => { CONFIG.surveyUrl = 'https://x.y'; return surveyMode() === 'link'; }));
await ctx.close();

console.log('[3] 실서버: 관리자 설문 탭이 SQL 미실행 상태를 안내하는지');
const live = await b.newContext({ viewport: { width: 1280, height: 900 } }); const l = await live.newPage(); wire(l, 'live');
await l.goto('file:///' + DIR + '원주축전_스탬프앱_3.html'); await l.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
await l.evaluate(() => location.hash = '#/admin'); await l.waitForSelector('#pw'); await l.fill('#pw', '1234'); await l.keyboard.press('Enter'); await l.waitForFunction(() => S.admin); await l.waitForSelector('.stats');
await l.evaluate(() => location.hash = '#/admin/survey'); await l.waitForSelector('#sqLoad'); await l.click('#sqLoad'); await l.waitForFunction(() => !/불러오는 중/.test($('#sqRes').textContent), null, { timeout: 25000 });
const msg = await l.evaluate(() => $('#sqRes').textContent);
check('SQL 9절 안내 문구', /9절/.test(msg), msg.slice(0, 80));
await live.close();

await b.close();
console.log('\nERRORS', errs.length ? errs : 'none'); console.log('FAILS', fails.length ? fails : 'none');
process.exit(fails.length || errs.length ? 1 : 0);

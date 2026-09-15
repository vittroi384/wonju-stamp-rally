// 부스 참여자 명단: 앱 현황 탭(로컬 모드) + 대시보드(RPC 는 가짜 응답으로 대체 — SQL 적용 전에도 UI 검증)
import { chromium } from 'playwright'; import fs from 'fs';
const DIR = 'C:/dev/stamp-rally-v3/'; const src = fs.readFileSync(DIR + '원주축전_스탬프앱_3.html', 'utf8');
fs.writeFileSync(DIR + 'tests/_local.html', src.replace(/supabaseUrl: '[^']*'/, "supabaseUrl: ''").replace(/\.\/qrcode\.min\.js|\.\/jsQR\.js/g, m => '..' + m.slice(1)));
const fails = [], errs = []; const check = (n, ok, x = '') => { console.log((ok ? '  ✓ ' : '  ✗ ') + n + (x ? ' — ' + x : '')); if(!ok) fails.push(n); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const b = await chromium.launch({ channel: 'chrome' }); const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); p.on('pageerror', e => errs.push(e.message));
await p.goto('file:///' + DIR + 'tests/_local.html'); await p.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
await p.evaluate(async () => { const d = await LocalDB._all(); const mk = (name, school, stamps) => { const v = { id: uuid(), name, school, grade: '초4', gender: '여', consentedAt: Date.now(), createdAt: Date.now(), surveyAt: null, giftAt: null }; d.visitors.push(v); stamps.forEach((bid, i) => d.stamps.push({ id: uuid(), visitorId: v.id, boothId: bid, at: Date.now() - i * 60000 })); }; mk('김하늘', '가온초', ['b1', 'b2', 'b3']); mk('이서준', '나래중', ['b1']); mk('박지우', '가온초', ['b2']); await LocalDB._save(d); });
await p.evaluate(() => location.hash = '#/admin'); await p.waitForSelector('#pw'); await p.fill('#pw', '1234'); await p.keyboard.press('Enter'); await p.waitForFunction(() => S.admin); await p.waitForSelector('[data-bv]');
check('현황 표 줄에 data-bv', await p.evaluate(() => $$('[data-bv]').length) >= 90);
await p.click('[data-bv="b1"]'); await p.waitForSelector('#bvList table'); await sleep(200);
check('b1 시트: 2명', await p.evaluate(() => $('#bvCnt').textContent.startsWith('2명') && $$('#bvList tbody tr').length === 2));
check('도장 수 표시 (김하늘 3)', await p.evaluate(() => [...$$('#bvList tbody tr')].some(tr => tr.textContent.includes('김하늘') && tr.querySelector('.num').textContent === '3')));
await p.fill('#bvQ', '나래'); await sleep(100);
check('검색: 학교로 1명', await p.evaluate(() => $$('#bvList tbody tr').length === 1 && $('#bvCnt').textContent.includes('1명 / 전체 2명')));
await p.evaluate(() => closeSheet()); await p.click('[data-bv="b5"]'); await p.waitForSelector('#bvCnt'); await sleep(200);
check('없는 부스: 0명 안내', await p.evaluate(() => $('#bvCnt').textContent.startsWith('0명') && /없어요/.test($('#bvList').textContent)));
await p.evaluate(() => closeSheet());
// 대시보드: RPC 가짜 응답
const d = await b.newPage({ viewport: { width: 1400, height: 900 } }); d.on('pageerror', e => errs.push('dash ' + e.message));
const dsrc = fs.readFileSync(DIR + '운영대시보드.html', 'utf8');
await d.route(/rest\/v1\//, async r => { const u = r.request().url();
  if(/rpc\/admin_login/.test(u)) return r.fulfill({ contentType: 'application/json', body: 'true' });
  if(/rpc\/admin_booth_visitors/.test(u)){ const body = JSON.parse(r.request().postData()); const rows = body.bid === 'b1' ? [{ visitor_id: 'x', name: '김하늘', school: '가온초', grade: '초4', gender: '여', stamped_at: new Date().toISOString(), n: 3 }, { visitor_id: 'y', name: '이서준', school: '나래중', grade: '중1', gender: '남', stamped_at: new Date().toISOString(), n: 1 }] : []; return r.fulfill({ contentType: 'application/json', body: JSON.stringify(rows) }); }
  if(/rpc\/admin_dashboard/.test(u)) return r.fulfill({ contentType: 'application/json', body: JSON.stringify({ at: new Date().toISOString(), goal: 7, visitors: 3, active: 3, stamps: 5, new_15m: 0, stamps_15m: 0, achievers: 0, survey_done: 0, gift_done: 0, gift_15m: 0, per_booth: [{ booth_id: 'b1', n: 2, n15: 0, last_at: new Date().toISOString() }], per_10min: [], per_hour: [], by_grade: [], by_gender: [], top_schools: [], dist: [], recent: [], survey: null }) });
  if(/booths\?/.test(u)) return r.fulfill({ contentType: 'application/json', body: JSON.stringify([{ id: 'b1', number: '1', name: '테스트부스', category: 'sci', organization: '기관', zone: 'A', sort_order: 1 }, { id: 'b2', number: '2', name: '둘', category: 'sci', organization: '', zone: 'A', sort_order: 2 }]) });
  if(/settings\?/.test(u)) return r.fulfill({ contentType: 'application/json', body: '[]' });
  return r.fulfill({ contentType: 'application/json', body: '[]' }); });
await d.goto('file:///' + DIR + '운영대시보드.html'); await d.waitForSelector('#pw'); await d.fill('#pw', 'abcdefgh'); await d.keyboard.press('Enter'); await d.waitForSelector('#allBody tr[data-bv]', { timeout: 10000 });
check('대시보드 부스 표 줄 data-bv', await d.evaluate(() => $$('#allBody tr[data-bv]').length) === 2);
await d.click('#allBody tr[data-bv="b1"]'); await d.waitForFunction(() => $$('#bvBody tr').length === 2, null, { timeout: 5000 });
check('명단 카드 열림·2명', await d.evaluate(() => !$('#bvCard').hidden && $('#bvSub').textContent.startsWith('2명') && $('#bvTitle').textContent.includes('테스트부스')));
check('선택 줄 강조', await d.evaluate(() => $('#allBody tr[data-bv="b1"]').classList.contains('sel')));
await d.fill('#bvQ', '이서'); await sleep(100); check('검색 1명', await d.evaluate(() => $$('#bvBody tr').length === 1 && $('#bvSub').textContent.includes('1명 / 전체 2명')));
await d.click('#allBody tr[data-bv="b2"]'); await d.waitForFunction(() => /없어요/.test($('#bvBody').textContent), null, { timeout: 5000 }); check('다른 부스 → 0명', true);
await d.click('#bvClose'); check('닫기', await d.evaluate(() => $('#bvCard').hidden && !$('#allBody tr.sel')));
console.log('ERRS', errs); console.log('FAILS', fails.length ? fails : 'none'); await b.close(); fs.unlinkSync(DIR + 'tests/_local.html'); process.exit(fails.length || errs.length ? 1 : 0);

// 관리자 교환권 QR 스캔 (로컬 모드, 테스트 모드 코드 입력으로 검증)
import { chromium } from 'playwright'; import fs from 'fs';
const DIR = 'C:/dev/stamp-rally-v3/'; const src = fs.readFileSync(DIR + '원주축전_스탬프앱_3.html', 'utf8');
fs.writeFileSync(DIR + 'tests/_local.html', src.replace(/supabaseUrl: '[^']*'/, "supabaseUrl: ''").replace(/\.\/qrcode\.min\.js|\.\/jsQR\.js/g, m => '..' + m.slice(1)));
const fails = [], errs = []; const check = (n, ok, x = '') => { console.log((ok ? '  ✓ ' : '  ✗ ') + n + (x ? ' — ' + x : '')); if(!ok) fails.push(n); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const b = await chromium.launch({ channel: 'chrome' }); const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); p.on('pageerror', e => errs.push(e.message));
await p.goto('file:///' + DIR + 'tests/_local.html'); await p.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
// 방문객 3명: 완주+설문 / 완주+설문 전 / 완주 전
const ids = await p.evaluate(async () => { const d = await LocalDB._all(); const mk = (name, n, survey) => { const v = { id: uuid(), name, school: '가온초', grade: '초4', gender: '여', consentedAt: Date.now(), createdAt: Date.now(), surveyAt: survey ? Date.now() : null, giftAt: null }; d.visitors.push(v); for(let i = 0; i < n; i++) d.stamps.push({ id: uuid(), visitorId: v.id, boothId: 'b' + (i + 1), at: Date.now() }); return v.id; }; const a = mk('완주설문', 7, true), b2 = mk('완주만', 7, false), c = mk('진행중', 3, false); await LocalDB._save(d); return { a, b2, c }; });
await p.evaluate(() => location.hash = '#/admin'); await p.waitForSelector('#pw'); await p.fill('#pw', '1234'); await p.keyboard.press('Enter'); await p.waitForFunction(() => S.admin); await p.waitForSelector('.stats');
await p.evaluate(() => location.hash = '#/admin/gift'); await p.waitForSelector('#gScan'); await p.click('#gScan'); await p.waitForSelector('#scanManual');
check('스캐너 제목', await p.evaluate(() => $('#scan .scan-top .t').textContent) === '교환권 QR 스캔');
const scan = async text => { await p.fill('#scanManual', text); await p.click('#scanManualGo'); await sleep(400); };
await scan('WJ:' + ids.a);
check('완주+설문 → 수령 가능 카드', await p.evaluate(() => /수령 가능/.test($('#scanMsg').textContent) && !!$('#scanGive')));
await p.click('#scanGive'); await sleep(300);
check('수령 처리 → 저장', await p.evaluate(async id => { const v = (await LocalDB._all()).visitors.find(x => x.id === id); return !!v.giftAt; }, ids.a));
check('완료 안내 후 자동 재개', await p.evaluate(() => /수령 완료/.test($('#scanMsg').textContent)));
await sleep(1400); check('1.2초 뒤 다음 학생 대기', await p.evaluate(() => scanner.paused === false));
await p.waitForSelector('#scanManual'); await scan('WJ:' + ids.a);
check('같은 학생 다시 → 이미 받음, 버튼 없음', await p.evaluate(() => /이미/.test($('#scanMsg').textContent) && !$('#scanGive')));
await p.click('#scanNext'); await p.waitForSelector('#scanManual'); await scan('WJ:' + ids.b2);
check('설문 전 → 안내, 버튼 없음', await p.evaluate(() => /설문을 아직/.test($('#scanMsg').textContent) && !$('#scanGive')));
await p.click('#scanNext'); await p.waitForSelector('#scanManual'); await scan(ids.c.replace(/-/g, '').slice(-6).toUpperCase());   // 6자리 코드로
check('완주 전(코드 검색) → 도장 3/7 안내', await p.evaluate(() => /완주 전 \(도장 3\/7\)/.test($('#scanMsg').textContent)));
await p.click('#scanNext'); await p.waitForSelector('#scanManual'); await scan('https://example.com/?b=7&t=abc');
check('부스 QR 넣으면 거부', await p.evaluate(() => /교환권이 아니거나/.test($('#scanMsg').textContent)));
await p.evaluate(() => closeScanner()); await sleep(400);
check('닫으면 목록 갱신 (수령 1명)', await p.evaluate(() => /미수령 1/.test($('#main').textContent) && $$('[data-undo]').length === 1));
// 방문객 스캐너는 그대로 (부스 모드)
await p.evaluate(() => { location.hash = '#/'; }); await sleep(300); await p.evaluate(() => openScanner()); await p.waitForSelector('#scanManual');
check('방문객 스캐너는 부스 모드', await p.evaluate(() => $('#scan .scan-top .t').textContent === '부스 QR 스캔' && /부스 번호 입력/.test($('#scanMsg').textContent)));
await p.evaluate(() => closeScanner());
console.log('ERRS', errs); console.log('FAILS', fails.length ? fails : 'none'); await b.close(); fs.unlinkSync(DIR + 'tests/_local.html'); process.exit(fails.length || errs.length ? 1 : 0);

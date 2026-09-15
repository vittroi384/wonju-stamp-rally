// (1) 라이브러리 로더 CDN→로컬 폴백  (2) 시드 버전 매칭 시 부스 요청 생략 — 실서버 읽기만 (쓰기 없음)
import { chromium } from 'playwright'; import fs from 'fs';
const DIR = 'C:/dev/stamp-rally-v3/', APP = 'file:///' + DIR + '원주축전_스탬프앱_3.html';
const fails = [], errs = []; const check = (n, ok, x = '') => { console.log((ok ? '  ✓ ' : '  ✗ ') + n + (x ? ' — ' + x : '')); if(!ok) fails.push(n); };
const b = await chromium.launch({ channel: 'chrome' });
const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true }); const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message));
const reqs = []; p.on('request', r => reqs.push(r.url()));
await p.goto(APP); await p.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
check('seedVersion 0 → 서버에서 부스 받음', reqs.some(u => u.includes('/booths?')));
const ver = await p.evaluate(() => S.settingsRaw.boothsVersion); check('서버 boothsVersion 있음', !!ver, String(ver));
// 시드 버전을 서버 버전에 맞춘 복사본
const src = fs.readFileSync(DIR + '원주축전_스탬프앱_3.html', 'utf8');
fs.writeFileSync(DIR + 'tests/_seed.html', src.replace('seedVersion: 0,', `seedVersion: ${ver},`).replace(/\.\/qrcode\.min\.js|\.\/jsQR\.js/g, m => '..' + m.slice(1)));
reqs.length = 0; await p.goto('file:///' + DIR + 'tests/_seed.html'); await p.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
check('시드 버전 = 서버 버전 → 부스 요청 없음', !reqs.some(u => u.includes('/booths?')) && reqs.some(u => u.includes('/settings?')));
check('부스 95개는 그대로', await p.evaluate(() => S.booths.length) === 95);
// 라이브러리: CDN 에서 로드
reqs.length = 0; await p.evaluate(() => loadQRCode()); await p.waitForFunction(() => !!window.QRCode, null, { timeout: 8000 });
check('qrcode CDN(jsdelivr) 로드', reqs.some(u => u.includes('jsdelivr') && u.includes('qrcode')) && !reqs.some(u => u.includes('qrcode.min.js?v=')));
await p.evaluate(() => loadJsQR()); await p.waitForFunction(() => !!window.jsQR, null, { timeout: 8000 });
check('jsQR CDN 로드', reqs.some(u => u.includes('jsdelivr') && u.includes('jsqr')));
// CDN 막힌 상황: jsdelivr 차단 → 로컬 폴백
const p2 = await ctx.newPage(); p2.on('pageerror', e => errs.push('p2 ' + e.message)); await p2.route(/jsdelivr\.net\/npm\/(jsqr|qrcodejs)/, r => r.abort());
await p2.goto('file:///' + DIR + 'tests/_seed.html'); await p2.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
const t0 = Date.now(); await p2.evaluate(() => loadJsQR()); await p2.waitForFunction(() => !!window.jsQR, null, { timeout: 8000 });
check('CDN 차단 → 로컬 jsQR 폴백', true, `${Date.now() - t0}ms`);
// CDN 느린 상황(응답 안 옴): 3초 타임아웃 후 로컬
const p3 = await ctx.newPage(); await p3.route(/jsdelivr\.net\/npm\/(jsqr|qrcodejs)/, () => {});   // 영원히 대기 (폰트 CSS 는 정상)
await p3.goto('file:///' + DIR + 'tests/_seed.html'); await p3.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
const t1 = Date.now(); await p3.evaluate(() => loadQRCode()); await p3.waitForFunction(() => !!window.QRCode, null, { timeout: 10000 });
const dt = Date.now() - t1; check('CDN 무응답 → 3초 타임아웃 후 로컬 qrcode', dt >= 2800 && dt < 6000, dt + 'ms');
// 교환권 QR 은 lazy 로드로 그려지는지 (로컬 모드로)
fs.writeFileSync(DIR + 'tests/_local.html', src.replace(/supabaseUrl: '[^']*'/, "supabaseUrl: ''").replace(/\.\/qrcode\.min\.js|\.\/jsQR\.js/g, m => '..' + m.slice(1)));
const p4 = await ctx.newPage(); p4.on('pageerror', e => errs.push('p4 ' + e.message)); await p4.goto('file:///' + DIR + 'tests/_local.html'); await p4.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
await p4.evaluate(async () => { const d = await LocalDB._all(); const v = { id: uuid(), name: '테스트', school: '가온초', grade: '초4', gender: '여', consentedAt: Date.now(), createdAt: Date.now(), surveyAt: Date.now(), giftAt: null }; d.visitors.push(v); for(let i = 0; i < 7; i++) d.stamps.push({ id: uuid(), visitorId: v.id, boothId: 'b' + (i + 1), at: Date.now() }); await LocalDB._save(d); await store.set('wj:me', v.id); });
await p4.reload(); await p4.waitForFunction(() => S.me && S.myStamps.length === 7 && document.querySelector('#main')); await p4.evaluate(() => location.hash = '#/my'); await p4.waitForSelector('#myQr'); await p4.waitForFunction(() => $('#myQr').querySelector('img,canvas'), null, { timeout: 8000 });
check('교환권 QR 지연 로드 후 렌더', true);
console.log('ERRS', errs); console.log('FAILS', fails.length ? fails : 'none'); await b.close(); fs.unlinkSync(DIR + 'tests/_seed.html'); fs.unlinkSync(DIR + 'tests/_local.html'); process.exit(fails.length || errs.length ? 1 : 0);

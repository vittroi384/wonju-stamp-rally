// 공개 저장소 README 스크린샷 (더미 데이터만). 로컬 모드 앱 + 대시보드는 가짜 집계를 직접 render()
// 사용: node tests/shots_public.mjs   (저장소 루트에서. assets/ 에 저장)
import { chromium } from 'playwright';
import fs from 'fs';
const DIR = process.cwd().replace(/\\/g, '/') + '/', OUT = DIR + 'assets/';
const src = fs.readFileSync(DIR + '원주축전_스탬프앱_3.html', 'utf8');
fs.writeFileSync(DIR + 'tests/_local.html', src.replace(/supabaseUrl: '[^']*'/, "supabaseUrl: ''").replace(/\.\/qrcode\.min\.js|\.\/jsQR\.js/g, m => '..' + m.slice(1)));
const APP = 'file:///' + DIR + 'tests/_local.html';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const pick = a => a[Math.floor(Math.random() * a.length)];
const b = await chromium.launch({ channel: 'chrome' });
const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
const p = await ctx.newPage();
await p.goto(APP); await p.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
await p.evaluate(() => location.hash = '#/register'); await p.waitForSelector('#rLevel'); await sleep(300);
await p.click('#rLevel button[data-l="초"]'); await p.click('#rGrade button[data-n="4"]'); await p.fill('#rSchool', '가온초'); await p.fill('#rName', '김하늘');
await p.screenshot({ path: OUT + 'register.png' });
await p.click('#rGender button[data-g="여"]'); await p.check('#rConsent'); await p.click('#rGo'); await p.waitForFunction(() => S.me && S.me.id); await sleep(2600);   // 환영 토스트 사라질 때까지
// 새 기능 더미: 운영 시간·시간대 전환·대상·쉬는 중·화장실/휴지통 (2026-09-21)
await p.evaluate(async () => { S.booths[11].hours = '10:00~16:00'; S.booths[11].target = 'elem'; S.booths[4].target = 'secondary'; S.booths[20].variant = { at: '13:00', name: '오후 체험 부스', org: '', cat: '', desc: '' }; S.booths[6].hours = '13:00~16:00'; await DB.saveBooths(S.booths);
  const data = { ...(S.settingsRaw || {}), closedBooths: [S.booths[2].id, S.booths[8].id], facilities: [{ id: 'f1', type: 'wc', label: '화장실', x: 90, y: 905 }, { id: 'f2', type: 'bin', label: '휴지통', x: 1210, y: 905 }, { id: 'f3', type: 'wc', label: '화장실', x: 1215, y: 115 }] }; await DB.saveSettings(data); S.settingsRaw = data; });
await p.evaluate(() => location.hash = '#/map'); await p.waitForSelector('#mapSvg'); await sleep(900); await p.screenshot({ path: OUT + 'map-phone.png' });
await p.evaluate(() => location.hash = '#/map/12'); await sleep(1200); await p.screenshot({ path: OUT + 'map-route.png' });
await p.evaluate(() => location.hash = '#/booth/12'); await sleep(500); await p.screenshot({ path: OUT + 'booth.png' });
await p.evaluate(() => location.hash = '#/'); await sleep(500); await p.screenshot({ path: OUT + 'home.png' });
await p.evaluate(async () => { const d = await LocalDB._all(); ['b3', 'b12', 'b25', 'b40', 'b58', 'b70', 'b81'].forEach((bid, i) => d.stamps.push({ id: uuid(), visitorId: S.me.id, boothId: bid, at: Date.now() - (7 - i) * 900000 })); await LocalDB._save(d); S.myStamps = await DB.stampsOf(S.me.id); });
await p.evaluate(() => location.hash = '#/my'); await sleep(400); await p.screenshot({ path: OUT + 'my-stamps-done.png' });
await p.evaluate(() => location.hash = '#/survey'); await p.waitForSelector('#svSubmit'); await sleep(300);
await p.evaluate(() => { $$('.sv-q')[0].querySelector('.sv-scale button[data-v="5"]').click(); $$('.sv-chip')[2].click(); const el = $$('.sv-q')[2]; el.querySelectorAll('.sv-opt')[0].click(); el.querySelectorAll('.sv-opt')[3].click(); });
await sleep(2500); await p.screenshot({ path: OUT + 'survey.png' });
await p.evaluate(() => { $$('.sv-q')[3].querySelectorAll('.sv-opt')[1].click(); $$('.sv-q')[4].querySelectorAll('.sv-opt')[0].click(); $$('.sv-q')[5].querySelectorAll('.sv-opt')[0].click(); });
await p.click('#svSubmit'); await p.waitForSelector('#myQr'); await sleep(2500); await p.screenshot({ path: OUT + 'voucher.png' });
// 더미 응답 + 방문객 (관리자 화면용)
await p.evaluate(async () => { const d = await LocalDB._all(); const pick = a => a[Math.floor(Math.random() * a.length)];
  for(let i = 0; i < 40; i++){ const v = { id: uuid(), name: '방문객' + i, school: pick(['가온초', '라온중', '사랑고', '푸른초', '하늘고']), grade: pick(['초3', '초5', '중1', '중2', '고1', '성인']), gender: pick(['남', '여']), consentedAt: Date.now(), createdAt: Date.now() - i * 60000, surveyAt: Date.now(), giftAt: i % 3 ? null : Date.now() }; d.visitors.push(v);
    const n = 7 + (i % 3); const ids = new Set(); while(ids.size < n) ids.add('b' + (1 + Math.floor(Math.random() * 90))); [...ids].forEach(bid => d.stamps.push({ id: uuid(), visitorId: v.id, boothId: bid, at: Date.now() - Math.random() * 3600e3 }));
    d.surveys.push({ visitorId: v.id, at: Date.now(), answers: { overall: pick([3, 4, 4, 5, 5, 5]), best: pick(['3', '12', '25', '40', '58', '7', '35']), why: [pick(['직접 만들어서', '설명이 쉬웠어서', '결과물을 가져가서', '신기한 걸 봐서'])], count: pick(['쉬웠어요', '딱 적당했어요', '딱 적당했어요', '조금 힘들었어요']), learn: pick(['많이 재미있어졌어요', '조금 재미있어졌어요', '비슷해요']), again: pick(['꼭 올래요', '꼭 올래요', '아마 올 것 같아요']), free: pick(['', '', '부스가 많아서 좋았어요', '점심시간에 줄이 길었어요', '']) } }); }
  await LocalDB._save(d); });
const a = await ctx.newPage(); await a.setViewportSize({ width: 1280, height: 900 });
await a.goto(APP); await a.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
await a.evaluate(() => location.hash = '#/map'); await a.waitForSelector('#mapSvg'); await sleep(900); await a.screenshot({ path: OUT + 'map-pc.png' });
await a.evaluate(() => location.hash = '#/admin'); await a.waitForSelector('#pw'); await a.fill('#pw', '1234'); await a.keyboard.press('Enter'); await a.waitForFunction(() => S.admin); await a.waitForSelector('.stats');
await a.evaluate(() => location.hash = '#/admin/gift'); await a.waitForSelector('#gBody tr'); await sleep(2500); await a.screenshot({ path: OUT + 'admin-gift.png', clip: { x: 0, y: 0, width: 1280, height: 800 } });
await a.evaluate(() => location.hash = '#/admin/dash'); await a.waitForSelector('.stats'); await sleep(600); await a.screenshot({ path: OUT + 'admin-dash.png', clip: { x: 0, y: 0, width: 1280, height: 800 } });
await a.evaluate(() => location.hash = '#/admin/booths'); await a.waitForSelector('#bSave'); await sleep(400); await a.screenshot({ path: OUT + 'admin-booths.png', clip: { x: 0, y: 0, width: 1280, height: 800 } });
await a.evaluate(() => location.hash = '#/admin/map'); await a.waitForSelector('#facTools'); await a.waitForSelector('#mapSvg'); await sleep(900); await a.screenshot({ path: OUT + 'admin-map.png', clip: { x: 0, y: 0, width: 1280, height: 800 } });
await a.evaluate(() => location.hash = '#/admin/booths'); await a.waitForSelector('#bStatus'); await a.click('#bStatus'); await a.waitForSelector('#stGrid'); await sleep(500); await a.screenshot({ path: OUT + 'admin-status.png', clip: { x: 0, y: 0, width: 1280, height: 800 } }); await a.evaluate(() => closeSheet()); await sleep(300);
await a.evaluate(() => location.hash = '#/admin/qr'); await a.waitForSelector('.qrgrid'); await sleep(1200); await a.screenshot({ path: OUT + 'admin-qr.png', clip: { x: 0, y: 0, width: 1280, height: 800 } });
await a.evaluate(() => location.hash = '#/admin/event'); await a.waitForSelector('#evSave'); await sleep(300); await a.screenshot({ path: OUT + 'admin-event.png', clip: { x: 0, y: 0, width: 1280, height: 800 } });
await a.evaluate(() => location.hash = '#/admin/survey'); await a.waitForSelector('#sqSave'); await a.click('#sqLoad'); await sleep(2500); await a.screenshot({ path: OUT + 'admin-survey.png', clip: { x: 0, y: 0, width: 1280, height: 800 } });
await ctx.close();
// 대시보드: 로그인 없이 가짜 집계로 직접 render
const d = await b.newPage({ viewport: { width: 1600, height: 1000 } });
await d.goto('file:///' + DIR + '운영대시보드.html'); await d.waitForSelector('#pw');
const booths = JSON.parse(src.match(/const SEED_BOOTHS = (\[.*?\]);/)[1]);
await d.evaluate(({ booths }) => {
  const pick = a => a[Math.floor(Math.random() * a.length)];
  D.booths = booths.map(b => ({ id: 'b' + b.n, n: b.n, name: b.name, cat: b.cat, org: b.org, zone: b.zone || '' })); D.byId = Object.fromEntries(D.booths.map(b => [b.id, b]));
  D.survey = [{ id: 'overall', title: '오늘 축전은 전체적으로 어땠나요?' }];
  const now = Date.now();
  const per_booth = D.booths.map(b => { const n = Math.floor(Math.random() * 40); return { booth_id: b.id, n, n15: Math.floor(Math.random() * 9), last_at: n ? new Date(now - Math.random() * 3600e3).toISOString() : null }; });
  const stamps = per_booth.reduce((a, r) => a + r.n, 0);
  const data = { at: new Date().toISOString(), goal: 7, visitors: 412, active: 380, stamps, new_15m: 23, stamps_15m: 118, achievers: 96, survey_done: 81, gift_done: 64, gift_15m: 9,
    per_booth, per_10min: Array.from({ length: 30 }, (_, i) => ({ t: new Date(Math.floor((now - (29 - i) * 600e3) / 600e3) * 600e3).toISOString(), n: 20 + Math.floor(Math.random() * 60) })),
    per_hour: [10, 11, 12, 13, 14].map((h, i) => ({ h, n: [180, 320, 210, 290, 140][i] })),
    by_grade: [['초1', 30], ['초3', 55], ['초5', 70], ['중1', 90], ['중2', 60], ['고1', 40], ['성인', 67]].map(([g, n]) => ({ g, n })),
    by_gender: [{ g: '여', n: 214 }, { g: '남', n: 198 }],
    top_schools: [['가온초', 48], ['라온중', 41], ['사랑고', 33], ['푸른초', 30], ['하늘고', 27], ['나래초', 22], ['마루중', 19], ['아람고', 15], ['다솜초', 12], ['바다중', 9]].map(([s, n]) => ({ s, n })),
    dist: [1, 2, 3, 4, 5, 6, 7].map(k => ({ k, n: [40, 52, 61, 48, 45, 38, 96][k - 1] })),
    recent: Array.from({ length: 30 }, (_, i) => ({ booth_id: pick(D.booths).id, at: new Date(now - i * 20000).toISOString() })),
    survey: { n: 81, scales: [{ q: 'overall', avg: 4.32, n: 81 }] } };
  $('#login').hidden = true; $('#dash').hidden = false; $('#logout').hidden = false; D.basic = false; D.data = data; render(data);
}, { booths });
await sleep(800); await d.screenshot({ path: OUT + 'dashboard.png', clip: { x: 0, y: 0, width: 1600, height: 925 } });   // 상단(KPI·히트맵·추이)만
await d.locator('.card.c12:not([hidden])').first().screenshot({ path: OUT + 'dashboard-table.png' });
await b.close(); fs.unlinkSync(DIR + 'tests/_local.html'); console.log('done →', OUT);

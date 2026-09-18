// 화면 스크린샷 (로컬 모드): 완주 카드 → 앱 내 설문 → 교환권 / 관리자 설문 탭(편집·결과) / 대시보드
import { chromium } from 'playwright';
import fs from 'fs';
const PW = process.env.ADMIN_PW; if(!PW){ console.error('ADMIN_PW 환경변수에 관리자 비번 넣고 실행:  $env:ADMIN_PW="비번"; node tests/파일.mjs'); process.exit(1); }   // 대시보드는 실서버 로그인. 앱 쪽은 로컬 모드라 CONFIG.adminPassword(1234) 그대로
const DIR = 'C:/dev/stamp-rally-v3/', OUT = DIR + 'tests/out/';
const src = fs.readFileSync(DIR + '원주축전_스탬프앱_3.html', 'utf8');
fs.writeFileSync(DIR + 'tests/_local.html', src.replace("supabaseUrl: 'https://YOUR-PROJECT.supabase.co'", "supabaseUrl: ''").replace(/\.\/qrcode\.min\.js|\.\/jsQR\.js/g, m => '..' + m.slice(1)));
const APP = 'file:///' + DIR + 'tests/_local.html';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const b = await chromium.launch({ channel: 'chrome' });
const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
const p = await ctx.newPage();
await p.goto(APP); await p.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
await p.evaluate(() => location.hash = '#/register'); await p.waitForSelector('#rLevel');
await p.click('#rLevel button[data-l="초"]'); await p.click('#rGrade button[data-n="4"]');
await p.fill('#rSchool', '단구초'); await p.fill('#rName', '박지우'); await p.click('#rGender button[data-g="여"]'); await p.check('#rConsent');
await p.click('#rGo'); await p.waitForFunction(() => S.me && S.me.id);
await p.evaluate(async () => { const d = await LocalDB._all(); ['b3', 'b12', 'b25', 'b40', 'b58', 'b70', 'b81'].forEach((bid, i) => d.stamps.push({ id: uuid(), visitorId: S.me.id, boothId: bid, at: Date.now() - (7 - i) * 900000 })); await LocalDB._save(d); S.myStamps = await DB.stampsOf(S.me.id); });
await p.evaluate(() => location.hash = '#/my'); await sleep(400); await p.screenshot({ path: OUT + 'a1_완주_내스탬프.png' });
await p.evaluate(() => location.hash = '#/survey'); await p.waitForSelector('#svSubmit'); await sleep(300);
await p.evaluate(() => $$('.sv-q')[0].querySelector('.sv-scale button[data-v="5"]').click());
await p.evaluate(() => $$('.sv-chip')[2].click());
await p.evaluate(() => { const el = $$('.sv-q')[2]; el.querySelectorAll('.sv-opt')[0].click(); el.querySelectorAll('.sv-opt')[3].click(); });
await p.screenshot({ path: OUT + 'a2_설문_상단.png' });
await p.evaluate(() => $$('.sv-q')[3].querySelectorAll('.sv-opt')[1].click());
await p.evaluate(() => $$('.sv-q')[4].querySelectorAll('.sv-opt')[0].click());
await p.evaluate(() => $$('.sv-q')[5].querySelectorAll('.sv-opt')[0].click());
await p.fill('.sv-q textarea', '재밌었어요! 화장실이 좀 멀어요');
await p.evaluate(() => $$('.sv-q')[5].scrollIntoView()); await sleep(200);
await p.screenshot({ path: OUT + 'a3_설문_하단.png' });
await p.click('#svSubmit'); await p.waitForSelector('#myQr'); await sleep(1200); await p.screenshot({ path: OUT + 'a4_교환권.png' });
// 응답 몇 개 더 (결과 화면용)
await p.evaluate(async () => { const d = await LocalDB._all(); const pick = a => a[Math.floor(Math.random() * a.length)];
  for(let i = 0; i < 40; i++){ const v = { id: uuid(), name: '방문객' + i, school: pick(['가온초', '라온중', '사랑고', '푸른초', '하늘고']), grade: pick(['초3', '초5', '중1', '중2', '고1', '성인']), gender: pick(['남', '여']), consentedAt: Date.now(), createdAt: Date.now(), surveyAt: Date.now(), giftAt: null }; d.visitors.push(v);
    d.surveys.push({ visitorId: v.id, at: Date.now(), answers: { overall: pick([3, 4, 4, 5, 5, 5]), best: pick(['3', '12', '25', '40', '58', '7', '35']), why: [pick(['직접 만들어서', '설명이 쉬웠어서', '결과물을 가져가서', '신기한 걸 봐서'])], count: pick(['쉬웠어요', '딱 적당했어요', '딱 적당했어요', '조금 힘들었어요']), learn: pick(['많이 재미있어졌어요', '조금 재미있어졌어요', '비슷해요']), again: pick(['꼭 올래요', '꼭 올래요', '아마 올 것 같아요']), free: pick(['', '', '부스가 많아서 좋았어요', '점심시간에 줄이 길었어요', '']) } }); }
  await LocalDB._save(d); });
const a = await ctx.newPage(); await a.setViewportSize({ width: 1280, height: 900 });
await a.goto(APP); await a.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
await a.evaluate(() => location.hash = '#/admin'); await a.waitForSelector('#pw'); await a.fill('#pw', '1234'); await a.keyboard.press('Enter'); await a.waitForFunction(() => S.admin); await a.waitForSelector('.stats');
await a.evaluate(() => location.hash = '#/admin/survey'); await a.waitForSelector('#sqSave'); await a.click('#sqLoad'); await sleep(600);
await a.screenshot({ path: OUT + 'a5_관리자_설문탭.png', fullPage: true });
await ctx.close();
// 대시보드 (실서버, 기본 모드)
const d = await b.newContext({ viewport: { width: 1600, height: 1000 } }); const dp = await d.newPage();
await dp.goto('file:///' + DIR + '운영대시보드.html'); await dp.waitForSelector('#pw'); await dp.fill('#pw', PW); await dp.click('#pwGo');
await dp.waitForFunction(() => !$('#dash').hidden && $('#kpis').children.length > 0, null, { timeout: 20000 }); await sleep(800);
await dp.screenshot({ path: OUT + 'a6_대시보드.png', fullPage: true });
await b.close(); fs.unlinkSync(DIR + 'tests/_local.html'); console.log('done');

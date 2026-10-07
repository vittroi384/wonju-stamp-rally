// 처음 온 사람이 QR 먼저 찍고 등록 → 도장 화면으로 돌아와 찍히는지 (숫자·한글 부스 번호)
import { chromium } from 'playwright'; import fs from 'fs';
const DIR = 'C:/dev/stamp-rally-v3/';
const src = fs.readFileSync(DIR + '원주축전_스탬프앱_3.html', 'utf8');
fs.writeFileSync(DIR + 'tests/_local.html', src.replace(/supabaseUrl: '[^']*'/, "supabaseUrl: ''").replace(/\.\/qrcode\.min\.js|\.\/jsQR\.js/g, m => 'file:///' + DIR + m.slice(2)));
const fails = [], errs = []; const check = (n, ok, x = '') => { console.log((ok ? '  ✓ ' : '  ✗ ') + n + (x ? ' — ' + x : '')); if(!ok) fails.push(n); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const b = await chromium.launch();
for(const n of ['7', '본1']){
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 } }); const p = await ctx.newPage(); p.on('pageerror', e => errs.push(e.message));
  await p.goto('file:///' + DIR + 'tests/_local.html?b=' + encodeURIComponent(n)); await p.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main')); await sleep(500);
  const exists = await p.evaluate(n => !!S.booths.find(b => b.n === n), n); if(!exists){ console.log('  (부스 ' + n + ' 없음, 건너뜀)'); await ctx.close(); continue; }
  check(`[${n}] QR 링크로 들어오면 등록 화면 + 돌아갈 주소`, await p.evaluate(() => location.hash.startsWith('#/register/%2Fstamp%2F') && !!document.querySelector('#rLevel')), await p.evaluate(() => location.hash));
  await p.click('#rLevel button[data-l="중"]'); await p.click('#rGrade button[data-n="2"]'); await p.fill('#rSchool', '테스트중'); await p.fill('#rName', 'QR먼저'); await p.click('#rGender button[data-g="여"]'); await p.check('#rConsent'); await p.click('#rGo');
  await p.waitForFunction(() => S.me && S.me.id); await sleep(1500);
  check(`[${n}] 등록 후 도장 화면으로 돌아와 찍힘`, await p.evaluate(() => /체험 완료/.test(document.body.innerText) && S.myStamps.length === 1), await p.evaluate(() => location.hash));
  await ctx.close();
}
console.log('ERRS', errs); console.log('FAILS', fails.length ? fails : 'none'); await b.close(); fs.unlinkSync(DIR + 'tests/_local.html'); process.exit(fails.length || errs.length ? 1 : 0);

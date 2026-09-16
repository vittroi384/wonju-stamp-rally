// 관리자 › 부스 표 순서: ≡ 끌기 + 번호순 정렬 (로컬 모드)
import { chromium } from 'playwright'; import fs from 'fs';
const DIR = 'C:/dev/stamp-rally-v3/'; const src = fs.readFileSync(DIR + '원주축전_스탬프앱_3.html', 'utf8');
fs.writeFileSync(DIR + 'tests/_local2.html', src.replace(/supabaseUrl: '[^']*'/, "supabaseUrl: ''").replace(/\.\/qrcode\.min\.js|\.\/jsQR\.js/g, m => '..' + m.slice(1)));
const fails = [], errs = []; const check = (n, ok, x = '') => { console.log((ok ? '  ✓ ' : '  ✗ ') + n + (x ? ' — ' + x : '')); if(!ok) fails.push(n); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const b = await chromium.launch({ channel: 'chrome' }); const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); p.on('pageerror', e => errs.push(e.message));
await p.goto('file:///' + DIR + 'tests/_local2.html'); await p.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
await p.evaluate(() => location.hash = '#/admin'); await p.waitForSelector('#pw'); await p.fill('#pw', '1234'); await p.keyboard.press('Enter'); await p.waitForFunction(() => S.admin); await p.waitForSelector('.stats');
await p.evaluate(() => location.hash = '#/admin/booths'); await p.waitForSelector('[data-drag]');
const order = () => p.evaluate(() => $$('tbody tr[data-i]').map(tr => $('[data-f=n]', tr).value));
check('화살표 없음', await p.evaluate(() => !$('[data-up]') && !$('[data-down]') && !!$('#bSort')));
const before = await order(); console.log('  처음', before.slice(0, 5).join(','));
// 3번째 행을 맨 위로 끌기
const src3 = await p.locator('tr[data-i="2"] [data-drag]').boundingBox(); const dst = await p.locator('tr[data-i="0"]').boundingBox();
await p.mouse.move(src3.x + src3.width / 2, src3.y + src3.height / 2); await p.mouse.down();
for(let k = 1; k <= 8; k++) await p.mouse.move(src3.x + src3.width / 2, src3.y + (dst.y + 4 - src3.y) * k / 8); await sleep(50);
await p.mouse.up(); await sleep(300);
const after = await order(); console.log('  끌기 후', after.slice(0, 5).join(','));
check('3번째 행이 맨 위로', after[0] === before[2] && after[1] === before[0] && after[2] === before[1] && after.length === before.length);
check('행의 data-i 다시 0부터', await p.evaluate(() => $$('tbody tr[data-i]').every((tr, i) => +tr.dataset.i === i)));
// 다른 셀 편집 유지 + 아래로 끌기
await p.fill('tr[data-i="1"] [data-f=name]', '편집중'); const s1 = await p.locator('tr[data-i="1"] [data-drag]').boundingBox(); const d4 = await p.locator('tr[data-i="4"]').boundingBox();
await p.mouse.move(s1.x + s1.width / 2, s1.y + s1.height / 2); await p.mouse.down(); for(let k = 1; k <= 8; k++) await p.mouse.move(s1.x + s1.width / 2, s1.y + (d4.y + d4.height - 4 - s1.y) * k / 8); await sleep(50); await p.mouse.up(); await sleep(300);
const after2 = await order(); console.log('  아래로 끌기 후', after2.slice(0, 6).join(','));
check('2번째 행이 5번째로, 편집값 유지', after2[4] === after[1] && await p.evaluate(() => $('tr[data-i="4"] [data-f=name]').value === '편집중'));
// 번호순 정렬
await p.click('#bSort'); await sleep(300); const sorted = await order(); console.log('  정렬 후', sorted.slice(0, 5).join(','), '…', sorted.slice(-5).join(','));
const nums = sorted.filter(n => /^\d+$/.test(n)).map(Number); check('숫자 번호 오름차순, 글자 번호는 뒤', nums.every((v, i) => i === 0 || nums[i - 1] <= v) && sorted.findIndex(n => !/^\d+$/.test(n)) >= nums.length);
check('정렬 후에도 편집값 유지', await p.evaluate(() => $$('[data-f=name]').some(i => i.value === '편집중')));
await p.click('#bSave'); await sleep(500);
check('저장 후 순서 유지', JSON.stringify(await p.evaluate(() => S.booths.map(b => b.n))) === JSON.stringify(sorted) && await p.evaluate(() => S.booths.some(b => b.name === '편집중')));
await p.screenshot({ path: 'C:/Users/jjook/AppData/Local/Temp/claude/C--dev/70bba92c-1743-4543-8c0c-20fe1e790450/scratchpad/reorder.png' });
console.log('ERRS', errs); console.log('FAILS', fails.length ? fails : 'none'); await b.close(); fs.unlinkSync(DIR + 'tests/_local2.html'); process.exit(fails.length || errs.length ? 1 : 0);
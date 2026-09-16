// 관리자 › 부스 표 자료 [편집] 시트 (로컬 모드)
import { chromium } from 'playwright'; import fs from 'fs';
const DIR = 'C:/dev/stamp-rally-v3/'; const src = fs.readFileSync(DIR + '원주축전_스탬프앱_3.html', 'utf8');
fs.writeFileSync(DIR + 'tests/_local.html', src.replace(/supabaseUrl: '[^']*'/, "supabaseUrl: ''").replace(/\.\/qrcode\.min\.js|\.\/jsQR\.js/g, m => '..' + m.slice(1)));
const fails = [], errs = []; const check = (n, ok, x = '') => { console.log((ok ? '  ✓ ' : '  ✗ ') + n + (x ? ' — ' + x : '')); if(!ok) fails.push(n); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const b = await chromium.launch({ channel: 'chrome' }); const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); p.on('pageerror', e => errs.push(e.message));
await p.goto('file:///' + DIR + 'tests/_local.html'); await p.waitForFunction(() => S.booths.length > 0 && document.querySelector('#main'));
await p.evaluate(() => location.hash = '#/admin'); await p.waitForSelector('#pw'); await p.fill('#pw', '1234'); await p.keyboard.press('Enter'); await p.waitForFunction(() => S.admin); await p.waitForSelector('.stats');
await p.evaluate(() => location.hash = '#/admin/booths'); await p.waitForSelector('[data-media]');
check('표 머리 = 자료 열 하나', await p.evaluate(() => $$('thead th').map(t => t.textContent).join('|')) === '|번호|부스명|운영|분류|구역|소개|자료|');
check('행마다 칩 3개 + 편집', await p.evaluate(() => $$('tr[data-i="0"] .mchip').length === 3 && !!$('tr[data-i="0"] [data-media]')));
check('처음엔 칩 모두 꺼짐', await p.evaluate(() => $$('tr[data-i="0"] .mchip.on').length === 0));
const tableW = await p.evaluate(() => $('.table').scrollWidth); console.log('  표 너비', tableW);
await p.click('tr[data-i="0"] [data-media]'); await p.waitForSelector('#sheet.show #mOk');
check('시트 제목에 번호·이름', await p.evaluate(() => /^1 · /.test($('#sheet .h-sec').textContent)));
check('영상 미리보기 안내', await p.evaluate(() => /주소를 넣으면/.test($('#mVideoPv').textContent)));
await p.fill('#mVideo', 'https://youtu.be/dQw4w9WgXcQ'); await sleep(100);
check('유튜브 썸네일 미리보기', await p.evaluate(() => ($('#mVideoPv img') || {}).src === 'https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg'));
await p.fill('#mVideo', 'https://naver.com'); await sleep(100);
check('유튜브 아닌 주소 경고', await p.evaluate(() => /아닌 것 같아요/.test($('#mVideoPv').textContent)));
await p.fill('#mVideo', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
await p.fill('#mPdf', 'https://example.com/docs/booth-guide.pdf'); await sleep(200);
check('PDF 파일명·보기·지우기 표시', await p.evaluate(() => $('#mPdfName').textContent === 'booth-guide.pdf' && !$('#mPdfOpen').hidden && !$('#mPdfClear').hidden && $('#mPdfOpen').href === 'https://example.com/docs/booth-guide.pdf'));
await p.click('#mPdfClear'); await sleep(100);
check('PDF 지우기', await p.evaluate(() => $('#mPdf').value === '' && $('#mPdfOpen').hidden && $('#mPdfName').textContent === '아직 없어요'));
await p.fill('#mPdf', 'https://example.com/a.pdf');
// 사진 업로드 (로컬 모드 → IndexedDB local:)
await p.setInputFiles('#mImgFile', { name: 'pic.png', mimeType: 'image/png', buffer: Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==', 'base64') });
await p.waitForFunction(() => $('#mImg').value.startsWith('local:')); await sleep(300);
check('사진 올리면 주소 채워지고 미리보기', await p.evaluate(() => !!$('#mImgPv img') && !$('#mImgClear').hidden));
await p.click('#mOk'); await sleep(400);
check('시트 닫힘', await p.evaluate(() => !$('#sheet').classList.contains('show')));
check('행 hidden 값 반영', await p.evaluate(() => { const tr = $('tr[data-i="0"]'); return $('[data-f=video]', tr).value === 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' && $('[data-f=pdf]', tr).value === 'https://example.com/a.pdf' && $('[data-f=img]', tr).value.startsWith('local:'); }));
check('칩 3개 켜짐', await p.evaluate(() => $$('tr[data-i="0"] .mchip.on').length === 3));
// 다른 셀 편집 유지되는지 + 저장
await p.fill('tr[data-i="1"] [data-f=name]', '이름바꿈'); await p.click('tr[data-i="1"] [data-media]'); await p.waitForSelector('#sheet.show #mOk'); await p.click('#mOk'); await sleep(400);
check('시트 열고 닫아도 다른 셀 편집 유지', await p.evaluate(() => $('tr[data-i="1"] [data-f=name]').value === '이름바꿈'));
await p.click('#bSave'); await sleep(500);
check('저장 후 값 유지·칩 켜짐', await p.evaluate(() => S.booths[0].video.includes('dQw4w9WgXcQ') && S.booths[0].pdf === 'https://example.com/a.pdf' && S.booths[1].name === '이름바꿈' && $$('tr[data-i="0"] .mchip.on').length === 3));
// 다시 열면 값이 들어 있는지
await p.click('tr[data-i="0"] [data-media]'); await p.waitForSelector('#sheet.show #mOk'); await sleep(300);
check('재편집 시 값 채워짐', await p.evaluate(() => $('#mVideo').value.includes('dQw4w9WgXcQ') && $('#mPdf').value === 'https://example.com/a.pdf' && !!$('#mImgPv img')));
await p.screenshot({ path: 'C:/Users/jjook/AppData/Local/Temp/claude/C--dev/70bba92c-1743-4543-8c0c-20fe1e790450/scratchpad/media_sheet.png' });
await p.evaluate(() => closeSheet()); await sleep(400);
await p.screenshot({ path: 'C:/Users/jjook/AppData/Local/Temp/claude/C--dev/70bba92c-1743-4543-8c0c-20fe1e790450/scratchpad/booth_table.png' });
// 방문객 부스 소개에 반영
const bn = await p.evaluate(() => S.booths[0].n); await p.evaluate(n => location.hash = '#/booth/' + n, bn); await sleep(800);
check('방문객 부스 소개: 영상·PDF 버튼', await p.evaluate(() => !!$('.yt iframe') && !!$('#bPdf')));
console.log('ERRS', errs); console.log('FAILS', fails.length ? fails : 'none'); await b.close(); fs.unlinkSync(DIR + 'tests/_local.html'); process.exit(fails.length || errs.length ? 1 : 0);
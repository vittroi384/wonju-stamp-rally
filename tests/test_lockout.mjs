// 관리자 비번 실패 잠금 (실서버, 11절 적용 후). 틀린 비번 10번 → 1분 잠김 → 맞는 비번도 거절 → 풀린 뒤 정상. 데이터 변경 없음
// 사용: node test_lockout.mjs <맞는 비번>
const fs = await import('fs'); const src = fs.readFileSync('C:/dev/stamp-rally-v3/원주축전_스탬프앱_3.html', 'utf8');
const URL_ = src.match(/supabaseUrl: '([^']+)'/)[1], KEY = src.match(/supabaseAnonKey: '([^']+)'/)[1], PW = process.argv[2] || '1234';
const fails = []; const check = (n, ok, x = '') => { console.log((ok ? '  ✓ ' : '  ✗ ') + n + (x ? ' — ' + x : '')); if(!ok) fails.push(n); };
async function rpc(fn, args){ const t0 = performance.now(); const r = await fetch(`${URL_}/rest/v1/rpc/${fn}`, { method: 'POST', headers: { apikey: KEY, Authorization: 'Bearer ' + KEY, 'Content-Type': 'application/json' }, body: JSON.stringify(args) }); const ms = Math.round(performance.now() - t0); const txt = await r.text(); let b = null; try{ b = JSON.parse(txt); }catch(e){} return { ok: r.ok, body: b, msg: b?.message || '', ms }; }
const sleep = ms => new Promise(r => setTimeout(r, ms));
let r = await rpc('admin_login', { pw: PW }); check('맞는 비번 → true', r.ok && r.body === true, r.ms + 'ms');
r = await rpc('admin_login', { pw: 'wrong-' + Date.now() }); check('틀린 비번 → false (예외 아님, 지연 없음)', r.ok && r.body === false && r.ms < 400, r.ms + 'ms');
r = await rpc('admin_counts', { pw: 'wrong' }); check('다른 관리자 RPC 틀린 비번 → ADMIN_UNAUTHORIZED 즉시', !r.ok && /ADMIN_UNAUTHORIZED/.test(r.msg) && r.ms < 400, r.ms + 'ms');
r = await rpc('add_stamp', { vid: '00000000-0000-0000-0000-000000000000', bid: 'b1', tok: 'x' }); check('BAD_TOKEN 지연 없음', !r.ok && /BAD_TOKEN/.test(r.msg) && r.ms < 400, r.ms + 'ms');
r = await rpc('visitor_recover', { code: 'zzzzzz', nm: '없음' }); check('recover 실패 지연 없음', r.ok && Array.isArray(r.body) && r.body.length === 0 && r.ms < 400, r.ms + 'ms');
for(let i = 0; i < 9; i++) await rpc('admin_login', { pw: 'wrong' + i });   // 위 1번 + 9번 = 10번째에서 잠김
r = await rpc('admin_login', { pw: PW }); const m = r.msg.match(/ADMIN_LOCKED:(\d+)/); check('10회 실패 후 맞는 비번도 ADMIN_LOCKED:초', !r.ok && !!m, r.msg);
r = await rpc('admin_counts', { pw: PW }); check('잠긴 동안 다른 관리자 RPC 도 잠김', !r.ok && /ADMIN_LOCKED/.test(r.msg), r.msg);
r = await rpc('admin_dashboard', { pw: PW }); check('대시보드 RPC 도 잠김', !r.ok && /ADMIN_LOCKED/.test(r.msg));
const wait = (m ? +m[1] : 60) + 2; console.log(`  … ${wait}초 대기`); await sleep(wait * 1000);
r = await rpc('admin_login', { pw: PW }); check('잠금 풀린 뒤 맞는 비번 → true', r.ok && r.body === true, r.ms + 'ms');
r = await rpc('admin_counts', { pw: PW }); check('관리자 RPC 정상', r.ok);
console.log('FAILS', fails.length ? fails : 'none'); process.exit(fails.length ? 1 : 0);

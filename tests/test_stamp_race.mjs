// 도장 간격 검사 경합 (실서버, add_stamp 행 잠금 적용 후). 방문객 하나가 부스 7개 링크를 동시에 열어도 도장은 1개만 찍히고
// 나머지 6개는 TOO_FAST 여야 한다. 적용 전에는 7개가 전부 들어간다(이 테스트가 그걸 잡아낸다).
// 사용: node tests/test_stamp_race.mjs <관리자 비번>   (토큰 목록을 받기 위해 비번이 필요)
// 데이터: 이름 'TEST-race-…' 방문객 1명 + 도장 1개가 남는다. admin_reset 은 쓰지 않는다. 행사 전 초기화 때 함께 지워진다.
const fs = await import('fs'); const src = fs.readFileSync('C:/dev/stamp-rally-v3/원주축전_스탬프앱_3.html', 'utf8');
const URL_ = src.match(/supabaseUrl: '([^']+)'/)[1], KEY = src.match(/supabaseAnonKey: '([^']+)'/)[1], PW = process.argv[2] || process.env.ADMIN_PW;
if(!PW){ console.error('비번 필요: node tests/test_stamp_race.mjs 비번  또는 $env:ADMIN_PW'); process.exit(1); }
const fails = []; const check = (n, ok, x = '') => { console.log((ok ? '  ✓ ' : '  ✗ ') + n + (x ? ' — ' + x : '')); if(!ok) fails.push(n); };
async function rpc(fn, args){ const t0 = performance.now(); const r = await fetch(`${URL_}/rest/v1/rpc/${fn}`, { method: 'POST', headers: { apikey: KEY, Authorization: 'Bearer ' + KEY, 'Content-Type': 'application/json' }, body: JSON.stringify(args) }); const ms = Math.round(performance.now() - t0); const txt = await r.text(); let b = null; try{ b = JSON.parse(txt); }catch(e){} return { ok: r.ok, body: b, msg: b?.message || '', ms }; }

const N = 7;
let r = await rpc('admin_booth_tokens', { pw: PW }); check('부스 토큰 목록', r.ok && Array.isArray(r.body) && r.body.length >= N, r.ok ? r.body.length + '개' : r.msg);
if(!r.ok) { console.log('FAILS', fails); process.exit(1); }
const booths = r.body.slice(0, N);

r = await rpc('visitor_create', { nm: 'TEST-race-' + Date.now().toString(36), school: 'TEST', grade: '1', gender: 'M' });
check('테스트 방문객 생성', r.ok && Array.isArray(r.body) && r.body[0]?.id, r.msg);
const vid = r.body[0].id;

// 핵심: 7개 부스에 동시에 add_stamp. 잠금이 있으면 1개만 ok, 6개는 TOO_FAST.
const results = await Promise.all(booths.map(b => rpc('add_stamp', { vid, bid: b.booth_id, tok: b.token })));
const okCount = results.filter(x => x.ok && x.body?.ok).length;
const tooFast = results.filter(x => !x.ok && /TOO_FAST/.test(x.msg)).length;
const other = results.filter(x => !(x.ok && x.body?.ok) && !/TOO_FAST/.test(x.msg));
check(`동시 ${N}건 중 도장 1개만 성공`, okCount === 1, `ok ${okCount}`);
check(`나머지 ${N - 1}건은 TOO_FAST`, tooFast === N - 1, `TOO_FAST ${tooFast}` + (other.length ? ', 기타 ' + other.map(x => x.msg || x.body?.dup && 'dup').join('|') : ''));

r = await rpc('visitor_stamps', { vid }); check('서버에 남은 도장 1개', r.ok && Array.isArray(r.body) && r.body.length === 1, r.ok ? r.body.length + '개' : r.msg);

// 같은 부스 재요청은 dup, 다른 부스는 아직 TOO_FAST
const first = results.find(x => x.ok && x.body?.ok)?.body?.stamp?.booth_id;
if(first){ r = await rpc('add_stamp', { vid, bid: first, tok: booths.find(b => b.booth_id === first).token }); check('같은 부스 재요청 → dup', r.ok && r.body?.dup === true); }
const otherBooth = booths.find(b => b.booth_id !== first);
r = await rpc('add_stamp', { vid, bid: otherBooth.booth_id, tok: otherBooth.token }); check('다른 부스 90초 안 → TOO_FAST', !r.ok && /TOO_FAST:\d+/.test(r.msg), r.msg);

console.log('FAILS', fails.length ? fails : 'none'); process.exit(fails.length ? 1 : 0);

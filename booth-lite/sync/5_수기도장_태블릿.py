# 5단계: 수기 도장을 '부스 고정 태블릿' 흐름으로 교체 + 대시보드 히트맵 숨김. 4단계 뒤에 실행
import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
start = s.index("/* 수기 도장(관리자 › 수기 도장, 미니 모드)")
end = s.index("/* 부스 편집 목록(카드 한 줄 = 부스 하나")
fn = r"""/* 수기 도장(관리자 › 수기 도장 · 미니 모드) — 폰 없는 어린이용 '부스 태블릿'.
   관리자로 로그인한 태블릿이 부스 QR 을 찍으면(앱 스캐너·카메라 앱 모두 renderStamp → 여기) 그 부스에 고정(sessionStorage wj:manual_booth).
   흐름: 이름/코드 치면 바로 목록 → [도장] 한 번 → 큰 확인 화면(도장 수·코드, 5초 뒤 자동) → 다음 어린이. 처음이면 [처음 왔어요] → 등록 항목 입력 → 등록+도장 한 번에.
   등록은 visitor_create(S.me 는 안 건드림), 도장은 admin_add_stamp(토큰·간격 검사 없음). 부스를 바꾸려면 [부스 바꾸기] 또는 다른 부스 QR */
function admManual(boothN){
  const booths = S.booths.filter(hasStamp), KEY = 'wj:manual_booth', goal = CONFIG.stampGoal;
  let cur = booths.find(b => b.n === boothN) || (boothN ? null : booths.find(b => b.n === sessionStorage.getItem(KEY))) || null;
  const pickScan = () => openScanner({ title: '부스 QR 스캔', hint: '<b>부스 앞 QR을 네모 안에</b>인식되면 이 태블릿이 그 부스로 고정돼요',
    onCode: async text => { const n = parseBoothQR(text), b = n && (boothByN(n) || boothByN(String(parseInt(n)))); if(!b || !hasStamp(b)){ $('#scanMsg').innerHTML = `<b>부스 QR이 아니에요</b><button class="btn sun sm" id="scanNext">다시 찍기</button>`; $('#scanNext').onclick = scanner.resume; return; } closeScanner(); go(admPath('/manual/' + encodeURIComponent(b.n)), true); } });
  if(!cur){   // 1) 부스 고르기
    sessionStorage.removeItem(KEY);
    admShell('manual', `
      <div class="card" style="display:flex;flex-direction:column;gap:12px">
        <div><div class="h-sec" style="margin:0">이 태블릿은 어느 부스인가요?</div><p class="small muted" style="margin-top:4px;line-height:1.6">폰이 없는 어린이는 부스에서 이 태블릿으로 도장을 찍어요. 부스를 한 번 고르면 이 탭에 고정돼요.</p></div>
        <button class="btn blue full" id="mScan">${I.qr} 부스 QR 찍어서 고르기</button>
        <div class="chips" style="margin:0;padding:0;flex-wrap:wrap;overflow:visible">${booths.map(b => `<button class="chip" data-pick="${esc(b.n)}">${esc(b.n)}번 · ${esc(b.name)}</button>`).join('')}</div>
      </div>`);
    $('#mScan').onclick = pickScan;
    $$('[data-pick]').forEach(c => c.onclick = () => go(admPath('/manual/' + encodeURIComponent(c.dataset.pick)), true));
    return;
  }
  sessionStorage.setItem(KEY, cur.n);
  admShell('manual', `
    <div class="card" style="display:flex;align-items:center;gap:10px;padding:12px 16px">
      <div class="grow"><div class="small muted">이 태블릿은</div><div id="mCur" style="font-size:19px;font-weight:900;letter-spacing:-.01em">${esc(cur.n)}번 · ${esc(cur.name)}</div></div>
      <button class="btn xs line" id="mChange">부스 바꾸기</button>
    </div>
    <div class="card" id="mPanel"></div>`);
  $('#mChange').onclick = () => { sessionStorage.removeItem(KEY); go(admPath('/manual'), true); };
  const panel = $('#mPanel');
  const vinfo = v => vCols().map(c => c.get(v)).filter(Boolean).join(' · ');
  /* 찾기 화면: 두 글자부터 자동 검색(350ms), 결과 한 줄 = 이름·항목·코드·도장 수 + [도장] */
  const showSearch = () => {
    panel.innerHTML = `
      <div class="h-sec" style="margin:0 0 10px">누구에게 ${esc(cur.n)}번 도장을 찍을까요?</div>
      <input class="inp" id="mq" placeholder="이름 또는 6자리 코드" autocomplete="off" style="font-size:19px;padding:14px 16px;font-weight:700">
      <div id="mRes" style="margin-top:8px"></div>
      <button class="btn blue full" id="mNew" style="margin-top:14px">처음 왔어요 · 새로 등록하고 도장</button>`;
    const inp = $('#mq'); let timer, seq = 0;
    const search = async () => {
      const q = inp.value.trim(); if(q.length < 2){ $('#mRes').innerHTML = q ? '<div class="small muted" style="padding:6px 2px">두 글자 이상 적어주세요</div>' : ''; return; }
      const my = ++seq; $('#mRes').innerHTML = '<div class="empty">찾는 중…</div>';
      let rows; try{ rows = await DB.findVisitor(q); }catch(e){ if(my === seq) $('#mRes').innerHTML = `<div class="empty">${esc(e.message)}</div>`; return; }
      if(my !== seq) return;
      $('#mRes').innerHTML = rows.length ? rows.map(v => `<div class="vrow"><div class="grow"><b style="font-size:17px">${esc(v.name)}</b> <span class="small muted">${esc(vinfo(v))}</span><div class="small muted">코드 <b style="letter-spacing:.08em">${shortCode(v.id)}</b> · 도장 ${v.n}/${goal}</div></div><button class="btn sun" data-stamp="${v.id}">도장</button></div>`).join('')
        : '<div class="empty">없어요. 처음 왔으면 아래 [새로 등록]을 눌러주세요</div>';
      $$('[data-stamp]').forEach(btn => btn.onclick = () => { btn.disabled = true; doStamp(rows.find(x => x.id === btn.dataset.stamp)); });
    };
    inp.oninput = () => { clearTimeout(timer); timer = setTimeout(search, 350); };
    inp.onkeydown = e => { if(e.key === 'Enter'){ clearTimeout(timer); search(); } };
    $('#mNew').onclick = showNew;
    setTimeout(() => inp.focus(), 50);
  };
  /* 도장 → 확인 화면. 완주면 confetti. 5초 뒤(또는 [다음]) 찾기 화면으로 */
  const doStamp = async v => {
    let r; try{ r = await DB.adminAddStamp(v.id, cur.id); }catch(e){ toast(e.message); return showSearch(); }
    const n = (v.n || 0) + (r.dup ? 0 : 1), done = n >= goal;
    if(done && !r.dup) confetti();
    panel.innerHTML = `<div class="stampscreen" id="mDone" style="padding-top:6px">
      <div class="bigstamp ${r.dup ? 'dup' : ''}" style="width:170px;height:170px"><div><div class="n">${esc(cur.n)}</div><div class="t">${r.dup ? '이미 찍었어요' : '도장 완료'}</div></div></div>
      <div><div class="stamp-h">${esc(v.name)} · 도장 ${n}/${goal}${done ? ' 완주! 🎉' : ''}</div>
        <p class="stamp-p" style="margin-top:6px">${done ? '운영본부에서 선물을 받아가세요' : `다음 부스에서는 이름이나 코드 <b style="letter-spacing:.1em">${shortCode(v.id)}</b> 를 말하면 돼요`}</p></div>
      <button class="btn blue full" style="max-width:340px" id="mNext">다음 어린이</button>
      <div class="small muted" id="mCnt">5초 뒤 자동으로 넘어가요</div></div>`;
    let left = 5; const t = setInterval(() => { const c = $('#mCnt'); if(!c) return clearInterval(t); if(--left <= 0){ clearInterval(t); showSearch(); } else c.textContent = `${left}초 뒤 자동으로 넘어가요`; }, 1000);
    $('#mNext').onclick = () => { clearInterval(t); showSearch(); };
  };
  /* 처음 온 어린이: 등록 항목(행사 설정에서 켠 것) + 이름 → 등록하고 바로 도장 */
  const showNew = () => {
    panel.innerHTML = `
      <div class="h-sec" style="margin:0 0 10px">처음 온 어린이 등록</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        ${regFieldsHTML('n')}
        <div class="field"><label>이름</label><input class="inp" id="nName" placeholder="홍길동" maxlength="20" autocomplete="off"></div>
        <div class="row" style="gap:8px"><button class="btn blue grow" id="nGo">등록하고 ${esc(cur.n)}번 도장</button><button class="btn line" id="nBack">뒤로</button></div>
      </div>`;
    $('#nBack').onclick = showSearch;
    const first = panel.querySelector('input'); if(first) setTimeout(() => first.focus(), 50);
    $('#nGo').onclick = async () => {
      const name = $('#nName').value.trim(), f = readRegFields('n'); if(f.err) return toast(f.err), $(f.focus).focus();
      if(!name) return toast('이름을 적어주세요'), $('#nName').focus();
      $('#nGo').disabled = true;
      try{ const v = await DB.createVisitor({ name, school: f.school, grade: f.grade, gender: f.gender }); doStamp({ ...v, n: 0 }); }
      catch(e){ $('#nGo').disabled = false; toast('등록에 실패했어요. 다시 눌러주세요'); }
    };
  };
  showSearch();
}
"""
s = s[:start] + fn + s[end:]
# 결과 줄 스타일
old = ".adm-nav button.on{background:var(--ink);color:#fff}"
assert s.count(old) == 1
s = s.replace(old, old + "\n.vrow{display:flex;align-items:center;gap:10px;padding:10px 2px;border-bottom:1px solid var(--line-2)}.vrow:last-child{border-bottom:0}   /* 수기 도장 검색 결과 한 줄 */")
io.open(p,'w',encoding='utf-8',newline='\n').write(s)

# 대시보드: 히트맵 카드 숨김(요소는 남겨 JS 가 안 깨지게), 추이 카드 전체 폭
p=r'C:\dev\booth-lite\운영대시보드.html'
d=io.open(p,encoding='utf-8').read()
if 'class="card c7" hidden' in d: print('dashboard already patched'); raise SystemExit(0)
old='    <div class="card c7">\n      <div class="h"><div><div class="t">배치도 히트맵</div>'
assert d.count(old)==1
d=d.replace(old,'    <div class="card c7" hidden>   <!-- booth-lite: 지도 없음 → 히트맵 숨김 (요소는 남겨 둠) -->\n      <div class="h"><div><div class="t">배치도 히트맵</div>')
old='    <div class="card c5">\n      <div class="h"><div><div class="t">도장 추이</div>'
assert d.count(old)==1
d=d.replace(old,'    <div class="card c5" style="grid-column:1/-1">\n      <div class="h"><div><div class="t">도장 추이</div>')
io.open(p,'w',encoding='utf-8',newline='\n').write(d)
print('ok')

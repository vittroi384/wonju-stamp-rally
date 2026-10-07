# 6단계: 방문객 번호표(visitors.no, SQL 16절) + 수기 도장 화면 UI 개선. 5단계 뒤에 실행
import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
def rep(old,new):
    global s
    assert s.count(old)==1, (s.count(old), old[:100])
    s=s.replace(old,new,1)

# ── 방문객 객체에 번호(no). 서버는 SQL 16절(serial) 이 매김, 로컬 모드는 max+1
rep("_v(r){ return r&&{id:r.id,name:r.name,school:r.school,grade:r.grade||'',gender:r.gender||'',",
    "_v(r){ return r&&{id:r.id,name:r.name,no:r.no??null,school:r.school,grade:r.grade||'',gender:r.gender||'',")
rep("async createVisitor({name,school,grade,gender}){ const d=await this._all(); const v={id:uuid(),name,school,grade:grade||'',gender:gender||'',",
    "async createVisitor({name,school,grade,gender}){ const d=await this._all(); const v={id:uuid(),no:d.visitors.reduce((m,x)=>Math.max(m,x.no||0),0)+1,name,school,grade:grade||'',gender:gender||'',")
rep("return d.visitors.filter(v=>v.name.toLowerCase().includes(q)||(v.school||'').toLowerCase().includes(q)||shortCode(v.id).toLowerCase()===q)",
    "return d.visitors.filter(v=>v.name.toLowerCase().includes(q)||(v.school||'').toLowerCase().includes(q)||shortCode(v.id).toLowerCase()===q||String(v.no)===q)")
# 방문객 표시용: 번호 있으면 '23번', 없으면(SQL 16절 전) 6자리 코드
rep("function readAge(sel){", "const vTag = v => v && v.no ? `${v.no}번` : shortCode(v.id);   // 번호표(SQL 16절) 있으면 번호, 아니면 코드\nfunction readAge(sel){")

# ── 스타일
old = ".vrow{display:flex;align-items:center;gap:10px;padding:10px 2px;border-bottom:1px solid var(--line-2)}.vrow:last-child{border-bottom:0}   /* 수기 도장 검색 결과 한 줄 */"
rep(old, """/* 수기 도장(부스 태블릿) */
.tb-head{display:flex;align-items:center;gap:14px;padding:14px 18px;border-radius:22px;background:linear-gradient(135deg,var(--ink),#2F3D73);color:#fff;box-shadow:var(--sh-1)}
.tb-head .bn{font-size:32px;font-weight:900;line-height:1;background:var(--sun);color:var(--ink);border-radius:16px;padding:12px 14px;min-width:66px;text-align:center}
.tb-head .bname{font-size:19px;font-weight:800;letter-spacing:-.01em}.tb-head .bsub{font-size:12.5px;opacity:.72;margin-bottom:2px}
.tb-head .chg{border:1.5px solid rgba(255,255,255,.35);background:none;color:#fff;border-radius:999px;padding:8px 13px;font-size:13px;font-weight:800;flex-shrink:0}
.tb-q{font-size:19px;font-weight:800;margin:4px 0 12px}
.tb-search{position:relative}.tb-search input{font-size:22px;padding:16px 52px 16px 54px;border-radius:18px;font-weight:700}
.tb-search .ic{position:absolute;left:18px;top:50%;transform:translateY(-50%);color:var(--ink-3);display:flex}.tb-search .ic svg{width:24px;height:24px}
.tb-search .clr{position:absolute;right:12px;top:50%;transform:translateY(-50%);border:0;background:var(--card-2);color:var(--ink-2);border-radius:50%;width:34px;height:34px;font-size:18px;font-weight:800;display:none}.tb-search.has .clr{display:block}
.tb-hint{font-size:13px;color:var(--ink-3);margin-top:8px;line-height:1.5}
.vcard{display:flex;align-items:center;gap:14px;padding:14px 16px;border-radius:18px;background:var(--card-2);margin-top:10px}
.vcard .av{width:50px;height:50px;border-radius:50%;background:var(--blue);color:#fff;display:grid;place-items:center;font-weight:900;font-size:20px;flex-shrink:0}
.vcard .nm{font-size:19px;font-weight:800;letter-spacing:-.01em}.vcard .meta{font-size:13px;color:var(--ink-3);margin-top:3px;display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.vcard .meta .no{background:var(--ink);color:#fff;border-radius:999px;padding:2px 9px;font-weight:800;font-size:12.5px}.vcard .meta .st{font-weight:700;color:var(--ink-2)}
.vcard .go{border:0;background:var(--sun);color:var(--ink);font-weight:900;font-size:17px;border-radius:16px;padding:14px 22px;flex-shrink:0;box-shadow:0 6px 14px rgba(255,200,61,.35)}.vcard .go:disabled{opacity:.5;box-shadow:none}
.tb-new{margin-top:14px;display:flex;align-items:center;justify-content:center;gap:8px;border:2px dashed var(--line);border-radius:18px;padding:16px;font-weight:800;color:var(--blue);background:none;width:100%;font-size:16px}
.tb-done{display:flex;flex-direction:column;align-items:center;text-align:center;gap:14px;padding:8px 0 4px}
.tb-done .nobig{display:inline-block;background:var(--ink);color:#fff;border-radius:999px;padding:8px 22px;font-size:30px;font-weight:900;letter-spacing:.04em}
.tb-done .prog{display:flex;gap:6px;justify-content:center;flex-wrap:wrap}.tb-done .prog span{width:30px;height:30px;border-radius:50%;background:var(--card-2);display:grid;place-items:center;font-size:12px;font-weight:800;color:var(--ink-3)}.tb-done .prog span.on{background:var(--sun);color:var(--ink)}
.tb-form{display:grid;grid-template-columns:1fr 1fr;gap:12px 14px}.tb-form .field.full{grid-column:1/-1}.tb-form .inp{font-size:18px;padding:14px 16px}@media(max-width:600px){.tb-form{grid-template-columns:1fr}}""")

# ── admManual 교체
start = s.index("/* 수기 도장(관리자 › 수기 도장 · 미니 모드)")
end = s.index("/* 부스 편집 목록(카드 한 줄 = 부스 하나")
fn = r"""/* 수기 도장(관리자 › 수기 도장 · 미니 모드) — 폰 없는 어린이용 '부스 태블릿'.
   관리자로 로그인한 태블릿이 부스 QR 을 찍으면(앱 스캐너·카메라 앱 모두 renderStamp → 여기) 그 부스에 고정(sessionStorage wj:manual_booth).
   흐름: 이름이나 번호표(visitors.no, SQL 16절) 치면 바로 목록 → [도장] 한 번 → 큰 확인 화면(번호·도장 수, 5초 뒤 자동) → 다음 어린이.
   처음이면 [처음 왔어요] → 등록 항목 입력 → 등록+도장 한 번에, 번호표를 크게 보여줌(어린이가 다음 부스에서 번호만 말하면 됨).
   등록은 visitor_create(S.me 는 안 건드림), 도장은 admin_add_stamp(토큰·간격 검사 없음). 부스를 바꾸려면 [부스 바꾸기] 또는 다른 부스 QR */
function admManual(boothN){
  const booths = S.booths.filter(hasStamp), KEY = 'wj:manual_booth', goal = CONFIG.stampGoal;
  let cur = booths.find(b => b.n === boothN) || (boothN ? null : booths.find(b => b.n === sessionStorage.getItem(KEY))) || null;
  const pickScan = () => openScanner({ title: '부스 QR 스캔', hint: '<b>부스 앞 QR을 네모 안에</b>인식되면 이 태블릿이 그 부스로 고정돼요',
    onCode: async text => { const n = parseBoothQR(text), b = n && (boothByN(n) || boothByN(String(parseInt(n)))); if(!b || !hasStamp(b)){ $('#scanMsg').innerHTML = `<b>부스 QR이 아니에요</b><button class="btn sun sm" id="scanNext">다시 찍기</button>`; $('#scanNext').onclick = scanner.resume; return; } closeScanner(); go(admPath('/manual/' + encodeURIComponent(b.n)), true); } });
  if(!cur){   // 1) 부스 고르기
    sessionStorage.removeItem(KEY);
    admShell('manual', `
      <div class="card" style="display:flex;flex-direction:column;gap:14px">
        <div><div class="tb-q" style="margin:0">이 태블릿은 어느 부스인가요?</div><p class="small muted" style="margin-top:4px;line-height:1.6">폰이 없는 어린이는 부스에서 이 태블릿으로 도장을 찍어요. 한 번 고르면 이 탭에 고정돼요.</p></div>
        <button class="btn blue full" id="mScan" style="font-size:16px;padding:16px">${I.qr} 부스 QR 찍어서 고르기</button>
        <div class="chips" style="margin:0;padding:0;flex-wrap:wrap;overflow:visible;gap:8px">${booths.map(b => `<button class="chip" data-pick="${esc(b.n)}" style="font-size:15px;padding:12px 16px"><b>${esc(b.n)}번</b>&nbsp;${esc(b.name)}</button>`).join('')}</div>
      </div>`);
    $('#mScan').onclick = pickScan;
    $$('[data-pick]').forEach(c => c.onclick = () => go(admPath('/manual/' + encodeURIComponent(c.dataset.pick)), true));
    return;
  }
  sessionStorage.setItem(KEY, cur.n);
  admShell('manual', `
    <div class="tb-head"><div class="bn">${esc(cur.n)}</div><div class="grow"><div class="bsub">이 태블릿은</div><div class="bname" id="mCur">${esc(cur.n)}번 · ${esc(cur.name)}</div></div><button class="chg" id="mChange">부스 바꾸기</button></div>
    <div class="card" id="mPanel" style="margin-top:14px"></div>`);
  $('#mChange').onclick = () => { sessionStorage.removeItem(KEY); go(admPath('/manual'), true); };
  const panel = $('#mPanel');
  const vinfo = v => vCols().map(c => c.get(v)).filter(Boolean).join(' · ');
  const prog = n => `<div class="prog">${Array.from({ length: goal }, (_, i) => `<span class="${i < n ? 'on' : ''}">${i + 1}</span>`).join('')}</div>`;
  /* 찾기 화면: 두 글자(또는 번호 한 글자)부터 자동 검색(350ms). 결과 카드 = 이름·항목·번호표·도장 수 + [도장] */
  const showSearch = () => {
    panel.innerHTML = `
      <div class="tb-q">누구에게 ${esc(cur.n)}번 도장을 찍을까요?</div>
      <div class="tb-search" id="mBox"><span class="ic">${I.search}</span><input class="inp" id="mq" placeholder="이름 또는 번호표" autocomplete="off"><button class="clr" id="mClr" aria-label="지우기">×</button></div>
      <div class="tb-hint">번호표만 쳐도 바로 나와요 · 처음 온 어린이는 아래 버튼</div>
      <div id="mRes"></div>
      <button class="tb-new" id="mNew">＋ 처음 왔어요 · 새로 등록하고 도장</button>`;
    const inp = $('#mq'); let timer, seq = 0;
    const search = async () => {
      const q = inp.value.trim(); $('#mBox').classList.toggle('has', !!q);
      if(!q || (q.length < 2 && !/^\d+$/.test(q))){ $('#mRes').innerHTML = q ? '<div class="small muted" style="padding:8px 2px">이름은 두 글자 이상 적어주세요</div>' : ''; return; }
      const my = ++seq; $('#mRes').innerHTML = '<div class="empty">찾는 중…</div>';
      let rows; try{ rows = await DB.findVisitor(q); }catch(e){ if(my === seq) $('#mRes').innerHTML = `<div class="empty">${esc(e.message)}</div>`; return; }
      if(my !== seq) return;
      if(/^\d+$/.test(q)) rows = rows.filter(v => String(v.no) === q).concat(rows.filter(v => String(v.no) !== q));   // 번호가 딱 맞는 사람 먼저
      $('#mRes').innerHTML = rows.length ? rows.map(v => `<div class="vcard"><div class="av">${esc(v.name.slice(0, 1))}</div><div class="grow"><div class="nm">${esc(v.name)}</div><div class="meta"><span class="no">${esc(vTag(v))}</span>${vinfo(v) ? `<span>${esc(vinfo(v))}</span>` : ''}<span class="st">도장 ${v.n}/${goal}</span></div></div><button class="go" data-stamp="${v.id}">도장</button></div>`).join('')
        : '<div class="empty">없어요. 처음 왔으면 아래 [새로 등록]을 눌러주세요</div>';
      $$('[data-stamp]').forEach(btn => btn.onclick = () => { btn.disabled = true; doStamp(rows.find(x => x.id === btn.dataset.stamp)); });
    };
    inp.oninput = () => { clearTimeout(timer); timer = setTimeout(search, 350); };
    inp.onkeydown = e => { if(e.key === 'Enter'){ clearTimeout(timer); search(); } };
    $('#mClr').onclick = () => { inp.value = ''; search(); inp.focus(); };
    $('#mNew').onclick = showNew;
    setTimeout(() => inp.focus(), 50);
  };
  /* 도장 → 확인 화면(번호표 크게·도장 칸 진행). 완주면 confetti. 5초 뒤(또는 [다음]) 찾기 화면으로 */
  const doStamp = async (v, fresh) => {
    let r; try{ r = await DB.adminAddStamp(v.id, cur.id); }catch(e){ toast(e.message); return showSearch(); }
    const n = (v.n || 0) + (r.dup ? 0 : 1), done = n >= goal;
    if(done && !r.dup) confetti();
    panel.innerHTML = `<div class="tb-done" id="mDone">
      <div class="bigstamp ${r.dup ? 'dup' : ''}" style="width:160px;height:160px"><div><div class="n">${esc(cur.n)}</div><div class="t">${r.dup ? '이미 찍었어요' : '도장 완료'}</div></div></div>
      <div><div class="stamp-h">${esc(v.name)}${fresh ? ' 등록 완료' : ''} · 도장 ${n}/${goal}${done ? ' 완주! 🎉' : ''}</div>${prog(n)}</div>
      <div><div class="small muted">${fresh ? '내 번호표 — 다음 부스에서 이 번호만 말하면 돼요' : '번호표'}</div><div class="nobig">${esc(vTag(v))}</div></div>
      ${done ? '<p class="stamp-p">운영본부에서 선물을 받아가세요</p>' : ''}
      <button class="btn blue full" style="max-width:340px;font-size:16px;padding:15px" id="mNext">다음 어린이</button>
      <div class="small muted" id="mCnt">${fresh ? 10 : 5}초 뒤 자동으로 넘어가요</div></div>`;
    let left = fresh ? 10 : 5; const t = setInterval(() => { const c = $('#mCnt'); if(!c) return clearInterval(t); if(--left <= 0){ clearInterval(t); showSearch(); } else c.textContent = `${left}초 뒤 자동으로 넘어가요`; }, 1000);
    $('#mNext').onclick = () => { clearInterval(t); showSearch(); };
  };
  /* 처음 온 어린이: 등록 항목(행사 설정에서 켠 것) + 이름 → 등록하고 바로 도장 */
  const showNew = () => {
    panel.innerHTML = `
      <div class="tb-q">처음 온 어린이 등록</div>
      <div class="tb-form">
        <div class="field full"><label>이름</label><input class="inp" id="nName" placeholder="홍길동" maxlength="20" autocomplete="off"></div>
        ${regFieldsHTML('n')}
      </div>
      <div class="row" style="gap:8px;margin-top:14px"><button class="btn blue grow" id="nGo" style="font-size:16px;padding:15px">등록하고 ${esc(cur.n)}번 도장</button><button class="btn line" id="nBack" style="padding:15px 18px">뒤로</button></div>`;
    $('#nBack').onclick = showSearch;
    setTimeout(() => { const el = $('#nName'); if(el) el.focus(); }, 50);   // 50ms 안에 화면이 바뀌었을 수 있음
    $('#nGo').onclick = async () => {
      const name = $('#nName').value.trim(); if(!name) return toast('이름을 적어주세요'), $('#nName').focus();
      const f = readRegFields('n'); if(f.err) return toast(f.err), $(f.focus).focus();
      $('#nGo').disabled = true;
      try{ const v = await DB.createVisitor({ name, school: f.school, grade: f.grade, gender: f.gender }); doStamp({ ...v, n: 0 }, true); }
      catch(e){ $('#nGo').disabled = false; toast('등록에 실패했어요. 다시 눌러주세요'); }
    };
  };
  showSearch();
}
"""
s = s[:start] + fn + s[end:]
io.open(p,'w',encoding='utf-8',newline='\n').write(s)

# ── SQL 16절
p=r'C:\dev\booth-lite\supabase_setup.sql'
q=io.open(p,encoding='utf-8').read()
sec = """
-- 16. 방문객 번호표 (2026-10-07, booth-lite) ---------------------------------------------
-- 폰 없는 어린이가 부스 태블릿에서 "23번"처럼 말할 수 있게 등록 순서대로 번호를 매김. 6자리 코드보다 쉬움.
-- 이 절만 따로 실행해도 됨. visitor_create/visitor_get 은 'returning *' 라 자동으로 no 가 포함됨.
alter table visitors add column if not exists no serial;
drop view if exists visitor_stats;
create view visitor_stats as
  select v.id, v.name, v.school, v.grade, v.gender, v.created_at, v.survey_done_at, v.gift_received_at, v.no, count(s.id)::int as n
  from visitors v left join stamps s on s.visitor_id = v.id group by v.id;
drop function if exists admin_find_visitor(text, text);   -- 반환 열이 늘어서 재생성
create function admin_find_visitor(pw text, q text)
returns table(id uuid, name text, school text, grade text, gender text, created_at timestamptz, survey_done_at timestamptz, gift_received_at timestamptz, n int, no int)
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform admin_ok(pw);
  return query select v.id, v.name, v.school, v.grade, v.gender, v.created_at, v.survey_done_at, v.gift_received_at, v.n, v.no
    from visitor_stats v
    where v.name ilike '%' || q || '%' or v.school ilike '%' || q || '%' or right(replace(v.id::text, '-', ''), 6) = lower(q)
       or (q ~ '^[0-9]+$' and v.no = q::int)
    order by (q ~ '^[0-9]+$' and v.no = q::int) desc, v.created_at desc limit 50;
end $$;
grant execute on function admin_find_visitor(text, text) to anon;
"""
if '-- 16. 방문객 번호표' not in q:
    q = q.rstrip('\n') + '\n' + sec
    io.open(p,'w',encoding='utf-8',newline='\n').write(q)
print('ok')

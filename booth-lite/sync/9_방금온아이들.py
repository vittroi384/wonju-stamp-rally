# 9단계: 번호표 표시 제거 + '방금 다른 부스에서 도장 찍은 아이들' 탭 한 번 도장. 8단계 뒤에 실행 (옛 9_번호표카드 는 폐기)
import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
def rep(old,new):
    global s
    assert s.count(old)==1, (s.count(old), old[:100])
    s=s.replace(old,new,1)

# ── DB: 최근 다른 부스에서 도장 찍은 사람(10분) — 서버는 부스별 명단 RPC 를 부스마다 조금씩(lim 40) 받아 합침. SQL 추가 없음
rep("  async boothVisitors(boothId){ const d=await this._all();",
    """  async recentVisitors(boothId,otherIds,mins=10){ const d=await this._all(); const since=Date.now()-mins*60000, here=new Set(d.stamps.filter(s=>s.boothId===boothId).map(s=>s.visitorId)), cnt={}; d.stamps.forEach(s=>cnt[s.visitorId]=(cnt[s.visitorId]||0)+1); const vm=Object.fromEntries(d.visitors.map(v=>[v.id,v])); const seen=new Map(); d.stamps.filter(s=>otherIds.includes(s.boothId)&&s.at>=since&&!here.has(s.visitorId)).sort((a,b)=>b.at-a.at).forEach(s=>{ if(!seen.has(s.visitorId)&&vm[s.visitorId]) seen.set(s.visitorId,{...vm[s.visitorId],stampedAt:s.at,n:cnt[s.visitorId]||0}); }); const counts={}; d.stamps.filter(s=>s.at>=since).forEach(s=>counts[s.boothId]=(counts[s.boothId]||0)+1); return {list:[...seen.values()].slice(0,12),counts}; },
  async boothVisitors(boothId){ const d=await this._all();""")
rep("  async boothVisitors(boothId){ return (await this._admPages('admin_booth_visitors',{bid:boothId}))",
    """  /* 최근 mins 분 안에 다른 부스에서 도장 찍었고 이 부스엔 아직 없는 사람. 부스마다 최신 40줄만 받아 합침(태블릿 7대 × 20초 주기여도 가벼움) */
  async recentVisitors(boothId,otherIds,mins=10){
    const row=r=>({id:r.visitor_id,name:r.name,school:r.school,grade:r.grade||'',gender:r.gender||'',stampedAt:+new Date(r.stamped_at),n:+r.n});
    const ids=[boothId,...otherIds], per=await Promise.all(ids.map(bid=>this._adm('admin_booth_visitors',{bid,off:0,lim:40}).then(rows=>(rows||[]).map(row))));
    const since=Date.now()-mins*60000, hereIds=new Set(per[0].map(v=>v.id)), seen=new Map(), counts={};
    per.forEach((rows,i)=>counts[ids[i]]=rows.filter(v=>v.stampedAt>=since).length);   // 부스별 최근 도장 수(혼잡도, 40 넘으면 40+)
    per.slice(1).flat().filter(v=>v.stampedAt>=since&&!hereIds.has(v.id)).sort((a,b)=>b.stampedAt-a.stampedAt).forEach(v=>{ if(!seen.has(v.id)) seen.set(v.id,v); });
    return {list:[...seen.values()].slice(0,12),counts};
  },
  async boothVisitors(boothId){ return (await this._admPages('admin_booth_visitors',{bid:boothId}))""")

# ── 번호표 표시 제거
rep("const vTag = v => v && v.no ? `${v.no}번` : shortCode(v.id);\n", "")
s = s.replace("   // 번호표(SQL 16절) 있으면 번호, 아니면 코드", "")   # 7단계가 surveyOn 줄을 끼우면서 이 주석이 그 줄 끝으로 밀려 있음
rep("""<input class="inp" id="mq" placeholder="이름 또는 번호표" autocomplete="off"><button class="clr" id="mClr" aria-label="지우기">×</button></div>
      <div class="tb-hint">번호표만 쳐도 바로 나와요 · 처음 온 어린이는 아래 버튼</div>
      <div id="mRes"></div>""",
"""<input class="inp" id="mq" placeholder="아이 이름" autocomplete="off"><button class="clr" id="mClr" aria-label="지우기">×</button></div>
      <div class="tb-hint">두 글자만 치면 나와요 · 같은 이름은 소속·나이로 구분 · 처음 온 어린이는 맨 아래 버튼</div>
      <div id="mRes"></div>
      <div id="mRecent"></div>""")
rep("""      if(!q || (q.length < 2 && !/^\\d+$/.test(q))){ $('#mRes').innerHTML = q ? '<div class="small muted" style="padding:8px 2px">이름은 두 글자 이상 적어주세요</div>' : ''; return; }""",
    """      $('#mRecent').hidden = !!q;   // 검색 중엔 최근 목록 숨김
      if(q.length < 2){ $('#mRes').innerHTML = q ? '<div class="small muted" style="padding:8px 2px">두 글자 이상 적어주세요</div>' : ''; return; }""")
rep("""      if(/^\\d+$/.test(q)) rows = rows.filter(v => String(v.no) === q).concat(rows.filter(v => String(v.no) !== q));   // 번호가 딱 맞는 사람 먼저
      $('#mRes').innerHTML = rows.length ? rows.map(v => `<div class="vcard"><div class="av">${esc(v.name.slice(0, 1))}</div><div class="grow"><div class="nm">${esc(v.name)}</div><div class="meta"><span class="no">${esc(vTag(v))}</span>${vinfo(v) ? `<span>${esc(vinfo(v))}</span>` : ''}<span class="st">도장 ${v.n}/${goal}</span></div></div><button class="go" data-stamp="${v.id}">도장</button></div>`).join('')
        : '<div class="empty">없어요. 처음 왔으면 아래 [새로 등록]을 눌러주세요</div>';
      $$('[data-stamp]').forEach(btn => btn.onclick = () => { btn.disabled = true; doStamp(rows.find(x => x.id === btn.dataset.stamp)); });
    };""",
"""      $('#mRes').innerHTML = rows.length ? rows.map(vcard).join('') : '<div class="empty">없어요. 처음 왔으면 아래 [새로 등록]을 눌러주세요</div>';
      wireStamp('#mRes', rows);
    };
    /* 방금 다른 부스에서 도장 찍은 아이들(10분) — 이름 안 치고 탭 한 번. 20초마다 갱신, 이 화면을 벗어나면 멈춤 */
    const recent = async () => {
      const box = $('#mRecent'); if(!box) return;
      let r = { list: [], counts: {} }; try{ r = await DB.recentVisitors(cur.id, booths.filter(b => b.id !== cur.id).map(b => b.id)); }catch(e){}
      const box2 = $('#mRecent'); if(!box2 || box2 !== box) return;
      const rows = r.list, mx = Math.max(1, ...Object.values(r.counts));
      /* 부스 상황: 부스별 최근 10분 도장 수. 많을수록 진한 칸 → 한가한 부스로 안내할 때 */
      const status = `<div class="tb-sec">부스 상황 <span class="muted small" style="font-weight:600">· 최근 10분 도장 수 · 모든 태블릿이 같은 서버를 봐요</span></div>
        <div class="tb-status">${booths.map(b => { const n = r.counts[b.id] || 0; return `<div class="bs ${b.id === cur.id ? 'me' : ''}" style="--f:${(n / mx).toFixed(2)}"><b>${esc(b.n)}</b><span>${n >= 40 ? '40+' : n}</span></div>`; }).join('')}</div>`;
      box.innerHTML = status + (rows.length ? `<div class="tb-sec">방금 다른 부스에서 도장 찍은 아이들 <span class="muted small" style="font-weight:600">· 탭 한 번이면 도장</span></div>${rows.map(v => vcard(v, `${fmtTime(v.stampedAt)} 도장`)).join('')}` : '<div class="small muted" style="padding:6px 2px">최근 10분 안에 다른 부스에서 도장 찍은 아이가 없어요</div>');
      wireStamp('#mRecent', rows);
    };
    recent(); const rt = setInterval(() => { if($('#mRecent')) recent(); else clearInterval(rt); }, 20000);""")
rep("""    inp.oninput = () => { clearTimeout(timer); timer = setTimeout(search, 350); };""",
    """    inp.oninput = () => { const r = $('#mRecent'); if(r) r.hidden = !!inp.value.trim(); clearTimeout(timer); timer = setTimeout(search, 350); };   // 치기 시작하면 최근 목록은 바로 숨김
    inp.addEventListener('focus', () => { clearInterval(rt); });   // 자판이 올라오면 갱신으로 목록이 흔들리지 않게""")
# 카드 그리기·버튼 연결은 공용
rep("""  const vinfo = v => vCols().map(c => c.get(v)).filter(Boolean).join(' · ');""",
    """  const vinfo = v => vCols().map(c => c.get(v)).filter(Boolean).join(' · ');
  const vcard = (v, extra) => `<div class="vcard"><div class="av">${esc(v.name.slice(0, 1))}</div><div class="grow"><div class="nm">${esc(v.name)}</div><div class="meta">${vinfo(v) ? `<span>${esc(vinfo(v))}</span>` : ''}<span class="st">도장 ${v.n}/${goal}</span>${extra ? `<span>${esc(extra)}</span>` : ''}</div></div><button class="go" data-stamp="${v.id}">도장</button></div>`;
  const wireStamp = (sel, rows) => $$(sel + ' [data-stamp]').forEach(btn => btn.onclick = () => { btn.disabled = true; doStamp(rows.find(x => x.id === btn.dataset.stamp)); });""")
# 확인 화면: 번호표 블록 제거
rep("""      <div><div class="small muted">${fresh ? '내 번호표 — 다음 부스에서 이 번호만 말하면 돼요' : '번호표'}</div><div class="nobig">${esc(vTag(v))}</div></div>
""", """      ${fresh ? '<p class="stamp-p">다음 부스에서는 이름만 말하면 돼요</p>' : ''}
""")
rep("<div class=\"small muted\" id=\"mCnt\">${fresh ? 10 : 5}초 뒤 자동으로 넘어가요</div></div>`;\n    let left = fresh ? 10 : 5;",
    "<div class=\"small muted\" id=\"mCnt\">5초 뒤 자동으로 넘어가요</div></div>`;\n    let left = 5;")
rep("""   흐름: 이름이나 번호표(visitors.no, SQL 16절) 치면 바로 목록 → [도장] 한 번 → 큰 확인 화면(번호·도장 수, 5초 뒤 자동) → 다음 어린이.
   처음이면 [처음 왔어요] → 등록 항목 입력 → 등록+도장 한 번에, 번호표를 크게 보여줌(어린이가 다음 부스에서 번호만 말하면 됨).""",
    """   흐름: 이름 두 글자 치면 바로 목록 → [도장] 한 번 → 큰 확인 화면(도장 수, 5초 뒤 자동) → 다음 어린이.
   '방금 다른 부스에서 도장 찍은 아이들'(10분, DB.recentVisitors) 이 미리 떠 있어 보통은 이름도 안 치고 탭 한 번.
   처음이면 [처음 왔어요] → 등록 항목 입력 → 등록+도장 한 번에.""")
# 스타일: 섹션 제목
rep(".tb-done .nobig{display:inline-block;background:var(--ink);color:#fff;border-radius:999px;padding:8px 22px;font-size:30px;font-weight:900;letter-spacing:.04em}",
    ".tb-sec{font-size:14px;font-weight:800;margin:18px 0 2px;color:var(--ink-2)}\n.tb-status{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}.tb-status .bs{flex:1 1 60px;min-width:60px;border-radius:12px;padding:8px 6px;text-align:center;background:color-mix(in srgb,var(--blue) calc(var(--f)*55%),var(--card-2));display:flex;flex-direction:column;gap:2px}.tb-status .bs b{font-size:15px}.tb-status .bs span{font-size:12px;font-weight:700;color:var(--ink-2)}.tb-status .bs.me{outline:2px solid var(--ink)}")
io.open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

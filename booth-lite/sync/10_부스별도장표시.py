# 10단계: 수기 도장 카드·확인 화면에 '어느 부스 도장을 받았는지' 1~7 칸 표시, 이 부스에 이미 찍었으면 버튼 '이미 찍음'. 9단계 뒤에 실행
import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
def rep(old,new):
    global s
    assert s.count(old)==1, (s.count(old), old[:100])
    s=s.replace(old,new,1)

# 카드: 부스 칸(.bprog) + 버튼. 칸은 visitor_stamps 로 채움(fillStamps). 이 부스에 이미 있으면 버튼 '이미 찍음'
rep("""  const vcard = (v, extra) => `<div class="vcard"><div class="av">${esc(v.name.slice(0, 1))}</div><div class="grow"><div class="nm">${esc(v.name)}</div><div class="meta">${vinfo(v) ? `<span>${esc(vinfo(v))}</span>` : ''}<span class="st">도장 ${v.n}/${goal}</span>${extra ? `<span>${esc(extra)}</span>` : ''}</div></div><button class="go" data-stamp="${v.id}">도장</button></div>`;
  const wireStamp = (sel, rows) => $$(sel + ' [data-stamp]').forEach(btn => btn.onclick = () => { btn.disabled = true; doStamp(rows.find(x => x.id === btn.dataset.stamp)); });
  const prog = n => `<div class="prog">${Array.from({ length: goal }, (_, i) => `<span class="${i < n ? 'on' : ''}">${i + 1}</span>`).join('')}</div>`;""",
"""  /* 부스 칸: 도장 받은 부스는 노랑, 이 부스는 테두리. ids = 그 아이가 도장 받은 부스 id 목록(null 이면 아직 불러오는 중) */
  const boothRow = (ids, big) => `<div class="bprog ${big ? 'big' : ''} ${ids ? '' : 'wait'}">${booths.map(b => `<span class="${ids && ids.includes(b.id) ? 'on' : ''} ${b.id === cur.id ? 'me' : ''}" title="${esc(b.name)}">${esc(b.n)}</span>`).join('')}</div>`;
  const vcard = (v, extra) => `<div class="vcard" data-v="${v.id}"><div class="av">${esc(v.name.slice(0, 1))}</div><div class="grow"><div class="nm">${esc(v.name)}</div><div class="meta">${vinfo(v) ? `<span>${esc(vinfo(v))}</span>` : ''}<span class="st">도장 ${v.n}/${goal}</span>${extra ? `<span>${esc(extra)}</span>` : ''}</div>${boothRow(v.boothIds || null)}</div><button class="go" data-stamp="${v.id}">도장</button></div>`;
  const wireStamp = (sel, rows) => { $$(sel + ' [data-stamp]').forEach(btn => btn.onclick = () => { btn.disabled = true; doStamp(rows.find(x => x.id === btn.dataset.stamp)); }); fillStamps(sel, rows); };
  /* 각 아이의 도장 부스를 서버에서 받아(visitor_stamps, 1분 캐시) 카드 칸을 채우고, 이 부스에 이미 있으면 버튼을 '이미 찍음'으로 */
  const stampCache = new Map();
  const stampsOf = async id => { const c = stampCache.get(id); if(c && Date.now() - c.at < 60000) return c.ids; const ids = (await DB.stampsOf(id)).map(s => s.boothId); stampCache.set(id, { ids, at: Date.now() }); return ids; };
  const fillStamps = (sel, rows) => rows.forEach(async v => {
    let ids; try{ ids = await stampsOf(v.id); }catch(e){ return; }
    v.boothIds = ids; v.n = ids.length;
    const card = $(sel + ` .vcard[data-v="${v.id}"]`); if(!card) return;
    card.querySelector('.bprog').outerHTML = boothRow(ids); card.querySelector('.st').textContent = `도장 ${ids.length}/${goal}`;
    if(ids.includes(cur.id)){ const b = card.querySelector('[data-stamp]'); b.textContent = '이미 찍음'; b.classList.add('done'); b.disabled = true; }
  });""")
# 확인 화면: 실제 받은 부스로 칸 채움
rep("""    let r; try{ r = await DB.adminAddStamp(v.id, cur.id); }catch(e){ toast(e.message); return showSearch(); }
    const n = (v.n || 0) + (r.dup ? 0 : 1), done = n >= goal;""",
"""    let r; try{ r = await DB.adminAddStamp(v.id, cur.id); }catch(e){ toast(e.message); return showSearch(); }
    stampCache.delete(v.id); let ids = null; try{ ids = await stampsOf(v.id); }catch(e){}
    const n = ids ? ids.length : (v.n || 0) + (r.dup ? 0 : 1), done = n >= goal;""")
rep("""· 도장 ${n}/${goal}${done ? ' 완주! 🎉' : ''}</div>${prog(n)}</div>""",
    """· 도장 ${n}/${goal}${done ? ' 완주! 🎉' : ''}</div>${boothRow(ids || [cur.id], true)}<div class="small muted" style="margin-top:6px">노란 칸 = 받은 부스</div></div>""")
# 스타일
rep(".tb-done .prog{display:flex;gap:6px;justify-content:center;flex-wrap:wrap}.tb-done .prog span{width:30px;height:30px;border-radius:50%;background:var(--card-2);display:grid;place-items:center;font-size:12px;font-weight:800;color:var(--ink-3)}.tb-done .prog span.on{background:var(--sun);color:var(--ink)}",
    ".bprog{display:flex;gap:4px;margin-top:7px;flex-wrap:wrap}.bprog span{width:26px;height:26px;border-radius:50%;background:var(--card);border:1.5px solid var(--line);display:grid;place-items:center;font-size:11.5px;font-weight:800;color:var(--ink-3)}.bprog span.on{background:var(--sun);border-color:var(--sun);color:var(--ink)}.bprog span.me{box-shadow:0 0 0 2px var(--ink)}.bprog.wait{opacity:.45}.bprog.big{justify-content:center;gap:6px;margin-top:10px}.bprog.big span{width:34px;height:34px;font-size:13px}\n.vcard .go.done{background:var(--card);color:var(--ink-3);box-shadow:none;border:1.5px solid var(--line)}")
io.open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

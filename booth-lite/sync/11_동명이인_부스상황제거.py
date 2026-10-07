# 11단계: 등록 직전 같은 이름 확인(중복 등록 방지) + 부스 상황 띠 제거. 10단계 뒤에 실행
import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
def rep(old,new):
    global s
    assert s.count(old)==1, (s.count(old), old[:100])
    s=s.replace(old,new,1)

# ── 부스 상황 띠 제거 (recentVisitors 의 counts 는 그대로 두되 안 그림)
rep("""      /* 부스 상황: 부스별 최근 10분 도장 수. 많을수록 진한 칸 → 한가한 부스로 안내할 때 */
      const status = `<div class="tb-sec">부스 상황 <span class="muted small" style="font-weight:600">· 최근 10분 도장 수 · 모든 태블릿이 같은 서버를 봐요</span></div>
        <div class="tb-status">${booths.map(b => { const n = r.counts[b.id] || 0; return `<div class="bs ${b.id === cur.id ? 'me' : ''}" style="--f:${(n / mx).toFixed(2)}"><b>${esc(b.n)}</b><span>${n >= 40 ? '40+' : n}</span></div>`; }).join('')}</div>`;
      box.innerHTML = status + (rows.length ?""",
"""      box.innerHTML = (rows.length ?""")
rep("      const rows = r.list, mx = Math.max(1, ...Object.values(r.counts));", "      const rows = r.list;")

# ── 등록 직전 같은 이름 확인: 같은 이름(정확히 일치)이 이미 있으면 목록을 보여주고 '이 아이예요 → 도장' / '다른 아이예요 → 새로 등록'
rep("""      const name = $('#nName').value.trim(); if(!name) return toast('이름을 적어주세요'), $('#nName').focus();
      const f = readRegFields('n'); if(f.err) return toast(f.err), $(f.focus).focus();
      $('#nGo').disabled = true;
      try{ const v = await DB.createVisitor({ name, school: f.school, grade: f.grade, gender: f.gender }); doStamp({ ...v, n: 0 }, true); }
      catch(e){ $('#nGo').disabled = false; toast('등록에 실패했어요. 다시 눌러주세요'); }""",
"""      const name = $('#nName').value.trim(); if(!name) return toast('이름을 적어주세요'), $('#nName').focus();
      const f = readRegFields('n'); if(f.err) return toast(f.err), $(f.focus).focus();
      $('#nGo').disabled = true;
      /* 같은 이름이 이미 있으면(최근 등록 포함) 먼저 보여줌 — 같은 아이를 두 번 등록하는 실수 방지. 소속까지 같으면 맨 위 */
      if(!$('#nGo').dataset.force){
        let same = []; try{ same = (await DB.findVisitor(name)).filter(v => v.name === name); }catch(e){}
        if(same.length){
          same.sort((a, b) => ((b.school || '') === f.school) - ((a.school || '') === f.school));
          const sameOrg = same.some(v => (v.school || '') === f.school && f.school);
          panel.innerHTML = `
            <div class="tb-q">같은 이름이 이미 있어요</div>
            <div class="tb-hint" style="margin:0 0 6px">${sameOrg ? `<b style="color:var(--coral)">소속까지 같은 아이가 있어요.</b> 방금 다른 부스에서 등록했을 수 있어요. ` : ''}이 아이가 맞으면 [이 아이예요]를 누르세요. 도장 칸을 보면 어느 부스를 돌았는지 알 수 있어요.</div>
            <div id="mSame">${same.map(v => vcard(v, `${fmtTime(v.createdAt)} 등록`)).join('')}</div>
            <div class="row" style="gap:8px;margin-top:14px"><button class="btn blue grow" id="nForce" style="font-size:15px;padding:14px">다른 아이예요 · ${esc(name)} 새로 등록</button><button class="btn line" id="nBack2" style="padding:14px 18px">뒤로</button></div>`;
          $$('#mSame [data-stamp]').forEach(b => b.textContent = '이 아이예요 · 도장');
          wireStamp('#mSame', same);
          $('#nBack2').onclick = () => { showNew(); setTimeout(() => { $('#nName').value = name; regFields().forEach(x => { const el = $('#n' + x.k); if(el) el.value = f[x.col] || ''; }); }, 0); };
          $('#nForce').onclick = async () => { $('#nForce').disabled = true; try{ const v = await DB.createVisitor({ name, school: f.school, grade: f.grade, gender: f.gender }); doStamp({ ...v, n: 0 }, true); }catch(e){ $('#nForce').disabled = false; toast('등록에 실패했어요. 다시 눌러주세요'); } };
          return;
        }
      }
      try{ const v = await DB.createVisitor({ name, school: f.school, grade: f.grade, gender: f.gender }); doStamp({ ...v, n: 0 }, true); }
      catch(e){ $('#nGo').disabled = false; toast('등록에 실패했어요. 다시 눌러주세요'); }""")
io.open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

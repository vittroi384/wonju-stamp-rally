import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
fn = r"""/* 수기 도장(관리자 › 수기 도장, 미니 모드). 부스를 고르고(칩 또는 QR 찍기) → 학생 찾기 → [도장] / 새 학생 등록 후 바로 도장.
   관리자 폰으로 부스 QR 을 찍으면(앱 스캐너·카메라 앱 모두) renderStamp 가 여기로 보냄(#/admin/manual/번호). 등록은 visitor_create(S.me 는 건드리지 않음), 도장은 admin_add_stamp */
function admManual(boothN){
  const booths = S.booths.filter(hasStamp);
  let cur = booths.find(b => b.n === boothN) || null;
  const chips = () => booths.map(b => `<button class="chip ${cur && cur.id === b.id ? '' : 'off'}" data-pick="${esc(b.n)}" style="${cur && cur.id === b.id ? 'background:var(--blue);color:#fff' : 'opacity:.6'}">${esc(b.n)}번 · ${esc(b.name)}</button>`).join('');
  admShell('manual', `
    <div class="card" style="display:flex;flex-direction:column;gap:12px">
      <div class="row" style="justify-content:space-between;gap:8px;flex-wrap:wrap">
        <div class="h-sec" style="margin:0">1. 부스 고르기 <span class="muted small" id="mCur">${cur ? `· ${esc(cur.n)}번 ${esc(cur.name)}` : '· 아직 안 골랐어요'}</span></div>
        <button class="btn sm" id="mScan">${I.qr} 부스 QR 찍어서 고르기</button>
      </div>
      <div class="chips" id="mChips" style="margin:0;padding:0;flex-wrap:wrap;overflow:visible">${chips()}</div>
    </div>
    <div class="card" style="display:flex;flex-direction:column;gap:10px">
      <div class="h-sec" style="margin:0">2. 학생 찾아서 도장</div>
      <div class="row" style="gap:8px"><input class="inp sm" id="mq" placeholder="이름, 학교, 코드 (두 글자 이상)" autocomplete="off" style="max-width:320px"><button class="btn sm" id="mGo">찾기</button></div>
      <div class="tscroll" id="mRes"></div>
    </div>
    <div class="card" style="display:flex;flex-direction:column;gap:12px">
      <div class="h-sec" style="margin:0">3. 처음 온 학생 — 등록하고 바로 도장</div>
      <div class="field"><label id="nSchoolL">학교</label><input class="inp" id="nSchool" placeholder="학교명" maxlength="30" autocomplete="off"></div>
      <div class="field"><label>구분</label><div class="gsel four" id="nLevel"><button type="button" data-l="초">초등</button><button type="button" data-l="중">중등</button><button type="button" data-l="고">고등</button><button type="button" data-l="성인">성인</button></div></div>
      <div class="field" id="nGradeF" hidden><label>학년</label><div class="gsel" id="nGrade"></div></div>
      <div class="field"><label>이름</label><input class="inp" id="nName" placeholder="홍길동" maxlength="20" autocomplete="off"></div>
      <div class="field"><label>성별</label><div class="gsel" id="nGender"><button type="button" data-g="남">남</button><button type="button" data-g="여">여</button></div></div>
      <button class="btn blue full" id="nGo">등록 + 도장</button>
      <p class="small muted" style="margin:0">학생이 자기 폰에서 이 기록을 이어받으려면 등록 뒤 알려주는 <b>6자리 코드</b>와 이름으로 [기록 이어받기]를 하면 돼요.</p>
    </div>`);
  const pick = b => { cur = b; $('#mCur').textContent = `· ${b.n}번 ${b.name}`; $('#mChips').innerHTML = chips(); wireChips(); history.replaceState(null, '', location.pathname + '#' + admPath('/manual/' + encodeURIComponent(b.n))); };
  const wireChips = () => $$('[data-pick]').forEach(c => c.onclick = () => pick(boothByN(c.dataset.pick)));
  wireChips();
  $('#mScan').onclick = () => openScanner({ title: '부스 QR 스캔', hint: '<b>부스 앞 QR을 네모 안에</b>인식되면 그 부스가 골라져요',
    onCode: async text => { const n = parseBoothQR(text), b = n && (boothByN(n) || boothByN(String(parseInt(n)))); if(!b || !hasStamp(b)){ $('#scanMsg').innerHTML = `<b>부스 QR이 아니에요</b><button class="btn sun sm" id="scanNext">다시 찍기</button>`; $('#scanNext').onclick = scanner.resume; return; } closeScanner(); pick(b); toast(`${b.n}번 ${b.name} 골랐어요`); } });
  const stamp = async (vid, name) => {
    if(!cur) return toast('먼저 부스를 골라주세요');
    try{ const r = await DB.adminAddStamp(vid, cur.id); toast(r.dup ? `${name}: ${cur.n}번은 이미 찍혀 있어요` : `${name}: ${cur.n}번 도장 넣었어요`); return true; }catch(e){ toast(e.message); return false; }
  };
  const find = async () => {
    const q = $('#mq').value.trim(); if(q.length < 2) return toast('두 글자 이상 적어주세요');
    $('#mRes').innerHTML = '<div class="empty">찾는 중…</div>';
    let rows; try{ rows = await DB.findVisitor(q); }catch(e){ $('#mRes').innerHTML = ''; return toast(e.message); }
    $('#mRes').innerHTML = rows.length ? `<table class="table"><thead><tr><th>코드</th><th>이름</th><th>학교</th><th>학년</th><th>도장</th><th></th></tr></thead><tbody>${rows.map(v => `<tr><td class="num" style="letter-spacing:.08em"><b>${shortCode(v.id)}</b></td><td><b>${esc(v.name)}</b></td><td class="muted">${esc(v.school || '')}</td><td class="muted">${esc(v.grade || '')}</td><td class="num">${v.n}</td>
      <td style="text-align:right"><button class="btn xs sun" data-stamp="${v.id}" data-name="${esc(v.name)}">도장</button></td></tr>`).join('')}</tbody></table>` : '<div class="empty">없어요. 처음 온 학생이면 아래에서 등록해 주세요</div>';
    $$('[data-stamp]').forEach(b => b.onclick = async () => { b.disabled = true; if(await stamp(b.dataset.stamp, b.dataset.name)) find(); else b.disabled = false; });
  };
  $('#mGo').onclick = find; $('#mq').onkeydown = e => { if(e.key === 'Enter') find(); };
  let gender = '', level = '', gradeNo = '';
  $$('#nGender button').forEach(b => b.onclick = () => { gender = b.dataset.g; $$('#nGender button').forEach(x => x.classList.toggle('on', x === b)); });
  $$('#nLevel button').forEach(b => b.onclick = () => {
    level = b.dataset.l; gradeNo = ''; $$('#nLevel button').forEach(x => x.classList.toggle('on', x === b));
    const adult = level === '성인', n = level === '초' ? 6 : 3;
    $('#nGradeF').hidden = adult;
    $('#nGrade').innerHTML = adult ? '' : Array.from({ length: n }, (_, i) => `<button type="button" data-n="${i + 1}">${i + 1}학년</button>`).join('');
    $$('#nGrade button').forEach(g => g.onclick = () => { gradeNo = g.dataset.n; $$('#nGrade button').forEach(x => x.classList.toggle('on', x === g)); });
    $('#nSchoolL').textContent = adult ? '소속 (선택)' : '학교';
  });
  $('#nGo').onclick = async () => {
    if(!cur) return toast('먼저 부스를 골라주세요');
    const name = $('#nName').value.trim(), school = $('#nSchool').value.trim();
    if(!level) return toast('초등·중등·고등·성인 중에 골라주세요');
    if(level !== '성인' && !gradeNo) return toast('학년을 골라주세요');
    const grade = level === '성인' ? '성인' : level + gradeNo;
    if(!school && grade !== '성인') return toast('학교를 적어주세요'), $('#nSchool').focus();
    if(!name) return toast('이름을 적어주세요'), $('#nName').focus();
    if(!gender) return toast('성별을 골라주세요');
    $('#nGo').disabled = true;
    try{
      const v = await DB.createVisitor({ name, school, grade, gender });
      await stamp(v.id, name);
      $('#mRes').innerHTML = `<div class="notice">${I.check}<span><b>${esc(name)}</b> 등록 완료 · 코드 <b style="letter-spacing:.1em">${shortCode(v.id)}</b> — 학생 폰에서 [기록 이어받기] 할 때 이 코드를 써요</span></div>`;
      $('#nName').value = ''; gender = ''; gradeNo = ''; $$('#nGender button, #nGrade button').forEach(x => x.classList.remove('on'));   // 학교·구분은 다음 학생을 위해 남겨 둠
    }catch(e){ toast('등록에 실패했어요. 다시 눌러주세요'); }
    $('#nGo').disabled = false;
  };
}
"""
anchor="/* 부스 편집 목록(카드 한 줄 = 부스 하나"
assert anchor in s
s=s.replace(anchor, fn+anchor,1)
io.open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

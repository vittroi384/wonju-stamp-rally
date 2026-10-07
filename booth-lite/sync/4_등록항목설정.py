# 4단계: 등록 항목(소속·나이·연락처) 관리자 설정 + 라우터 복귀 주소 버그 수정. 3단계 뒤에 실행
import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
def rep(old,new):
    global s
    assert s.count(old)==1, (s.count(old), old[:100])
    s=s.replace(old,new,1)

# ── 라우터: 조각마다 디코딩 (통째로 디코딩하면 #/register/%2Fstamp%2F2 의 복귀 주소가 쪼개져 등록 뒤 홈으로 감 → 도장 안 찍힘)
if "let h = location.hash.replace(/^#/, '') || '/'; try{ h = decodeURIComponent(h); }" in s: rep("""  let h = location.hash.replace(/^#/, '') || '/'; try{ h = decodeURIComponent(h); }catch(e){}   // 부스 번호가 한글(본1 등)이면 주소가 인코딩돼 있음
  const [_, a, b, c] = h.split('/');""",
"""  const h = location.hash.replace(/^#/, '') || '/';
  const [_, a, b, c] = h.split('/').map(x => { try{ return decodeURIComponent(x); }catch(e){ return x; } });   // 조각마다 디코딩: 한글 부스 번호(본1)도, 등록 복귀 주소(%2Fstamp%2F2)도 살아남음""")   # 축전 앱이 이미 고쳤으면 건너뜀

# ── 등록 항목 정의 + 헬퍼 (readAge 옆)
rep("function readAge(sel){ const a = parseInt($(sel).value); return a >= 1 && a <= 120 ? String(a) : ''; }   // 나이 입력칸 → '12' (범위 밖·빈칸이면 '')",
"""function readAge(sel){ const a = parseInt($(sel).value); return a >= 1 && a <= 120 ? String(a) : ''; }   // 나이 입력칸 → '12' (범위 밖·빈칸이면 '')
/* 등록 항목. 이름은 항상 받고, 아래 셋은 관리자 › 행사 설정에서 사용/필수를 켜고 끔(settings.regFields = {org:{on,req}, age:{…}, phone:{…}}).
   DB 열은 축전 앱과 같게 두고 뜻만 다름: school = 소속, grade = 나이, gender = 연락처 (SQL 안 바꾸려고) */
const REG_FIELD_DEFS = [
  { k: 'org',   label: '소속',   col: 'school', type: 'text',   ph: '학교·기관·단체명', max: 30, on: true,  req: true },
  { k: 'age',   label: '나이',   col: 'grade',  type: 'number', ph: '예: 12',           max: 3,  on: true,  req: true },
  { k: 'phone', label: '연락처', col: 'gender', type: 'tel',    ph: '010-1234-5678',    max: 20, on: true,  req: false },
];
function regFields(){ const o = (S.settingsRaw && S.settingsRaw.regFields) || {}; return REG_FIELD_DEFS.map(d => ({ ...d, ...(o[d.k] || {}) })).filter(f => f.on); }
function regLabels(){ return regFields().map(f => f.label).concat('이름').join('·'); }
function regFieldsHTML(prefix){
  return regFields().map(f => `<div class="field"><label>${f.label}${f.req ? '' : ' <span class="muted small" style="font-weight:600">(선택)</span>'}</label><input class="inp" id="${prefix}${f.k}" type="${f.type}" ${f.type === 'number' ? 'inputmode="numeric" min="1" max="120"' : f.type === 'tel' ? 'inputmode="tel"' : ''} placeholder="${f.ph}" maxlength="${f.max}" autocomplete="off"></div>`).join('\\n');
}
/* 입력칸 읽기 → {school, grade, gender} (DB 열 이름). 필수 비었거나 나이가 숫자가 아니면 {err, focus} */
function readRegFields(prefix){
  const out = { school: '', grade: '', gender: '' };
  for(const f of regFields()){
    const sel = '#' + prefix + f.k, raw = $(sel).value.trim(); let v = raw;
    if(f.k === 'age'){ v = readAge(sel); if(raw && !v) return { err: '나이는 1~120 사이 숫자로 적어주세요', focus: sel }; }
    if(f.req && !v) return { err: `${f.label}을(를) 적어주세요`, focus: sel };
    out[f.col] = v;
  }
  return out;
}
function vCols(){ return regFields().map(f => ({ label: f.label, get: v => (v && v[f.col]) || '' })); }   // 관리자 표·CSV 의 가변 열
const vColsTH = () => vCols().map(c => `<th>${c.label}</th>`).join('');
const vColsTD = v => vCols().map(c => `<td class="muted">${esc(c.get(v))}</td>`).join('');""")

# ── 문구
rep('<div class="sc-foot">소속·나이·이름만 적으면 시작돼요','<div class="sc-foot">${regLabels()}만 적으면 시작돼요')
rep('<span style="white-space:nowrap">소속·나이·이름만</span> 적으면 바로 시작할 수 있어요.','<span style="white-space:nowrap">${regLabels()}만</span> 적으면 바로 시작할 수 있어요.')

# ── 방문객 등록 폼
rep("""      <div class="field"><label>소속</label><input class="inp" id="rSchool" placeholder="학교·기관·단체명" maxlength="30" autocomplete="off"></div>
      <div class="field"><label>나이</label><input class="inp" id="rAge" type="number" inputmode="numeric" min="1" max="120" placeholder="예: 12" autocomplete="off"></div>
      <div class="field"><label>이름</label><input class="inp" id="rName" placeholder="홍길동" maxlength="20" autocomplete="off"></div>
      <label class="consent"><input type="checkbox" id="rConsent"><span><b>개인정보 수집·이용 동의</b><br>행사 운영과 선물 지급 확인을 위해 소속·나이·이름을 수집하며,""",
"""      ${regFieldsHTML('r')}
      <div class="field"><label>이름</label><input class="inp" id="rName" placeholder="홍길동" maxlength="20" autocomplete="off"></div>
      <label class="consent"><input type="checkbox" id="rConsent"><span><b>개인정보 수집·이용 동의</b><br>행사 운영과 선물 지급 확인을 위해 ${regLabels()}을 수집하며,""")
rep("""  $('#rGo').onclick = async () => {   // 소속·나이·이름 (DB 열은 school·grade 그대로 씀: school = 소속, grade = 나이 숫자, gender 는 안 받음)
    const name = $('#rName').value.trim(), school = $('#rSchool').value.trim(), grade = readAge('#rAge'), gender = '';
    if(!school) return toast('소속을 적어주세요'), $('#rSchool').focus();
    if(!grade) return toast('나이를 적어주세요 (숫자)'), $('#rAge').focus();
    if(!name) return toast('이름을 적어주세요'), $('#rName').focus();""",
"""  $('#rGo').onclick = async () => {   // 항목은 regFields() (관리자 › 행사 설정). DB 열: school = 소속, grade = 나이, gender = 연락처
    const name = $('#rName').value.trim(), f = readRegFields('r'); if(f.err) return toast(f.err), $(f.focus).focus();
    const { school, grade, gender } = f;
    if(!name) return toast('이름을 적어주세요'), $('#rName').focus();""")

# ── 수기 도장 등록 폼
rep("""      <div class="field"><label>소속</label><input class="inp" id="nSchool" placeholder="학교·기관·단체명" maxlength="30" autocomplete="off"></div>
      <div class="field"><label>나이</label><input class="inp" id="nAge" type="number" inputmode="numeric" min="1" max="120" placeholder="예: 12" autocomplete="off"></div>""",
"""      ${regFieldsHTML('n')}""")
rep("""    const name = $('#nName').value.trim(), school = $('#nSchool').value.trim(), grade = readAge('#nAge'), gender = '';
    if(!school) return toast('소속을 적어주세요'), $('#nSchool').focus();
    if(!grade) return toast('나이를 적어주세요 (숫자)'), $('#nAge').focus();
    if(!name) return toast('이름을 적어주세요'), $('#nName').focus();""",
"""    const name = $('#nName').value.trim(), f = readRegFields('n'); if(f.err) return toast(f.err), $(f.focus).focus();
    const { school, grade, gender } = f;
    if(!name) return toast('이름을 적어주세요'), $('#nName').focus();""")
rep("""      $('#nName').value = ''; $('#nAge').value = '';   // 소속은 다음 학생(같은 단체)을 위해 남겨 둠""",
    """      $('#nName').value = ''; regFields().filter(f => f.k !== 'org').forEach(f => $('#n' + f.k).value = '');   // 소속은 다음 사람(같은 단체)을 위해 남겨 둠""")

# ── 관리자 표 4곳: 가변 열
rep("""<th>시각</th><th>이름</th><th>소속</th><th>나이</th><th>도장</th></tr></thead><tbody>${list.map(v => `<tr><td class="muted">${fmtTime(v.stampedAt)}</td><td><b>${esc(v.name || '')}</b></td><td>${esc(v.school || '')}</td><td>${esc(v.grade || '')}</td>""",
    """<th>시각</th><th>이름</th>${vColsTH()}<th>도장</th></tr></thead><tbody>${list.map(v => `<tr><td class="muted">${fmtTime(v.stampedAt)}</td><td><b>${esc(v.name || '')}</b></td>${vColsTD(v)}""")
rep("""<th>코드</th><th>이름</th><th>소속</th><th>나이</th><th>스탬프</th><th>설문</th><th>상태</th><th></th></tr></thead><tbody id="gBody">""",
    """<th>코드</th><th>이름</th>${vColsTH()}<th>스탬프</th><th>설문</th><th>상태</th><th></th></tr></thead><tbody id="gBody">""")
rep("""<td><b>${esc(v.name)}</b></td><td class="muted">${esc(v.school || '')}</td><td class="muted">${esc(v.grade || '')}</td><td class="num">${perVisitor[v.id]}</td>""",
    """<td><b>${esc(v.name)}</b></td>${vColsTD(v)}<td class="num">${perVisitor[v.id]}</td>""")
rep("""<tr><td colspan="8" class="empty">해당하는 달성자가 없어요</td></tr>""","""<tr><td colspan="${6 + vCols().length}" class="empty">해당하는 달성자가 없어요</td></tr>""")
rep("""<th>코드</th><th>이름</th><th>소속</th><th>나이</th><th>도장</th><th>등록</th><th></th></tr></thead><tbody>${rows.map(v => `<tr><td class="num" style="letter-spacing:.08em"><b>${shortCode(v.id)}</b></td><td><b>${esc(v.name)}</b></td><td class="muted">${esc(v.school || '')}</td><td class="muted">${esc(v.grade || '')}</td><td class="num">${v.n}</td><td class="muted">${fmtTime(v.createdAt)}</td>""",
    """<th>코드</th><th>이름</th>${vColsTH()}<th>도장</th><th>등록</th><th></th></tr></thead><tbody>${rows.map(v => `<tr><td class="num" style="letter-spacing:.08em"><b>${shortCode(v.id)}</b></td><td><b>${esc(v.name)}</b></td>${vColsTD(v)}<td class="num">${v.n}</td><td class="muted">${fmtTime(v.createdAt)}</td>""")
rep("""'<div class="empty">없어요. 이름 일부나 학교로 다시 찾아보세요</div>'""","""'<div class="empty">없어요. 이름 일부나 소속으로 다시 찾아보세요</div>'""")
rep("""<th>코드</th><th>이름</th><th>소속</th><th>나이</th><th>도장</th><th></th></tr></thead><tbody>${rows.map(v => `<tr><td class="num" style="letter-spacing:.08em"><b>${shortCode(v.id)}</b></td><td><b>${esc(v.name)}</b></td><td class="muted">${esc(v.school || '')}</td><td class="muted">${esc(v.grade || '')}</td><td class="num">${v.n}</td>""",
    """<th>코드</th><th>이름</th>${vColsTH()}<th>도장</th><th></th></tr></thead><tbody>${rows.map(v => `<tr><td class="num" style="letter-spacing:.08em"><b>${shortCode(v.id)}</b></td><td><b>${esc(v.name)}</b></td>${vColsTD(v)}<td class="num">${v.n}</td>""")

# ── CSV 3종
rep("""[['제출시각', '소속', '나이', '나이대', '성별', ...SURVEY.map(q => q.title)]].concat(rows.map(r => [new Date(r.at).toLocaleString('ko-KR'), r.school, r.grade, gradeGroup(r.grade), r.gender, ...SURVEY""",
    """[['제출시각', ...vCols().map(c => c.label), '나이대', ...SURVEY.map(q => q.title)]].concat(rows.map(r => [new Date(r.at).toLocaleString('ko-KR'), ...vCols().map(c => c.get(r)), gradeGroup(r.grade), ...SURVEY""")
rep("""[['시각', '부스번호', '부스명', '이름', '소속', '나이', '성별']].concat(stamps.slice().sort((a, b) => a.at - b.at).map(s => { const b = boothById(s.boothId), v = vmap[s.visitorId]; return [new Date(s.at).toLocaleString('ko-KR'), b?.n || '', b?.name || '', v?.name || '', v?.school || '', v?.grade || '', v?.gender || '']; }))""",
    """[['시각', '부스번호', '부스명', '이름', ...vCols().map(c => c.label)]].concat(stamps.slice().sort((a, b) => a.at - b.at).map(s => { const b = boothById(s.boothId), v = vmap[s.visitorId]; return [new Date(s.at).toLocaleString('ko-KR'), b?.n || '', b?.name || '', v?.name || '', ...vCols().map(c => c.get(v))]; }))""")
rep("""[['등록시각', '이름', '소속', '나이', '나이대', '성별', '스탬프수', '설문완료', '선물수령']].concat(visitors.map(v => [new Date(v.createdAt).toLocaleString('ko-KR'), v.name, v.school || '', v.grade || '', gradeGroup(v.grade), v.gender || '', cnt[v.id] || 0,""",
    """[['등록시각', '이름', ...vCols().map(c => c.label), '나이대', '스탬프수', '설문완료', '선물수령']].concat(visitors.map(v => [new Date(v.createdAt).toLocaleString('ko-KR'), v.name, ...vCols().map(c => c.get(v)), gradeGroup(v.grade), cnt[v.id] || 0,""")
rep("스탬프 기록은 방문객 이름·소속·나이와 함께 나가요.","스탬프 기록은 방문객 이름과 등록 항목(행사 설정에서 켠 것)과 함께 나가요.")

# ── 관리자 › 행사 설정: 등록 항목 카드 + 저장
rep("""        <div class="card"><div class="h-sec" style="margin:0 0 6px">자료 링크</div>""",
"""        <div class="card"><div class="h-sec" style="margin:0 0 6px">등록 항목</div><p class="small muted" style="margin-bottom:8px;line-height:1.6">방문객이 처음에 적는 칸. <b>이름</b>은 항상 받고, 아래는 켜고 끌 수 있어요. '필수'를 끄면 비워도 넘어가요. 바꾸면 이미 등록한 사람의 기록은 그대로예요.</p>
          <div style="display:flex;flex-direction:column;gap:8px">${REG_FIELD_DEFS.map(d => { const o = { ...d, ...(((S.settingsRaw || {}).regFields || {})[d.k] || {}) }; return `<div class="row" style="gap:14px;align-items:center"><b style="flex:0 0 56px">${d.label}</b><label class="small" style="display:flex;gap:6px;align-items:center"><input type="checkbox" id="rf_${d.k}_on" ${o.on ? 'checked' : ''}> 사용</label><label class="small" style="display:flex;gap:6px;align-items:center"><input type="checkbox" id="rf_${d.k}_req" ${o.req ? 'checked' : ''}> 필수</label></div>`; }).join('')}</div></div>
        <div class="card"><div class="h-sec" style="margin:0 0 6px">자료 링크</div>""")
rep("""      schedule: parse('#evSchedule', ['time', 'title', 'place']), resources: parse('#evResources', ['title', 'desc', 'url']) };""",
    """      schedule: parse('#evSchedule', ['time', 'title', 'place']), resources: parse('#evResources', ['title', 'desc', 'url']),
      regFields: Object.fromEntries(REG_FIELD_DEFS.map(d => [d.k, { on: $('#rf_' + d.k + '_on').checked, req: $('#rf_' + d.k + '_on').checked && $('#rf_' + d.k + '_req').checked }])) };""")

io.open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

# ── 축전 기본값 정리 (일정·자료 링크 비움, 설문 문구 '축전' → '행사'). 관리자 › 행사 설정/설문에서 채움
s=io.open(p,encoding='utf-8').read()
import re
s=re.sub(r"let SCHEDULE = \[   // 기본값\. 관리자 › 행사 설정에서 바꾸면 서버\(settings\) 값으로 덮임\n(?:  \{time:.*\n)+\];", "let SCHEDULE = [];   // 기본값 없음. 관리자 › 행사 설정 › 오늘의 일정에서 적으면 서버(settings) 값으로 채워짐", s, count=1)
s=re.sub(r"let RESOURCES = \[\n(?:  \{title:.*\n)+\];", "let RESOURCES = [];   // 기본값 없음. 관리자 › 행사 설정 › 자료 링크", s, count=1)
assert "let SCHEDULE = [];" in s and "let RESOURCES = [];" in s
s=s.replace("title: '오늘 축전은 전체적으로 어땠나요?'","title: '오늘 행사는 전체적으로 어땠나요?'")
io.open(p,'w',encoding='utf-8',newline='\n').write(s)
print('defaults ok')

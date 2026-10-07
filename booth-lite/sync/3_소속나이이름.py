import io, re
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    assert s.count(old)>=1, old[:90]
    if count==1: assert s.count(old)==1, ('multi', old[:90])
    s=s.replace(old,new) if count!=1 else s.replace(old,new,1)

# 나이대 그룹 (DB grade 열에 나이 숫자를 넣음)
rep("const gradeGroup = g => !g ? '' : g === '성인' ? '성인' : g[0] === '초' ? (+g[1] <= 3 ? '초저' : '초고') : g[0] === '중' ? '중' : '고';",
    "const gradeGroup = g => { const a = parseInt(g); return !g ? '' : isNaN(a) ? '기타' : a <= 12 ? '어린이' : a <= 18 ? '청소년' : '성인'; };   // 나이대. grade 열에 나이 숫자를 넣음(booth-lite)")
rep("function myLevel(){ const g = (S.me && S.me.grade) || ''; return g.startsWith('초') ? 'elem' : (g.startsWith('중') || g.startsWith('고')) ? 'secondary' : ''; }",
    "function myLevel(){ const a = parseInt((S.me && S.me.grade) || ''); return isNaN(a) ? '' : a <= 12 ? 'elem' : a <= 18 ? 'secondary' : ''; }   // 나이 기준: 12세 이하 어린이, 13~18 청소년")
# 홈·등록 문구
rep('<div class="sc-foot">학교·학년·이름만 적으면 시작돼요','<div class="sc-foot">소속·나이·이름만 적으면 시작돼요')
rep('<span style="white-space:nowrap">학교·학년·이름만</span> 적으면 바로 시작할 수 있어요.','<span style="white-space:nowrap">소속·나이·이름만</span> 적으면 바로 시작할 수 있어요.')
rep('placeholder="부스 이름, 번호, 학교"','placeholder="부스 이름, 번호"')
# 등록 폼
rep("""      <div class="field"><label id="rSchoolL">학교</label><input class="inp" id="rSchool" placeholder="학교명" maxlength="30" autocomplete="off"></div>
      <div class="field"><label>구분</label><div class="gsel four" id="rLevel"><button type="button" data-l="초">초등</button><button type="button" data-l="중">중등</button><button type="button" data-l="고">고등</button><button type="button" data-l="성인">성인</button></div></div>
      <div class="field" id="rGradeF" hidden><label>학년</label><div class="gsel" id="rGrade"></div></div>
      <div class="field"><label>이름</label><input class="inp" id="rName" placeholder="홍길동" maxlength="20" autocomplete="off"></div>
      <div class="field"><label>성별</label><div class="gsel" id="rGender"><button type="button" data-g="남">남</button><button type="button" data-g="여">여</button></div></div>
      <label class="consent"><input type="checkbox" id="rConsent"><span><b>개인정보 수집·이용 동의</b><br>행사 운영과 선물 지급 확인을 위해 학교·학년·이름·성별을 수집하며,""",
"""      <div class="field"><label>소속</label><input class="inp" id="rSchool" placeholder="학교·기관·단체명" maxlength="30" autocomplete="off"></div>
      <div class="field"><label>나이</label><input class="inp" id="rAge" type="number" inputmode="numeric" min="1" max="120" placeholder="예: 12" autocomplete="off"></div>
      <div class="field"><label>이름</label><input class="inp" id="rName" placeholder="홍길동" maxlength="20" autocomplete="off"></div>
      <label class="consent"><input type="checkbox" id="rConsent"><span><b>개인정보 수집·이용 동의</b><br>행사 운영과 선물 지급 확인을 위해 소속·나이·이름을 수집하며,""")
rep("""  let gender = '';
  $$('#rGender button').forEach(b => b.onclick = () => { gender = b.dataset.g; $$('#rGender button').forEach(x => x.classList.toggle('on', x === b)); });
  let level = '', gradeNo = '';   // 구분(초·중·고·성인) 따로, 학년 숫자 따로 → 저장은 '초3' 형태
  $$('#rLevel button').forEach(b => b.onclick = () => {
    level = b.dataset.l; gradeNo = ''; $$('#rLevel button').forEach(x => x.classList.toggle('on', x === b));
    const adult = level === '성인', n = level === '초' ? 6 : 3;
    $('#rGradeF').hidden = adult;
    $('#rGrade').innerHTML = adult ? '' : Array.from({ length: n }, (_, i) => `<button type="button" data-n="${i + 1}">${i + 1}학년</button>`).join('');
    $$('#rGrade button').forEach(g => g.onclick = () => { gradeNo = g.dataset.n; $$('#rGrade button').forEach(x => x.classList.toggle('on', x === g)); });
    $('#rSchoolL').textContent = adult ? '소속 (선택)' : '학교'; $('#rSchool').placeholder = adult ? '학교·기관명 (없으면 비워도 돼요)' : '학교명';   // 성인은 학교 대신 소속, 비워도 됨
  });
  $('#rGo').onclick = async () => {
    const name = $('#rName').value.trim(), school = $('#rSchool').value.trim();
    if(!level) return toast('초등·중등·고등·성인 중에 골라주세요');
    if(level !== '성인' && !gradeNo) return toast('학년을 골라주세요');
    const grade = level === '성인' ? '성인' : level + gradeNo;
    if(!school && grade !== '성인') return toast('학교를 적어주세요'), $('#rSchool').focus();
    if(!name) return toast('이름을 적어주세요'), $('#rName').focus();
    if(!gender) return toast('성별을 골라주세요');
    if(!$('#rConsent').checked)""",
"""  $('#rGo').onclick = async () => {   // 소속·나이·이름 (DB 열은 school·grade 그대로 씀: school = 소속, grade = 나이 숫자, gender 는 안 받음)
    const name = $('#rName').value.trim(), school = $('#rSchool').value.trim(), grade = readAge('#rAge'), gender = '';
    if(!school) return toast('소속을 적어주세요'), $('#rSchool').focus();
    if(!grade) return toast('나이를 적어주세요 (숫자)'), $('#rAge').focus();
    if(!name) return toast('이름을 적어주세요'), $('#rName').focus();
    if(!$('#rConsent').checked)""")
# readAge 헬퍼 (admPath 옆)
rep("function admPath(sub){ return '/' + CONFIG.adminPath + (sub || ''); }",
    "function admPath(sub){ return '/' + CONFIG.adminPath + (sub || ''); }\nfunction readAge(sel){ const a = parseInt($(sel).value); return a >= 1 && a <= 120 ? String(a) : ''; }   // 나이 입력칸 → '12' (범위 밖·빈칸이면 '')")
# 수기 도장 폼
rep("""      <div class="field"><label id="nSchoolL">학교</label><input class="inp" id="nSchool" placeholder="학교명" maxlength="30" autocomplete="off"></div>
      <div class="field"><label>구분</label><div class="gsel four" id="nLevel"><button type="button" data-l="초">초등</button><button type="button" data-l="중">중등</button><button type="button" data-l="고">고등</button><button type="button" data-l="성인">성인</button></div></div>
      <div class="field" id="nGradeF" hidden><label>학년</label><div class="gsel" id="nGrade"></div></div>
      <div class="field"><label>이름</label><input class="inp" id="nName" placeholder="홍길동" maxlength="20" autocomplete="off"></div>
      <div class="field"><label>성별</label><div class="gsel" id="nGender"><button type="button" data-g="남">남</button><button type="button" data-g="여">여</button></div></div>""",
"""      <div class="field"><label>소속</label><input class="inp" id="nSchool" placeholder="학교·기관·단체명" maxlength="30" autocomplete="off"></div>
      <div class="field"><label>나이</label><input class="inp" id="nAge" type="number" inputmode="numeric" min="1" max="120" placeholder="예: 12" autocomplete="off"></div>
      <div class="field"><label>이름</label><input class="inp" id="nName" placeholder="홍길동" maxlength="20" autocomplete="off"></div>""")
rep("""  let gender = '', level = '', gradeNo = '';
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
    $('#nGo').disabled = true;""",
"""  $('#nGo').onclick = async () => {
    if(!cur) return toast('먼저 부스를 골라주세요');
    const name = $('#nName').value.trim(), school = $('#nSchool').value.trim(), grade = readAge('#nAge'), gender = '';
    if(!school) return toast('소속을 적어주세요'), $('#nSchool').focus();
    if(!grade) return toast('나이를 적어주세요 (숫자)'), $('#nAge').focus();
    if(!name) return toast('이름을 적어주세요'), $('#nName').focus();
    $('#nGo').disabled = true;""")
rep("""      $('#nName').value = ''; gender = ''; gradeNo = ''; $$('#nGender button, #nGrade button').forEach(x => x.classList.remove('on'));   // 학교·구분은 다음 학생을 위해 남겨 둠""",
    """      $('#nName').value = ''; $('#nAge').value = '';   // 소속은 다음 학생(같은 단체)을 위해 남겨 둠""")
# 표 머리글·칸: 학교→소속, 학년→나이, 성별 칸 제거
rep("<th>시각</th><th>이름</th><th>학교</th><th>학년</th><th>성별</th><th>도장</th></tr></thead><tbody>${list.map(v => `<tr><td class=\"muted\">${fmtTime(v.stampedAt)}</td><td><b>${esc(v.name || '')}</b></td><td>${esc(v.school || '')}</td><td>${esc(v.grade || '')}</td><td>${esc(v.gender || '')}</td>",
    "<th>시각</th><th>이름</th><th>소속</th><th>나이</th><th>도장</th></tr></thead><tbody>${list.map(v => `<tr><td class=\"muted\">${fmtTime(v.stampedAt)}</td><td><b>${esc(v.name || '')}</b></td><td>${esc(v.school || '')}</td><td>${esc(v.grade || '')}</td>")
rep("<th>코드</th><th>이름</th><th>학교</th><th>학년</th><th>성별</th><th>스탬프</th>","<th>코드</th><th>이름</th><th>소속</th><th>나이</th><th>스탬프</th>")
rep("<td class=\"muted\">${esc(v.grade || '')}</td><td class=\"muted\">${esc(v.gender || '')}</td><td class=\"num\">${perVisitor[v.id]}</td>","<td class=\"muted\">${esc(v.grade || '')}</td><td class=\"num\">${perVisitor[v.id]}</td>")
rep("<tr><td colspan=\"9\" class=\"empty\">해당하는 달성자가 없어요</td></tr>","<tr><td colspan=\"8\" class=\"empty\">해당하는 달성자가 없어요</td></tr>")
rep("<th>코드</th><th>이름</th><th>학교</th><th>학년</th><th>도장</th><th>등록</th>","<th>코드</th><th>이름</th><th>소속</th><th>나이</th><th>도장</th><th>등록</th>")
rep("<th>코드</th><th>이름</th><th>학교</th><th>학년</th><th>도장</th><th></th>","<th>코드</th><th>이름</th><th>소속</th><th>나이</th><th>도장</th><th></th>")
rep('placeholder="이름, 학교, 교환권 코드"','placeholder="이름, 소속, 교환권 코드"')
rep("완주 전인 사람도 이름·학교·코드로 찾아요.","완주 전인 사람도 이름·소속·코드로 찾아요.")
rep('placeholder="이름, 학교, 코드" autocomplete="off" style="max-width:280px"','placeholder="이름, 소속, 코드" autocomplete="off" style="max-width:280px"')
rep('placeholder="이름, 학교, 코드 (두 글자 이상)"','placeholder="이름, 소속, 코드 (두 글자 이상)"')
rep('<input class="inp" id="bvQ" placeholder="이름·학교 검색"','<input class="inp" id="bvQ" placeholder="이름·소속 검색"')
rep("명 · 학년별 ${Object.entries(rows.reduce","명 · 나이대별 ${Object.entries(rows.reduce")
rep("[['제출시각', '학교', '학년', '학년군', '성별', ...SURVEY","[['제출시각', '소속', '나이', '나이대', '성별', ...SURVEY")
rep("스탬프 기록은 방문객 이름·학교·학년·성별과 함께 나가요. 명단에는 학년군(초저·초고·중·고·성인)과 설문 완료 시각이 붙어요.","스탬프 기록은 방문객 이름·소속·나이와 함께 나가요. 명단에는 나이대(어린이 ~12 · 청소년 13~18 · 성인 19~)와 설문 완료 시각이 붙어요.")
rep("[['시각', '부스번호', '부스명', '이름', '학교', '학년', '성별']]","[['시각', '부스번호', '부스명', '이름', '소속', '나이', '성별']]")
rep("[['등록시각', '이름', '학교', '학년', '학년군', '성별', '스탬프수', '설문완료', '선물수령']]","[['등록시각', '이름', '소속', '나이', '나이대', '성별', '스탬프수', '설문완료', '선물수령']]")
io.open(p,'w',encoding='utf-8',newline='\n').write(s)

# 대시보드
p=r'C:\dev\booth-lite\운영대시보드.html'
s=io.open(p,encoding='utf-8').read()
rep('<div class="t">학년군</div><div class="s">등록 기준</div>','<div class="t">나이대</div><div class="s">등록 기준</div>')
rep('<div class="t">학교 TOP 10</div>','<div class="t">소속 TOP 10</div>')
rep('<input class="inp" id="bvQ" placeholder="이름·학교 검색"','<input class="inp" id="bvQ" placeholder="이름·소속 검색"')
rep("<th>#</th><th>시각</th><th>이름</th><th>학교</th><th>학년</th><th>성별</th><th class=\"r\">도장</th>","<th>#</th><th>시각</th><th>이름</th><th>소속</th><th>나이</th><th class=\"r\">도장</th>")
rep("<td>${esc(r.grade || '')}</td><td>${esc(r.gender || '')}</td><td class=\"r\">${r.n}</td></tr>`).join('') || '<tr><td colspan=\"7\" class=\"empty\">없어요</td></tr>'",
    "<td>${esc(r.grade || '')}</td><td class=\"r\">${r.n}</td></tr>`).join('') || '<tr><td colspan=\"6\" class=\"empty\">없어요</td></tr>'")
rep("const gradeGroup = g => !g || g === '미입력' ? '미입력' : g === '성인' ? '성인' : g[0] === '초' ? (+g[1] <= 3 ? '초등 저학년' : '초등 고학년') : g[0] === '중' ? '중학생' : g[0] === '고' ? '고등학생' : '기타';",
    "const gradeGroup = g => { const a = parseInt(g); return !g || g === '미입력' ? '미입력' : isNaN(a) ? '기타' : a <= 12 ? '어린이 (~12세)' : a <= 18 ? '청소년 (13~18세)' : '성인 (19세~)'; };   // grade 열 = 나이 숫자(booth-lite)")
rep("const order = ['초등 저학년', '초등 고학년', '중학생', '고등학생', '성인', '기타', '미입력'], g = {};","const order = ['어린이 (~12세)', '청소년 (13~18세)', '성인 (19세~)', '기타', '미입력'], g = {};")
io.open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

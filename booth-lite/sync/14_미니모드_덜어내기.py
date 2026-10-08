# 14단계: 축전 전용 기능을 미니 모드(CONFIG.miniMode)에서 숨김. 13단계 뒤에 실행
#   삭제가 아니라 `CONFIG.miniMode ? '' : …` 조건 숨김 — 축전 앱 쪽 코드는 그대로 살아 있음
#   앱: 시간대 전환·대상 세그먼트·QR 제외·분류 색·엑셀/CSV·설문 링크 칸·일정·자료·교환 마감·데모 데이터·설문 탭(설문 끄면)·
#       부스 소개의 운영 시간/시간대/대상·등록 화면 1단계 문구·홈 검색창
#   대시보드: CONFIG.miniMode 플래그 추가 → 성별·소속 TOP10 카드 숨김
import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    n=s.count(old); assert n==count,(n,old[:80]); s=s.replace(old,new)

# 1. [시간] 시트: '다른 부스로 바뀜' 카드 + 카드의 🔁 칩. 확인 흐름이 이 칸들을 읽으므로 DOM 엔 두고 display:none → 기존 variant 는 그대로 보존(tSw 가 v 유무를 따라감)
rep("""<div class="card tight tsheet" style="margin-bottom:14px"><div class="kv">
        <label class="row" style="gap:8px;align-items:center;cursor:pointer"><input type="checkbox" id="tSw\"""",
    """<div class="card tight tsheet" style="margin-bottom:14px${CONFIG.miniMode ? ';display:none' : ''}"><div class="kv">
        <label class="row" style="gap:8px;align-items:center;cursor:pointer"><input type="checkbox" id="tSw\"""")
rep("""<span class="mchip ${b.variant ? 'on' : ''}" data-m="variant">""",
    """<span class="mchip ${b.variant ? 'on' : ''}" data-m="variant"${CONFIG.miniMode ? ' style="display:none"' : ''}>""")
# 2. 부스 카드 대상 세그먼트(.tsel). hidden input(data-f=target) 은 남아 저장 때 target '' 그대로
rep("""<div class="tsel" data-tsel="${i}" title="대상: 초등 이하로 두면 중고등학생 폰에는 안 보이고 도장도 안 찍혀요">${TARGETS.map(t => `<button type="button" class="${(b.target || '') === t.id ? 'on' : ''}" data-t="${t.id}">${t.name}</button>`).join('')}</div>""",
    """${CONFIG.miniMode ? '' : `<div class="tsel" data-tsel="${i}" title="대상: 초등 이하로 두면 중고등학생 폰에는 안 보이고 도장도 안 찍혀요">${TARGETS.map(t => `<button type="button" class="${(b.target || '') === t.id ? 'on' : ''}" data-t="${t.id}">${t.name}</button>`).join('')}</div>`}""")
# 3·4·5. 부스 툴바: 엑셀 양식·엑셀/CSV 불러오기·CSV, QR 제외·분류 색 버튼 + 그 핸들러
rep("""      <button class="btn sm line" id="bXlsx">엑셀 양식 내려받기</button>
      <label class="btn sm line" style="cursor:pointer">엑셀·CSV 불러오기<input type="file" accept=".xlsx,.csv,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" id="bImp" hidden></label>
      <button class="btn xs soft" id="bCsv" title="예전 방식">CSV</button>
""",
    """      ${CONFIG.miniMode ? '' : `<button class="btn sm line" id="bXlsx">엑셀 양식 내려받기</button>
      <label class="btn sm line" style="cursor:pointer">엑셀·CSV 불러오기<input type="file" accept=".xlsx,.csv,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" id="bImp" hidden></label>
      <button class="btn xs soft" id="bCsv" title="예전 방식">CSV</button>`}
""")
rep("""      <button class="btn sm line" id="bNoStamp" title="QR 안 하는(도장 없는) 부스 고르기">QR 제외</button>
      <button class="btn sm line" id="bColors" title="분류별 색 바꾸기 (홈 칩·지도·QR 인쇄물에 반영)">분류 색</button>
""",
    """      ${CONFIG.miniMode ? '' : `<button class="btn sm line" id="bNoStamp" title="QR 안 하는(도장 없는) 부스 고르기">QR 제외</button>
      <button class="btn sm line" id="bColors" title="분류별 색 바꾸기 (홈 칩·지도·QR 인쇄물에 반영)">분류 색</button>`}
""")
rep("""  $('#bNoStamp').textContent = noStampLabel();
  $('#bNoStamp').onclick = () => openPickSheet({""",
    """  if(!CONFIG.miniMode){ $('#bNoStamp').textContent = noStampLabel();   // 미니 모드: 버튼 없음
  $('#bNoStamp').onclick = () => openPickSheet({""")
rep("""after: () => { $('#bNoStamp').textContent = noStampLabel(); } });
""",
    """after: () => { $('#bNoStamp').textContent = noStampLabel(); } }); }
""")
rep("  $('#bColors').onclick = openColorSheet;", "  if(!CONFIG.miniMode) $('#bColors').onclick = openColorSheet;")
rep("  $('#bXlsx').onclick = async () => {", "  if(!CONFIG.miniMode) $('#bXlsx').onclick = async () => {")
rep("  $('#bCsv').onclick = () => download(", "  if(!CONFIG.miniMode) $('#bCsv').onclick = () => download(")
rep("  $('#bImp').onchange = async e => {", "  if(!CONFIG.miniMode) $('#bImp').onchange = async e => {")

# 8. 행사 설정: 설문 링크·최소 시간·구글폼 항목 ID + 안내 문단
rep("""        <div class="field"><label>설문 링크 (구글폼 등 · 선택)</label><input class="inp" id="evSurvey" value="${esc(CONFIG.surveyUrl)}" placeholder="비우면 앱 안의 설문(설문 탭)을 써요"></div>
        <div class="row" style="gap:10px;align-items:flex-start">""",
    """        ${CONFIG.miniMode ? '' : `<div class="field"><label>설문 링크 (구글폼 등 · 선택)</label><input class="inp" id="evSurvey" value="${esc(CONFIG.surveyUrl)}" placeholder="비우면 앱 안의 설문(설문 탭)을 써요"></div>
        <div class="row" style="gap:10px;align-items:flex-start">""")
rep("""를 적어두면, 제출 후 그 링크를 누른 폰은 <b>자동으로 완료 처리</b>돼요.</p>
""",
    """를 적어두면, 제출 후 그 링크를 누른 폰은 <b>자동으로 완료 처리</b>돼요.</p>`}
""")
# 11. 선물 교환 마감 칸
rep("""        <div class="field"><label>선물 교환 마감 (안내 문구)</label><input class="inp" id="evDeadline" value="${esc(CONFIG.giftDeadline)}" maxlength="20" placeholder="예: 15:50"></div>
""",
    """        ${CONFIG.miniMode ? '' : `<div class="field"><label>선물 교환 마감 (안내 문구)</label><input class="inp" id="evDeadline" value="${esc(CONFIG.giftDeadline)}" maxlength="20" placeholder="예: 15:50"></div>`}
""")
# 9. 오늘의 일정 카드
rep("""        <div class="card"><div class="h-sec" style="margin:0 0 6px">오늘의 일정</div><p class="small muted" style="margin-bottom:8px;line-height:1.6">한 줄에 하나 · <code>시간 | 제목 | 장소·설명</code> · 시간은 <code>10:00</code> 또는 <code>09:00~10:00</code></p>
          <textarea class="inp" id="evSchedule" style="min-height:160px;font-size:14px">${esc(lines(SCHEDULE, x => [x.time, x.title, x.place].join(' | ')))}</textarea></div>
""",
    """        ${CONFIG.miniMode ? '' : `<div class="card"><div class="h-sec" style="margin:0 0 6px">오늘의 일정</div><p class="small muted" style="margin-bottom:8px;line-height:1.6">한 줄에 하나 · <code>시간 | 제목 | 장소·설명</code> · 시간은 <code>10:00</code> 또는 <code>09:00~10:00</code></p>
          <textarea class="inp" id="evSchedule" style="min-height:160px;font-size:14px">${esc(lines(SCHEDULE, x => [x.time, x.title, x.place].join(' | ')))}</textarea></div>`}
""")
# 10. 자료 링크 카드
rep("""        <div class="card"><div class="h-sec" style="margin:0 0 6px">자료 링크</div><p class="small muted" style="margin-bottom:8px;line-height:1.6">한 줄에 하나 · <code>제목 | 설명 | 주소(https://…)</code></p>
          <textarea class="inp" id="evResources" style="min-height:90px;font-size:14px">${esc(lines(RESOURCES, x => [x.title, x.desc, x.url].join(' | ')))}</textarea></div>
""",
    """        ${CONFIG.miniMode ? '' : `<div class="card"><div class="h-sec" style="margin:0 0 6px">자료 링크</div><p class="small muted" style="margin-bottom:8px;line-height:1.6">한 줄에 하나 · <code>제목 | 설명 | 주소(https://…)</code></p>
          <textarea class="inp" id="evResources" style="min-height:90px;font-size:14px">${esc(lines(RESOURCES, x => [x.title, x.desc, x.url].join(' | ')))}</textarea></div>`}
""")
# 8·9·10·11 저장: 미니 모드는 없는 칸(surveyUrl·surveyMinSec·surveyCodeField·giftDeadline·schedule·resources)을 data 에서 뺌 → savePatch 가 서버 값과 병합하므로 기존 값 유지
rep("""    const surveyMinSec = parseInt($('#evSurveySec').value); if(!(surveyMinSec >= 0 && surveyMinSec <= 600)) return toast('설문 최소 시간은 0~600초 사이로');
    const surveyCodeField = $('#evSurveyField').value.trim(); if(surveyCodeField && !/^[\\w.]+$/.test(surveyCodeField)) return toast('항목 ID는 entry.숫자 형식이에요');
""",
    """    const full = !CONFIG.miniMode;   // 미니 모드: 설문 링크·마감·일정·자료 칸이 없음 → data 에서 빼면 savePatch 병합으로 기존 값 유지
    const surveyMinSec = full ? parseInt($('#evSurveySec').value) : undefined; if(full && !(surveyMinSec >= 0 && surveyMinSec <= 600)) return toast('설문 최소 시간은 0~600초 사이로');
    const surveyCodeField = full ? $('#evSurveyField').value.trim() : undefined; if(full && surveyCodeField && !/^[\\w.]+$/.test(surveyCodeField)) return toast('항목 ID는 entry.숫자 형식이에요');
""")
rep("""stampGoal: goal, surveyUrl: $('#evSurvey').value.trim(), surveyMinSec, surveyCodeField, giftDeadline: $('#evDeadline').value.trim(), giftPlace:""",
    """stampGoal: goal, ...(full ? { surveyUrl: $('#evSurvey').value.trim(), surveyMinSec, surveyCodeField, giftDeadline: $('#evDeadline').value.trim() } : {}), giftPlace:""")
rep("""      schedule: parse('#evSchedule', ['time', 'title', 'place']), resources: parse('#evResources', ['title', 'desc', 'url']), surveyOn: $('#evSurveyOn').checked,""",
    """      ...(full ? { schedule: parse('#evSchedule', ['time', 'title', 'place']), resources: parse('#evResources', ['title', 'desc', 'url']) } : {}), surveyOn: $('#evSurveyOn').checked,""")
rep("""    if((data.surveyUrl && !/^https?:\\/\\//.test(data.surveyUrl)) || data.resources.some(r => !/^https?:\\/\\//.test(r.url))) return toast('링크는 http:// 또는 https:// 로 시작해야 해요');""",
    """    if(full && ((data.surveyUrl && !/^https?:\\/\\//.test(data.surveyUrl)) || data.resources.some(r => !/^https?:\\/\\//.test(r.url)))) return toast('링크는 http:// 또는 https:// 로 시작해야 해요');""")

# 9. 홈 일정 띠 + 안내 화면 '오늘의 일정'
rep("""    ${next ? `<div class="notice">${I.bell}<span>""", """    ${!CONFIG.miniMode && next ? `<div class="notice">${I.bell}<span>""")
rep("""    <div class="card"><div class="h-sec" style="margin:0 0 6px">오늘의 일정</div>
      <div class="timeline">${SCHEDULE.map(s => `<div class="tl"><div class="tm">${schedTimeHTML(s.time)}</div><div><div class="t">${esc(s.title)}</div><div class="s">${esc(s.place)}</div></div></div>`).join('')}</div></div>
    <div class="h-sec">자료</div>
    ${RESOURCES.map(r => `<a class="link" href="${esc(r.url)}" target="_blank" rel="noopener"><span class="ic">${I.doc}</span><div class="grow"><div class="t">${esc(r.title)}</div><div class="s">${esc(r.desc)}</div></div><span class="bgo">${I.chev}</span></a>`).join('')}
""",
    """    ${CONFIG.miniMode ? '' : `<div class="card"><div class="h-sec" style="margin:0 0 6px">오늘의 일정</div>
      <div class="timeline">${SCHEDULE.map(s => `<div class="tl"><div class="tm">${schedTimeHTML(s.time)}</div><div><div class="t">${esc(s.title)}</div><div class="s">${esc(s.place)}</div></div></div>`).join('')}</div></div>
    <div class="h-sec">자료</div>
    ${RESOURCES.map(r => `<a class="link" href="${esc(r.url)}" target="_blank" rel="noopener"><span class="ic">${I.doc}</span><div class="grow"><div class="t">${esc(r.title)}</div><div class="s">${esc(r.desc)}</div></div><span class="bgo">${I.chev}</span></a>`).join('')}`}
""")
# 11. 안내 화면 기본 문장의 '교환은 HH:MM까지예요'
rep("""${CONFIG.giftDeadline ? ` 교환은 ${esc(CONFIG.giftDeadline)}까지예요.` : ''}""",
    """${CONFIG.giftDeadline && !CONFIG.miniMode ? ` 교환은 ${esc(CONFIG.giftDeadline)}까지예요.` : ''}""")

# 13. 데이터 탭 데모 데이터 버튼
rep("""        ${local ? `<div class="card"><div class="h-sec" style="margin:0 0 10px">데모</div>""",
    """        ${local && !CONFIG.miniMode ? `<div class="card"><div class="h-sec" style="margin:0 0 10px">데모</div>""")
# 14. 관리자 탭: 설문 사용을 끄면 '설문' 탭 숨김(탭 렌더 시점에 필터 → 켜면 다시 보임)
rep("""    <div class="adm-nav no-print">${ADM_TABS.map(([k, l]) =>""",
    """    <div class="adm-nav no-print">${ADM_TABS.filter(([k]) => !(CONFIG.miniMode && k === 'survey' && !surveyOn())).map(([k, l]) =>""")

# 16. 방문객 부스 소개: 대상 pill · 운영 시간 줄 · 시간대 전환 줄
rep("""${b.target ? `<span class="pill" style="margin-left:6px">${esc(targetName(b.target))} 대상</span>` : ''}""",
    """${b.target && !CONFIG.miniMode ? `<span class="pill" style="margin-left:6px">${esc(targetName(b.target))} 대상</span>` : ''}""")
rep("""${b.hours ? `<div class="k" style="margin-top:4px">운영 시간</div>""", """${b.hours && !CONFIG.miniMode ? `<div class="k" style="margin-top:4px">운영 시간</div>""")
rep("""${b.variant && b.variant.at ? `<div class="k" style="margin-top:4px">시간대</div>""", """${!CONFIG.miniMode && b.variant && b.variant.at ? `<div class="k" style="margin-top:4px">시간대</div>""")

# 17. 등록 화면 3단계: 1단계 '부스에서 도장 받기', 3단계는 설문 안 쓰면 '선물 받기'
rep("""      <div class="step"><div class="ic">📱</div><div class="t">부스 QR 찍기</div><div class="s">폰 카메라로</div></div>
""",
    """      ${CONFIG.miniMode ? `<div class="step"><div class="ic">🖐️</div><div class="t">부스에서 도장 받기</div><div class="s">체험을 마치면</div></div>` : `<div class="step"><div class="ic">📱</div><div class="t">부스 QR 찍기</div><div class="s">폰 카메라로</div></div>`}
""")
rep("""<div class="step"><div class="ic">🎁</div><div class="t">설문 후 선물</div><div class="s">${esc(giftPlace())}에서</div></div>""",
    """<div class="step"><div class="ic">🎁</div><div class="t">${CONFIG.miniMode && !surveyOn() ? '선물 받기' : '설문 후 선물'}</div><div class="s">${esc(giftPlace())}에서</div></div>""")

# 18. 홈 검색 입력칸(분류 칩은 유지). S.q 는 '' 그대로라 filteredBooths 는 전체 목록
rep("""    <div class="searchbar">${I.search}<input id="q" placeholder="부스 이름, 번호" value="${esc(S.q)}" autocomplete="off"></div>
""",
    """    ${CONFIG.miniMode ? '' : `<div class="searchbar">${I.search}<input id="q" placeholder="부스 이름, 번호" value="${esc(S.q)}" autocomplete="off"></div>`}
""")
rep("""  $('#q').oninput = e => { S.q = e.target.value; draw(); };""",
    """  const qInp = $('#q'); if(qInp) qInp.oninput = e => { S.q = e.target.value; draw(); };   // 미니 모드: 검색창 없음""")

io.open(p,'w',encoding='utf-8',newline='\n').write(s); print('app ok')

# ---------------- 15. 운영대시보드: 성별·소속 TOP10 카드 숨김 (나이대는 유지) ----------------
p=r'C:\dev\booth-lite\운영대시보드.html'
s=io.open(p,encoding='utf-8').read()
rep("""  timeoutMs: 20000,
};""",
    """  timeoutMs: 20000,
  miniMode: true,             // booth-lite: 성별·소속 TOP10 카드 숨김 (히트맵은 HTML 에서 hidden)
};""")
rep("""      <div class="h" style="margin-top:14px"><div><div class="t">성별</div></div></div>
      <div class="dist" id="gender" style="max-height:none;overflow:visible"></div>
""",
    """      <div id="genderSec"><div class="h" style="margin-top:14px"><div><div class="t">성별</div></div></div>
      <div class="dist" id="gender" style="max-height:none;overflow:visible"></div></div>
""")
rep("""    <div class="card c4">
      <div class="h"><div><div class="t">소속 TOP 10</div><div class="s">등록 인원</div></div></div>""",
    """    <div class="card c4" id="schoolsCard">
      <div class="h"><div><div class="t">소속 TOP 10</div><div class="s">등록 인원</div></div></div>""")
rep("""const $ = (s, el = document) => el.querySelector(s), $$ = (s, el = document) => [...el.querySelectorAll(s)];
""",
    """const $ = (s, el = document) => el.querySelector(s), $$ = (s, el = document) => [...el.querySelectorAll(s)];
if(CONFIG.miniMode){ $('#genderSec').hidden = true; $('#schoolsCard').hidden = true; }   // 미니 모드: 성별·소속 TOP10 숨김(요소는 남겨 둠)
""")
io.open(p,'w',encoding='utf-8',newline='\n').write(s); print('dash ok')

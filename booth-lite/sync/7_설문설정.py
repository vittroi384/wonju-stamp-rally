# 7단계: 설문 사용/안 함 토글(settings.surveyOn) + 기본 문항을 일반 부스 행사용으로. 6단계 뒤에 실행
import io, re
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
def rep(old,new):
    global s
    assert s.count(old)==1, (s.count(old), old[:100])
    s=s.replace(old,new,1)

# 기본 문항 (축전 전용 문항 제거)
start=s.index("const DEFAULT_SURVEY = ["); end=s.index("];", start)+2
s=s[:start]+"""const DEFAULT_SURVEY = [   // booth-lite 기본 문항. 관리자 › 설문에서 바꿈. 행사 설정에서 '설문 사용'을 끄면 완주 즉시 교환권
  { id: 'overall', type: 'scale',  title: '오늘 체험은 전체적으로 어땠나요?', sub: '가장 가까운 표정을 골라주세요', required: true },
  { id: 'best',    type: 'booth',  title: '가장 재미있었던 부스는?', sub: '도장 찍은 부스 중에서 골라주세요', required: true },
  { id: 'why',     type: 'multi',  title: '그 부스가 좋았던 이유는?', sub: '여러 개 골라도 돼요', required: true, opts: ['직접 만들어서', '설명이 쉬웠어서', '결과물을 가져가서', '신기한 걸 봐서', '친구랑 같이 해서', '선생님이 친절해서'] },
  { id: 'count',   type: 'single', title: '도장 모으기는 어땠나요?', required: true, opts: ['쉬웠어요', '딱 적당했어요', '조금 힘들었어요', '너무 많았어요'] },
  { id: 'again',   type: 'single', title: '다음에도 참여하고 싶나요?', required: true, opts: ['꼭 할래요', '아마 할 것 같아요', '잘 모르겠어요'] },
  { id: 'free',    type: 'text',   title: '하고 싶은 말이 있다면 적어주세요', sub: '불편했던 점, 바라는 점 뭐든 좋아요', required: false },
];"""+s[end:]

# surveyOn 헬퍼
rep("const vTag = v => v && v.no ? `${v.no}번` : shortCode(v.id);",
    "const vTag = v => v && v.no ? `${v.no}번` : shortCode(v.id);\nconst surveyOn = () => !(S.settingsRaw && S.settingsRaw.surveyOn === false);   // 행사 설정 '설문 사용'. 끄면 완주 즉시 교환권(설문 완료로 자동 기록)")

# 내 스탬프: 설문 안 쓰면 완주 즉시 완료 처리
rep("""  if(S.surveyReturn){   // 구글폼 확인 메시지의 링크(?survey)로 돌아온 경우 — 완주자면 바로 완료 처리""",
    """  if(!surveyOn() && done && !S.pending.length && !S.me.surveyAt){ markSurveyDone().then(renderMy); return; }   // 설문 안 씀 → 완주 즉시 교환권
  if(S.surveyReturn){   // 구글폼 확인 메시지의 링크(?survey)로 돌아온 경우 — 완주자면 바로 완료 처리""")
# 홈: 완주했는데 설문 안 쓰면 바로 처리해서 '설문 참여하면' 문구가 안 뜨게
rep("  const title = done ? (S.me.surveyAt || S.me.giftAt ?",
    "  if(!surveyOn() && done && !S.pending.length && !S.me.surveyAt){ markSurveyDone().then(renderHome); return; }\n  const title = done ? (S.me.surveyAt || S.me.giftAt ?")
# 설문 화면 직접 진입 막기
rep("  if(S.me.surveyAt) return go('/my', true);\n", "  if(S.me.surveyAt || !surveyOn()) return go('/my', true);\n")
# 관리자 선물 수령 QR 스캔: 설문 안 쓰면 설문 안 봄
rep("ok = done && v.surveyAt && !v.giftAt;", "ok = done && (v.surveyAt || !surveyOn()) && !v.giftAt;")
rep("!done ? `아직 완주 전 (도장 ${n}/${CONFIG.stampGoal})` : !v.surveyAt ? '설문을 아직 안 했어요' : '';",
    "!done ? `아직 완주 전 (도장 ${n}/${CONFIG.stampGoal})` : (!v.surveyAt && surveyOn()) ? '설문을 아직 안 했어요' : '';")
# 행사 설정: 설문 사용 체크 + 저장
rep("""        <div class="field"><label>설문 링크 (구글폼 등 · 선택)</label>""",
    """        <label class="small" style="display:flex;gap:8px;align-items:center;margin:2px 0 12px;font-weight:700"><input type="checkbox" id="evSurveyOn" ${surveyOn() ? 'checked' : ''}> 설문 사용 <span class="muted" style="font-weight:600">— 끄면 완주하자마자 교환권이 열려요 (폰 없는 어린이도 선물 수령 가능)</span></label>
        <div class="field"><label>설문 링크 (구글폼 등 · 선택)</label>""")
rep("""      schedule: parse('#evSchedule', ['time', 'title', 'place']), resources: parse('#evResources', ['title', 'desc', 'url']),""",
    """      schedule: parse('#evSchedule', ['time', 'title', 'place']), resources: parse('#evResources', ['title', 'desc', 'url']), surveyOn: $('#evSurveyOn').checked,""")
# 설문 탭 안내
rep("<b>지금 방식: ${mode === 'link' ? '외부 설문 링크(구글폼 등)' : mode === 'app' ? '앱 안의 설문' : '설문 없음 (자기신고 버튼만)'}</b>",
    "<b>지금 방식: ${!surveyOn() ? '설문 안 씀 (행사 설정에서 꺼둠 → 완주 즉시 교환권)' : mode === 'link' ? '외부 설문 링크(구글폼 등)' : mode === 'app' ? '앱 안의 설문' : '설문 없음 (자기신고 버튼만)'}</b>")
io.open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

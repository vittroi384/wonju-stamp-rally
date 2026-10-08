# 13단계: 선물 안내 문구를 관리자 › 행사 설정에서 바꾸게. 12단계 뒤에 실행
#   giftPlace — 선물 받는 곳(기본 '운영본부'). 완주·교환권·등록 단계·도장 화면·안내 화면의 "운영본부에서" 자리에 들어감
#   giftText  — 안내 화면 '선물 교환' 카드 본문(여러 줄). 비우면 기존 기본 문장 그대로
import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    n=s.count(old); assert n==count,(n,old[:80]); s=s.replace(old,new)

# CONFIG 기본값
rep("  giftDeadline: '15:50',                 // 선물 교환 마감(안내 화면 문구)\n",
    "  giftDeadline: '15:50',                 // 선물 교환 마감(안내 화면 문구)\n"
    "  giftPlace: '운영본부',                 // 선물 받는 곳. 완주·교환권·안내 문구의 '운영본부' 자리 (관리자 › 행사 설정)\n"
    "  giftText: '',                          // 안내 화면 '선물 교환' 카드 본문. 비우면 기본 문장 (관리자 › 행사 설정)\n")
# 설정 키 + 헬퍼
rep("const SETTING_KEYS = ['eventTitle', 'eventDate', 'venue', 'stampGoal', 'surveyUrl', 'surveyMinSec', 'surveyCodeField', 'giftDeadline', 'contact', 'notice'];",
    "const SETTING_KEYS = ['eventTitle', 'eventDate', 'venue', 'stampGoal', 'surveyUrl', 'surveyMinSec', 'surveyCodeField', 'giftDeadline', 'giftPlace', 'giftText', 'contact', 'notice'];\n"
    "const giftPlace = () => (CONFIG.giftPlace || '운영본부').trim();   // 선물 받는 곳 — 비워 저장해도 기본값")
# 표시 자리 5곳
rep("`<b>완주!</b> 운영본부에서<br>선물 받아가세요`", "`<b>완주!</b> ${esc(giftPlace())}에서<br>선물 받아가세요`")
rep('<div class="step"><div class="ic">🎁</div><div class="t">설문 후 선물</div><div class="s">운영본부에서</div></div>',
    '<div class="step"><div class="ic">🎁</div><div class="t">설문 후 선물</div><div class="s">${esc(giftPlace())}에서</div></div>')
rep("설문 참여 완료 · 운영본부에서 선물 받아가세요</div>", "설문 참여 완료 · ${esc(giftPlace())}에서 선물 받아가세요</div>")
rep("${done ? '<p class=\"stamp-p\">운영본부에서 선물을 받아가세요</p>' : ''}", "${done ? `<p class=\"stamp-p\">${esc(giftPlace())}에서 선물을 받아가세요</p>` : ''}")
rep('<div class="card"><p class="desc">부스 ${CONFIG.stampGoal}곳의 도장을 모으고 <b>설문</b>에 참여하면 <b>운영본부</b>에서 선물을 드려요. 내 스탬프 화면의 교환권을 보여주세요.${CONFIG.giftDeadline ? ` 교환은 ${esc(CONFIG.giftDeadline)}까지예요.` : \'\'}</p></div>',
    '<div class="card"><p class="desc">${CONFIG.giftText ? esc(CONFIG.giftText).replace(/\\n/g, \'<br>\') : `부스 ${CONFIG.stampGoal}곳의 도장을 모으고 ${surveyOn() ? \'<b>설문</b>에 참여하면 \' : \'\'}<b>${esc(giftPlace())}</b>에서 선물을 드려요. 내 스탬프 화면의 교환권을 보여주세요.${CONFIG.giftDeadline ? ` 교환은 ${esc(CONFIG.giftDeadline)}까지예요.` : \'\'}`}</p></div>')
# 관리자 › 행사 설정 입력칸 + 저장
rep('<div class="field"><label>선물 교환 마감 (안내 문구)</label><input class="inp" id="evDeadline" value="${esc(CONFIG.giftDeadline)}" maxlength="20" placeholder="예: 15:50"></div>\n',
    '<div class="field"><label>선물 교환 마감 (안내 문구)</label><input class="inp" id="evDeadline" value="${esc(CONFIG.giftDeadline)}" maxlength="20" placeholder="예: 15:50"></div>\n'
    '        <div class="field"><label>선물 받는 곳 (완주·교환권 화면의 "○○에서 선물 받아가세요")</label><input class="inp" id="evGiftPlace" value="${esc(CONFIG.giftPlace)}" maxlength="20" placeholder="운영본부"></div>\n'
    '        <div class="field"><label>선물 교환 안내 (안내 화면 · 비우면 기본 문장)</label><textarea class="inp" id="evGiftText" style="min-height:80px;font-size:14px" maxlength="300" placeholder="예: 부스 7곳 도장을 다 모으면 안내데스크에서 선물을 드려요. 교환권 화면을 보여주세요.">${esc(CONFIG.giftText)}</textarea></div>\n')
rep("giftDeadline: $('#evDeadline').value.trim(), contact: $('#evContact').value.trim(),",
    "giftDeadline: $('#evDeadline').value.trim(), giftPlace: $('#evGiftPlace').value.trim(), giftText: $('#evGiftText').value.trim(), contact: $('#evContact').value.trim(),")
io.open(p,'w',encoding='utf-8',newline='\n').write(s); print('ok')

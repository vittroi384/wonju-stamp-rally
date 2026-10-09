# 17단계: 첫 화면(등록) — 실물 도장이 없는 행사라 가운데 칸 'QR로 체험 N개 완료하기 · 13~19번 부스', 소개 문장 '체험이 기록돼요'. 16단계 뒤에 실행
import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
old='<div class="step"><div class="ic">🟡</div><div class="t">도장 ${CONFIG.stampGoal}개 모으기</div><div class="s">부스 어디든</div></div>'
new='<div class="step"><div class="ic">🟡</div><div class="t">QR로 체험 ${CONFIG.stampGoal}개 완료하기</div><div class="s">13~19번 부스</div></div>'
def rep(old,new):
    global s
    if old not in s and new in s: print('already patched:', new[:30]); return
    assert s.count(old)==1, (s.count(old), old[:60]); s=s.replace(old,new)
rep(old,new)
rep('부스에 붙은 QR을 찍으면 도장이 찍혀요.', '부스에 붙은 QR을 찍으면 체험이 기록돼요.')
io.open(p,'w',encoding='utf-8',newline='\n').write(s); print('ok')

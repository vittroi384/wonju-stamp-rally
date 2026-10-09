# 19단계: 화면 곳곳에 글자로 박혀 있던 '운영본부'를 선물 받는 곳(giftPlace, 관리자 › 행사 설정) 으로. 18단계 뒤에 실행
#   축전 앱은 실제로 운영본부라 그대로, 부스 행사는 선물 장소가 따로(예: 16번 부스)라 한 화면에 두 장소가 같이 뜨던 문제
import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
R=[
 ("`운영본부로 오세요 <button", "`${esc(giftPlace())}로 오세요 <button"),
 ("코드를 모르면 운영본부에서 이름으로 찾아드려요.", "코드를 모르면 ${esc(giftPlace())}에서 이름으로 찾아드려요."),
 ("교환권을 운영본부에서 보여주고 선물을 받아가세요.'", "교환권을 ' + esc(giftPlace()) + '에서 보여주고 선물을 받아가세요.'"),
 ("운영본부(정문 오른쪽) 담당자에게 이 화면을 보여주세요.", "${esc(giftPlace())} 담당자에게 이 화면을 보여주세요."),
 ("바로 교환권이 나와요. <b>운영본부</b>에서 선물을 받아요.", "바로 교환권이 나와요. <b>${esc(giftPlace())}</b>에서 선물을 받아요."),
 ("교환권이 나오면 <b>운영본부</b>에서", "교환권이 나오면 <b>${esc(giftPlace())}</b>에서"),
]
if all(n in s for o,n in R): print('already patched'); raise SystemExit
for o,n in R:
    assert s.count(o)==1,(s.count(o),o); s=s.replace(o,n)
io.open(p,'w',encoding='utf-8',newline='\n').write(s); print('ok')

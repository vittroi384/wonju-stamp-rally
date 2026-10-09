# 16단계: QR 인쇄 카드 아래 참여 안내에서 '도장 N개를 모아 주세요' 줄을 빼고 2단계로. 15단계 뒤에 실행
#   선물 받는 곳은 관리자 › 행사 설정 › 선물 받는 곳(giftPlace) 값을 그대로 씀
import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
old='<div><i>2</i><div>도장 <b>${goal}개</b>를 모아 주세요<small>앱의 별이 하나씩 채워집니다</small></div></div><div><i>3</i><div>${s3}</div></div>'
new='<div><i>2</i><div>${s3}</div></div>'
if old not in s and new in s: print('already patched'); raise SystemExit
assert s.count(old)==1, s.count(old)
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='\n').write(s); print('ok')

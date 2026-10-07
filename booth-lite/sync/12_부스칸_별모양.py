# 12단계: 수기 도장 카드·확인 화면의 1~7 부스 칸을 도장 칸과 같은 별 모양(clip-path --star)으로. 11단계 뒤에 실행
import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
old=".bprog{display:flex;gap:4px;margin-top:7px;flex-wrap:wrap}.bprog span{width:26px;height:26px;border-radius:50%;background:var(--card);border:1.5px solid var(--line);display:grid;place-items:center;font-size:11.5px;font-weight:800;color:var(--ink-3)}.bprog span.on{background:var(--sun);border-color:var(--sun);color:var(--ink)}.bprog span.me{box-shadow:0 0 0 2px var(--ink)}"
assert s.count(old)==1
new=("/* 부스 칸 = 별(도장 칸과 같은 모양). 빈 칸: 연한 별 테두리(::before 가 안쪽을 카드색으로 덮음) · 받은 부스: 노란 별 · 이 부스: 진한 테두리 */\n"
     ".bprog{display:flex;gap:5px;margin-top:7px;flex-wrap:wrap}.bprog span{width:30px;height:30px;clip-path:var(--star);background:var(--line);position:relative;isolation:isolate;display:grid;place-items:center;font-size:11px;font-weight:800;color:var(--ink-3);padding-top:3px}"
     ".bprog span::before{content:\"\";position:absolute;inset:0;background:var(--card);clip-path:var(--star);transform:scale(.78);transform-origin:50% 55%;z-index:-1}"
     ".bprog span.on{background:var(--sun);color:var(--ink)}.bprog span.on::before{display:none}.bprog span.me{background:var(--ink)}.bprog span.me.on{background:var(--sun)}.bprog span.me.on::before{display:block;background:var(--ink);transform:scale(.9)}.bprog span.me.on{color:#fff}")
s=s.replace(old,new,1)
s=s.replace(".bprog.big span{width:34px;height:34px;font-size:13px}",".bprog.big span{width:40px;height:40px;font-size:13px;padding-top:4px}")
io.open(p,'w',encoding='utf-8',newline='\n').write(s); print('ok')

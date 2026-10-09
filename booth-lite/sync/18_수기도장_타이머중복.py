# 18단계: 수기 도장 화면 목록 자동 갱신 정리. 17단계 뒤에 실행
#   ① 도장 찍을 때마다 갱신 타이머가 하나씩 쌓이던 버그: 예전 조건 $('#mRecent') 가 다음 찾기 화면의 새 #mRecent 에도 참 → 자기 상자(rbox.isConnected) 기준으로
#   ② 찾기 화면이 열리면 입력칸 자동 포커스 → focus 에서 타이머를 꺼서 정작 지금 화면은 갱신이 안 됐음 → focus 끄기 삭제, 대신 검색어가 있을 때(목록 숨김)만 건너뜀
#   ③ 간격 20초 → 60초: 갱신마다 방문객·도장 전체를 받으므로 태블릿 7대 × 하루 데이터량을 줄임. 도장 찍은 직후엔 어차피 새로 받음
import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
NEW="recent(); const rbox = $('#mRecent'), rt = setInterval(() => { if(!rbox.isConnected) return clearInterval(rt); if(!inp.value.trim() && !document.hidden) recent(); }, 60000);   // 자기 상자 기준(새 찾기 화면의 #mRecent 로 착각하면 타이머가 쌓임). 검색 중·화면 꺼짐이면 건너뜀"
if NEW in s: print('already patched'); raise SystemExit
olds=["recent(); const rt = setInterval(() => { if($('#mRecent')) recent(); else clearInterval(rt); }, 20000);",
      "recent(); const rbox = $('#mRecent'), rt = setInterval(() => { if(rbox.isConnected) recent(); else clearInterval(rt); }, 20000);   // 자기 상자 기준(새 찾기 화면의 #mRecent 로 착각하면 타이머가 쌓임)"]
hit=[o for o in olds if s.count(o)==1]; assert len(hit)==1, [s.count(o) for o in olds]
s=s.replace(hit[0],NEW)
f="    inp.addEventListener('focus', () => { clearInterval(rt); });   // 자판이 올라오면 갱신으로 목록이 흔들리지 않게\n"
assert s.count(f)==1, s.count(f); s=s.replace(f,'')
s=s.replace("20명 넘으면 [더 보기].\n       방문객·도장 전체를 한 번에 받아(관리자 RPC, 1000행씩) 아이별 부스 칸을 바로 채우므로 아이마다 서버를 안 부른다. 20초마다 갱신, 이 화면을 벗어나면 멈춤",
            "20명 넘으면 [더 보기].\n       방문객·도장 전체를 한 번에 받아(관리자 RPC, 1000행씩) 아이별 부스 칸을 바로 채우므로 아이마다 서버를 안 부른다. 60초마다 갱신, 이 화면을 벗어나면 멈춤")
io.open(p,'w',encoding='utf-8',newline='\n').write(s); print('ok')

# 15단계: 스캐너를 닫아도 카메라 스트림을 잠시(기본 3분) 들고 있다가 다음 스캔에 재사용 → 같은 페이지 안에서 권한 창이 한 번만 뜬다.
#   탭이 숨겨지거나 3분 동안 안 쓰면 그때 끈다. 14단계 뒤에 실행
import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    n=s.count(old); assert n==count,(n,old[:80]); s=s.replace(old,new)

rep("  giftText: '',                          // 안내 화면 '선물 교환' 카드 본문. 비우면 기본 문장 (관리자 › 행사 설정)\n",
    "  giftText: '',                          // 안내 화면 '선물 교환' 카드 본문. 비우면 기본 문장 (관리자 › 행사 설정)\n"
    "  cameraKeepMs: 180000,                  // 스캐너를 닫은 뒤 카메라를 들고 있는 시간(ms). 그 안에 다시 열면 권한 창 없이 바로 켜짐. 0 이면 바로 끔\n")

# 열 때: 살아 있는 스트림이 있으면 재사용
rep("    scanner.stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' }, width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false });\n",
    "    clearTimeout(scanner.idle);\n"
    "    const alive = scanner.stream && scanner.stream.getVideoTracks().some(t => t.readyState === 'live');   // 닫은 지 얼마 안 됐으면 그대로 재사용(권한 창 없음)\n"
    "    if(!alive) scanner.stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' }, width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false });\n")

# 닫을 때: 바로 끄지 않고 타이머로. 탭이 숨겨지면 즉시 끔
rep("  if(scanner.stream){ scanner.stream.getTracks().forEach(t => t.stop()); scanner.stream = null; }\n  const v = $('#scanVideo'); if(v) v.srcObject = null;\n",
    "  clearTimeout(scanner.idle);\n"
    "  if(scanner.stream){ if(CONFIG.cameraKeepMs > 0) scanner.idle = setTimeout(stopCamera, CONFIG.cameraKeepMs); else stopCamera(); }\n"
    "  const v = $('#scanVideo'); if(v) v.srcObject = null;\n")
rep("function closeScanner(){\n",
    "/* 카메라 끄기. 스캐너를 닫은 뒤 cameraKeepMs 가 지나거나 탭이 숨겨지면 호출 */\n"
    "function stopCamera(){ clearTimeout(scanner.idle); if(scanner.stream){ scanner.stream.getTracks().forEach(t => t.stop()); scanner.stream = null; } }\n"
    "document.addEventListener('visibilitychange', () => { if(document.hidden && !scanner.on) stopCamera(); });\n"
    "function closeScanner(){\n")
io.open(p,'w',encoding='utf-8',newline='\n').write(s); print('ok')

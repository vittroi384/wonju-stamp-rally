import re,io,sys
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    assert old in s, old[:80]
    s=s.replace(old,new,count)
rep("<title>2026 원주 수학과학축전 · 부스 스탬프</title>","<title>booth-lite · 스탬프</title>")
rep("  eventTitle: '2026 원주 수학과학축전',","  eventTitle: 'booth-lite',\n  miniMode: true,                        // ★미니 모드★ 지도 없음(탭·버튼·관리자 지도 탭 숨김). 관리자가 부스 QR 을 찍으면 수기 도장 화면으로")
rep("  eventDate: '2026. 10. 10. (토) 10:00–16:00',","  eventDate: '날짜 미정',                 // 관리자 › 행사 설정에서 바꿈")
rep("  venue: '원주종합운동장',","  venue: '',")
rep("  stampGoal: 7,                          // 완주 기준. 2026-09-09 주최측 요청으로 5→7","  stampGoal: 7,                          // 완주 기준(부스 7개). 관리자 › 행사 설정에서 바꿈")
rep("  supabaseUrl: 'https://YOUR-PROJECT.supabase.co',","  supabaseUrl: '',                       // ★booth-lite 전용 Supabase 프로젝트 주소(축전 서버와 별개). 비우면 로컬 모드")
rep("  supabaseAnonKey: 'YOUR_SUPABASE_ANON_KEY',","  supabaseAnonKey: '',")
# seed booths 1~7
s=re.sub(r"const SEED_BOOTHS = \[.*?\];", "const SEED_BOOTHS = " + str([{"n":str(i),"name":f"booth-lite {i}","cat":"exp","org":""} for i in range(1,8)]).replace("'",'"') + ";", s, count=1, flags=re.S)
# CATS
old=s[s.index("const CATS = ["):s.index("CATS.forEach(c => c.def = c.color);")]
rep(old,"""const CATS = [                                                  // 분류. color 는 관리자 › 부스 › [분류 색] 에서 바꿀 수 있음(settings.categoryColors), def = 기본색. 없는 이름을 적으면 새 분류가 생김
  {id:'exp',   name:'체험',       color:'#1FA97A'},
  {id:'ops',   name:'운영·편의',   color:'#151A2D'},
];
""")
old=s[s.index("const DESC_BY_CAT = {"):s.index("};",s.index("const DESC_BY_CAT = {"))+2]
rep(old,"""const DESC_BY_CAT = {
  exp:'직접 해 보고 도장을 받는 체험 부스입니다.',
  ops:'행사 운영을 돕는 안내·편의 부스입니다.',
};""")
# visitor tabs
rep("  const tabs = [['/', '홈', I.home], ['/map', '지도', I.map], ['/my', '내 스탬프', I.stamp], ['/info', '안내', I.info]];",
    "  const tabs = [['/', '홈', I.home], ['/map', '지도', I.map], ['/my', '내 스탬프', I.stamp], ['/info', '안내', I.info]].filter(t => !(CONFIG.miniMode && t[0] === '/map'));   // 미니 모드: 지도 탭 없음")
rep("  if(a === 'map') return renderMap(b);","  if(a === 'map') return CONFIG.miniMode ? renderHome() : renderMap(b);   // 미니 모드: 지도 없음")
rep("  if(a === CONFIG.adminPath) return renderAdmin(b || 'dash');","  if(a === CONFIG.adminPath) return renderAdmin(b || 'dash', c);   // c = 수기 도장 탭의 부스 번호")
rep("""    <div class="h-sec">부스 둘러보기 <button class="more" onclick="go('/map')">지도에서 보기 ›</button></div>""",
    """    <div class="h-sec">부스 둘러보기 ${CONFIG.miniMode ? '' : `<button class="more" onclick="go('/map')">지도에서 보기 ›</button>`}</div>""")
rep("""      <div class="k" style="margin-top:4px">위치</div><div class="v" style="font-size:14px">${esc(zoneOf(b.zone).name)} <button class="more" style="border:0;background:none;color:var(--blue);font-weight:800;font-size:13px;padding:0 4px" onclick="go('/map/${b.n}')">지도 ›</button></div>""",
    """      ${CONFIG.miniMode ? '' : `<div class="k" style="margin-top:4px">위치</div><div class="v" style="font-size:14px">${esc(zoneOf(b.zone).name)} <button class="more" style="border:0;background:none;color:var(--blue);font-weight:800;font-size:13px;padding:0 4px" onclick="go('/map/${b.n}')">지도 ›</button></div>`}""")
rep("""    <button class="btn ${st ? '' : 'line'} full" onclick="go('/map/${b.n}')">${I.pin} 지도에서 위치 보기</button>""",
    """    ${CONFIG.miniMode ? '' : `<button class="btn ${st ? '' : 'line'} full" onclick="go('/map/${b.n}')">${I.pin} 지도에서 위치 보기</button>`}""")
# renderStamp: admin → manual
rep("""function renderStamp(n){
  const b = boothByN(n); if(!b) return go('/', true);
  if(!S.me){""","""function renderStamp(n){
  const b = boothByN(n); if(!b) return go('/', true);
  if(CONFIG.miniMode && S.admin){ go(admPath('/manual/' + encodeURIComponent(b.n)), true); return; }   // 관리자 폰으로 부스 QR 을 찍으면 → 수기 도장
  if(!S.me){""")
# admin tabs
rep("const ADM_TABS = [['dash', '현황'], ['gift', '선물 수령'], ['booths', '부스'], ['map', '지도'], ['qr', 'QR 시트'], ['event', '행사 설정'], ['survey', '설문'], ['data', '데이터']];",
    "const ADM_TABS = [['dash', '현황'], ['manual', '수기 도장'], ['gift', '선물 수령'], ['booths', '부스'], ['map', '지도'], ['qr', 'QR 시트'], ['event', '행사 설정'], ['survey', '설문'], ['data', '데이터']]\n  .filter(([k]) => CONFIG.miniMode ? k !== 'map' : k !== 'manual');   // 미니 모드: 지도 탭 대신 수기 도장 탭")
rep("async function renderAdmin(tab){","async function renderAdmin(tab, arg){")
rep("  if(tab === 'booths') return admBooths();\n  if(tab === 'map') return admMap();","  if(tab === 'booths') return admBooths();\n  if(tab === 'manual') return admManual(arg);\n  if(tab === 'map') return admMap();")
io.open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

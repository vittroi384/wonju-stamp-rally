# 8단계: 수기 도장 › 부스 고르기 화면을 타일 격자로. 7단계 뒤에 실행
import io
p=r'C:\dev\booth-lite\booth-lite_스탬프앱.html'
s=io.open(p,encoding='utf-8').read()
def rep(old,new):
    global s
    assert s.count(old)==1, (s.count(old), old[:100])
    s=s.replace(old,new,1)

rep(".tb-form{display:grid;grid-template-columns:1fr 1fr;gap:12px 14px}",
"""/* 부스 고르기 타일 */
.tb-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;margin-top:14px}
.tb-tile{position:relative;border:0;background:var(--card);border-radius:20px;padding:16px 16px 14px;text-align:left;box-shadow:var(--sh-1);display:flex;flex-direction:column;gap:8px;min-height:128px;overflow:hidden;color:var(--ink);transition:transform .12s}
.tb-tile::before{content:"";position:absolute;left:0;top:0;right:0;height:6px;background:var(--c)}
.tb-tile .num{width:46px;height:46px;border-radius:14px;background:var(--c);color:#fff;font-weight:900;font-size:21px;display:grid;place-items:center;margin-top:4px}
.tb-tile .nm{font-size:16px;font-weight:800;line-height:1.3;word-break:keep-all}.tb-tile .org{font-size:12.5px;color:var(--ink-3);margin-top:auto}
.tb-tile:active{transform:scale(.96)}
.tb-qr{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;border:2px dashed var(--blue);background:var(--blue-soft,#EEF2FF);color:var(--blue);border-radius:20px;padding:18px;font-size:16px;font-weight:800;margin-top:4px}
.tb-qr svg{width:22px;height:22px}
.tb-form{display:grid;grid-template-columns:1fr 1fr;gap:12px 14px}""")

old_start = s.index("    admShell('manual', `\n      <div class=\"card\" style=\"display:flex;flex-direction:column;gap:14px\">\n        <div><div class=\"tb-q\" style=\"margin:0\">이 태블릿은 어느 부스인가요?</div>")
old_end = s.index("    $('#mScan').onclick = pickScan;", old_start)
s = s[:old_start] + """    admShell('manual', `
      <div class="card" style="padding-bottom:18px">
        <div class="tb-q" style="margin:0">이 태블릿은 어느 부스인가요?</div>
        <p class="small muted" style="margin-top:4px;line-height:1.6">폰이 없는 어린이는 부스에서 이 태블릿으로 도장을 찍어요. 한 번 고르면 이 탭에 고정돼요.</p>
        <button class="tb-qr" id="mScan">${I.qr} 부스 QR 찍어서 고르기</button>
        <div class="tb-grid">${booths.map(b => { const c = catOf(b.cat); return `<button class="tb-tile" data-pick="${esc(b.n)}" style="--c:${c.color}"><span class="num">${esc(b.n)}</span><span class="nm">${esc(b.name)}</span><span class="org">${esc(b.org || c.name)}</span></button>`; }).join('')}</div>
      </div>`);
""" + s[old_end:]
io.open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

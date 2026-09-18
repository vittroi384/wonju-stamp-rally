// 실서버: 앱 내 설문 제출(visitor_survey_submit) + 관리자 설문 결과 + 대시보드 풀 모드
import { chromium } from 'playwright';
const DIR='C:/dev/stamp-rally-v3/', APP='file:///'+DIR+'원주축전_스탬프앱_3.html', DASH='file:///'+DIR+'운영대시보드.html';
const U='https://YOUR-PROJECT.supabase.co', K='YOUR_SUPABASE_ANON_KEY';
const PW = process.env.ADMIN_PW; if(!PW){ console.error('ADMIN_PW 환경변수에 관리자 비번 넣고 실행:  $env:ADMIN_PW="비번"; node tests/파일.mjs'); process.exit(1); }
const H={apikey:K,Authorization:`Bearer ${K}`,'Content-Type':'application/json'};
const rpc=async(fn,b)=>{const r=await fetch(`${U}/rest/v1/rpc/${fn}`,{method:'POST',headers:H,body:JSON.stringify(b)});const t=await r.text();return {ok:r.ok,body:t?JSON.parse(t):null};};
const fails=[],errs=[]; const check=(n,ok,x='')=>{console.log((ok?'  ✓ ':'  ✗ ')+n+(x?' — '+x:'')); if(!ok) fails.push(n);};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
await rpc('admin_reset',{pw:PW});
// RPC 직접: 완주 전 제출 → NOT_DONE
const v=await rpc('visitor_create',{nm:'테스터',school:'원주중',grade:'중2',gender:'남'}); const vid=v.body[0].id;
let r=await rpc('visitor_survey_submit',{vid,ans:{overall:5}}); check('완주 전 제출 거부(NOT_DONE)', !r.ok && /NOT_DONE/.test(JSON.stringify(r.body)));
for(const b of ['b1','b2','b3','b4','b5','b6','b7']) await rpc('admin_add_stamp',{pw:PW,vid,bid:b});   // 앱 도장은 90초 간격 때문에 전부 수동 도장
const b=await chromium.launch({channel:'chrome'}); const ctx=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true});
const p=await ctx.newPage(); p.on('pageerror',e=>errs.push(e.message));
await p.goto(APP); await p.waitForFunction(()=>S.booths.length>0&&document.querySelector('#main'));
await p.evaluate(async id=>{ await store.set('wj:me',id); },vid); await p.reload(); await p.waitForFunction(()=>S.me&&S.myStamps.length===7&&document.querySelector('#main'));
await p.evaluate(()=>location.hash='#/my'); await sleep(400);
check('앱 내 설문 모드', await p.evaluate(()=>surveyMode()==='app'));
await p.evaluate(()=>location.hash='#/survey'); await p.waitForSelector('#svSubmit');
await p.evaluate(()=>{ $$('.sv-q')[0].querySelector('.sv-scale button[data-v="4"]').click(); $$('.sv-chip')[1].click(); const e=$$('.sv-q')[2]; e.querySelectorAll('.sv-opt')[1].click(); $$('.sv-q')[3].querySelectorAll('.sv-opt')[1].click(); $$('.sv-q')[4].querySelectorAll('.sv-opt')[0].click(); $$('.sv-q')[5].querySelectorAll('.sv-opt')[0].click(); });
await p.fill('.sv-q textarea','실서버 테스트 응답');
await p.click('#svSubmit'); await p.waitForSelector('#myQr',{timeout:10000}); check('실서버 제출 → 교환권', true);
const vg=await rpc('visitor_get',{vid}); check('survey_done_at 기록', !!vg.body[0].survey_done_at);
r=await rpc('visitor_survey_submit',{vid,ans:{overall:1}}); check('재제출은 처음 것 유지', r.ok);
const ans=await rpc('admin_survey_answers',{pw:PW,off:0,lim:10}); check('admin_survey_answers 1건·overall=4', ans.body.length===1&&ans.body[0].answers.overall===4&&!('name' in ans.body[0]), JSON.stringify(ans.body[0]?.answers));
// 관리자 설문 탭 결과
const a=await ctx.newPage(); a.on('pageerror',e=>errs.push('admin '+e.message)); await a.setViewportSize({width:1280,height:900});
await a.goto(APP); await a.waitForFunction(()=>S.booths.length>0&&document.querySelector('#main'));
await a.evaluate(()=>location.hash='#/admin'); await a.waitForSelector('#pw'); await a.fill('#pw',PW); await a.keyboard.press('Enter'); await a.waitForFunction(()=>S.admin); await a.waitForSelector('.stats');
await a.evaluate(()=>location.hash='#/admin/survey'); await a.waitForSelector('#sqLoad'); await a.click('#sqLoad'); await a.waitForFunction(()=>/응답 <b>1<\/b>명/.test($('#sqRes').innerHTML),null,{timeout:20000});
check('관리자 설문 결과 렌더', await a.evaluate(()=>/평균/.test($('#sqRes').textContent)&&/실서버 테스트 응답/.test($('#sqRes').textContent)));
// 대시보드 풀 모드
const d=await b.newPage({viewport:{width:1600,height:1000}}); d.on('pageerror',e=>errs.push('dash '+e.message));
await d.goto(DASH); await d.waitForSelector('#pw'); await d.fill('#pw',PW); await d.click('#pwGo');
await d.waitForFunction(()=>!$('#dash').hidden&&$('#kpis').children.length>0,null,{timeout:20000}); await sleep(800);
check('admin_dashboard 풀 모드', await d.evaluate(()=>D.basic===false&&$('#banner').hidden));
const dd=await d.evaluate(()=>D.data);
check('집계 값', dd.visitors===1&&dd.stamps===7&&dd.achievers===1&&dd.survey_done===1&&dd.per_10min.length>0&&dd.dist.length===1&&dd.recent.length===7&&dd.by_grade[0].g==='중2', JSON.stringify({v:dd.visitors,s:dd.stamps,a:dd.achievers,sd:dd.survey_done,t:dd.per_10min.length,d:dd.dist,r:dd.recent.length,g:dd.by_grade,sv:dd.survey}));
check('설문 척도 평균 4.00', dd.survey?.n===1&&dd.survey.scales[0].avg==4);
check('패널 채워짐', await d.evaluate(()=>/4\.00/.test($('#survey').textContent)&&$('#funnel .f')!=null&&$('#recent .tk')!=null&&/중학생/.test($('#grade').textContent)&&/원주중/.test($('#schools').textContent)));
await d.screenshot({path:'out/a7_대시보드_풀모드.png',fullPage:true});
await b.close(); await rpc('admin_reset',{pw:PW});
console.log('ERRORS',errs.length?errs:'none'); console.log('FAILS',fails.length?fails:'none'); process.exit(fails.length||errs.length?1:0);

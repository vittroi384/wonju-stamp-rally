// ※ 2026-09-14 버전. 당시엔 REST 직접 insert 가 열려 있었음 — 지금 스키마(RPC 전용)에선 그대로 안 돌아감. 결과 기록용. 최신 부하 시나리오는 soak.mjs
// 점진적 부하 테스트: 단계별 동접 N명이 동시에 등록→도장7→조회 수행
import { writeFileSync } from 'node:fs';
const U='https://YOUR-PROJECT.supabase.co', K='YOUR_SUPABASE_ANON_KEY';
const H={apikey:K,Authorization:`Bearer ${K}`,'Content-Type':'application/json',Prefer:'return=representation'};
const STAGES=(process.argv[2]||'50,100,200,400,800,1200,2000').split(',').map(Number);
const BOOTHS=Array.from({length:90},(_,i)=>'b'+(i+1));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));

async function req(kind,path,opt={},samples,timeout=30000){
  const t0=performance.now(); const ac=new AbortController(); const tm=setTimeout(()=>ac.abort(),timeout);
  try{
    const r=await fetch(`${U}/rest/v1/${path}`,{...opt,headers:{...H,...(opt.headers||{})},signal:ac.signal});
    const txt=await r.text(); const ms=performance.now()-t0;
    samples.push({kind,ms,status:r.status});
    return {ok:r.ok||r.status===409,status:r.status,body:txt};
  }catch(e){ const ms=performance.now()-t0; samples.push({kind,ms,status:0,err:e.name}); return {ok:false,status:0,body:e.name}; }
  finally{ clearTimeout(tm); }
}

async function visitor(i,samples){
  // 실제 사람처럼 0~3초 사이에 흩어져 시작
  await sleep(Math.random()*3000);
  const v=await req('register','visitors',{method:'POST',body:JSON.stringify({name:'부하'+i,school:'테스트초',grade:'초3',gender:i%2?'남':'여',consented_at:new Date().toISOString()})},samples);
  if(!v.ok) return;
  let vid; try{ vid=JSON.parse(v.body)[0].id; }catch(e){ return; }
  const picked=new Set(); while(picked.size<7) picked.add(BOOTHS[Math.floor(Math.random()*BOOTHS.length)]);
  for(const b of picked){
    await req('stamp','stamps',{method:'POST',body:JSON.stringify({visitor_id:vid,booth_id:b})},samples);
    await sleep(Math.random()*200);
  }
  await req('mystamps',`stamps?visitor_id=eq.${vid}&order=created_at`,{},samples);
}
async function dashboard(samples){
  const t0=performance.now();
  await Promise.all([
    req('dash','booth_stats?select=*',{},samples), req('dash','hourly_stats?select=*',{},samples),
    req('dash','visitor_stats?n=gte.7&select=*&order=created_at.desc',{headers:{Range:'0-999','Range-Unit':'items'}},samples),
    req('dash','visitors?select=id',{headers:{Prefer:'count=exact',Range:'0-0'}},samples),
    req('dash','visitor_stats?n=gte.1&select=id',{headers:{Prefer:'count=exact',Range:'0-0'}},samples),
    req('dash','stamps?select=id',{headers:{Prefer:'count=exact',Range:'0-0'}},samples),
  ]);
  return performance.now()-t0;
}
const pct=(a,p)=>{ if(!a.length) return 0; const s=[...a].sort((x,y)=>x-y); return s[Math.min(s.length-1,Math.floor(p*s.length))]; };

const results=[];
for(const n of STAGES){
  const samples=[]; const t0=performance.now();
  const dashTimes=[]; let running=true;
  const poller=(async()=>{ while(running){ dashTimes.push(await dashboard(samples)); await sleep(2000); } })();   // 운영본부 화면이 2초마다 새로고침하는 상황
  await Promise.all(Array.from({length:n},(_,i)=>visitor(i,samples)));
  running=false; await poller;
  const dur=(performance.now()-t0)/1000;
  const byKind={};
  for(const k of ['register','stamp','mystamps','dash']){
    const s=samples.filter(x=>x.kind===k); const ok=s.filter(x=>x.status>=200&&x.status<300||x.status===409);
    const lat=ok.map(x=>x.ms);
    byKind[k]={n:s.length,err:s.length-ok.length,p50:pct(lat,.5),p95:pct(lat,.95),max:Math.max(0,...lat)};
  }
  const all=samples.filter(x=>x.kind!=='dash'); const errs=all.filter(x=>!(x.status>=200&&x.status<300||x.status===409));
  const errCodes={}; errs.forEach(e=>{ const k=e.status||e.err; errCodes[k]=(errCodes[k]||0)+1; });
  const r={users:n,requests:all.length,errors:errs.length,errRate:+(100*errs.length/all.length).toFixed(2),errCodes,durationSec:+dur.toFixed(1),rps:+(all.length/dur).toFixed(1),
    p50:+pct(all.filter(x=>!errs.includes(x)).map(x=>x.ms),.5).toFixed(0),p95:+pct(all.filter(x=>!errs.includes(x)).map(x=>x.ms),.95).toFixed(0),max:+Math.max(...all.map(x=>x.ms)).toFixed(0),
    dashP50:+pct(dashTimes,.5).toFixed(0),dashMax:+Math.max(0,...dashTimes).toFixed(0),byKind};
  results.push(r);
  console.log(JSON.stringify({users:r.users,req:r.requests,err:r.errors,errRate:r.errRate,errCodes:r.errCodes,sec:r.durationSec,rps:r.rps,p50:r.p50,p95:r.p95,max:r.max,dashP50:r.dashP50,dashMax:r.dashMax}));
  writeFileSync('load_results.json',JSON.stringify(results,null,1));
  if(r.errRate>50){ console.log('에러율 50% 초과 → 중단'); break; }
  await sleep(5000);   // 단계 사이 숨 고르기
}

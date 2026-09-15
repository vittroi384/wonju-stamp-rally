-- =====================================================================
-- 2026 원주 수학과학축전 스탬프앱 · Supabase 설정 SQL
-- 대시보드 › SQL Editor 에 통째로 붙여넣고 Run. 다시 실행해도 됨.
-- ---------------------------------------------------------------------
-- 권한 모델 (anon 키 하나만 씀, Auth 없음)
--   anon : booths·settings select 만. 방문객 데이터는 RPC 로만 — visitor_create·visitor_get·visitor_stamps·visitor_recover(uuid 본인 확인)·add_stamp(토큰·간격 검사)
--          + visitor_survey_done(vid) RPC 로 설문 완료 시각만 1회 기록
--   관리자: 비밀번호를 받는 RPC 로만 쓰기 — admin_reset / admin_set_gift / admin_save_booths
--          비번 검사 admin_login, 비번 변경 admin_set_password. 비번은 해시로 admin_secret 에 저장.
--   초기 비밀번호: 1234  → 관리자 화면 › 데이터 에서 바로 바꿀 것
-- =====================================================================

create extension if not exists pgcrypto;

-- 1. 테이블 -----------------------------------------------------------
create table if not exists booths (
  id text primary key,            -- 'b' + 번호 (예: b7, b본1). 도장 기록(stamps.booth_id)이 이 id 를 가리킴
  number text,                    -- 부스 번호. 숫자든 '본1'·'네2' 같은 문자든 됨. QR 주소의 b= 값
  name text,                      -- 부스명
  category text,                  -- 분류 코드: sci 원리의정원 · craft 대담한갤러리 · play 한바탕놀이터 · app 상상공작소 · etc 상상그이상 · ops 운영·편의
  organization text,              -- 운영기관(학교·단체)
  description text,               -- 소개 글
  sort_order int,                 -- 표·지도 순서 (같은 구역 안에서)
  zone text default '',           -- 지도 구역: '' 트랙 둘레 · hq 운영본부 · photo 인생네컷 · goalL 왼쪽 골대 뒤 · goalR 오른쪽 골대 뒤
  video_url text default '',      -- 유튜브 링크
  pdf_url text default '',        -- 자료 PDF (Storage 공개 URL 또는 외부 링크)
  image_url text default ''       -- 대표 사진
);
-- 2026-09-14 컬럼명 풀어쓰기 (n·cat·org·desc·ord·video·pdf·img → number·category·organization·description·sort_order·video_url·pdf_url·image_url). 옛 이름이 남아 있으면 바꿈
do $$ begin
  if exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'booths' and column_name = 'n') then
    alter table booths rename column n to number;
    alter table booths rename column cat to category;
    alter table booths rename column org to organization;
    alter table booths rename column "desc" to description;
    alter table booths rename column ord to sort_order;
    alter table booths rename column video to video_url;
    alter table booths rename column pdf to pdf_url;
    alter table booths rename column img to image_url;
  end if;
end $$;
create table if not exists visitors (
  id uuid primary key default gen_random_uuid(), name text not null, school text,
  grade text default '', gender text default '',                  -- 학년 '초3'·'중1'·'성인' / 성별 '남'·'여'
  consented_at timestamptz not null, survey_done_at timestamptz,  -- 설문 완료(자기신고) 시각
  gift_received_at timestamptz, created_at timestamptz default now()
);
-- 이미 만든 테이블에 열 추가 (2026-09-09: 학년·성별·설문)
alter table visitors add column if not exists grade text default '';
alter table visitors add column if not exists gender text default '';
alter table visitors add column if not exists survey_done_at timestamptz;
create table if not exists stamps (
  id bigserial primary key, visitor_id uuid references visitors(id) on delete cascade,
  booth_id text, created_at timestamptz default now(), unique (visitor_id, booth_id)
);
create table if not exists admin_secret (id int primary key default 1 check (id = 1), pw_hash text not null);
insert into admin_secret (id, pw_hash) values (1, crypt('1234', gen_salt('bf'))) on conflict (id) do nothing;

create index if not exists stamps_visitor_idx on stamps(visitor_id);
create index if not exists stamps_booth_idx   on stamps(booth_id);
create index if not exists stamps_created_idx on stamps(created_at);

-- 2. 집계 뷰 (대시보드는 이것만 읽음) -----------------------------------
create or replace view booth_stats as
  select booth_id, count(*)::int as n, max(created_at) as last_at from stamps group by booth_id;
create or replace view hourly_stats as
  select extract(hour from created_at at time zone 'Asia/Seoul')::int as h, count(*)::int as n from stamps group by 1;
drop view if exists visitor_stats;   -- 열이 늘어서 재생성
create view visitor_stats as
  select v.id, v.name, v.school, v.grade, v.gender, v.created_at, v.survey_done_at, v.gift_received_at, count(s.id)::int as n
  from visitors v left join stamps s on s.visitor_id = v.id group by v.id;

-- 3. RLS ---------------------------------------------------------------
alter table booths       enable row level security;
alter table visitors     enable row level security;
alter table stamps       enable row level security;
alter table admin_secret enable row level security;   -- 정책 없음 = API 로는 아무도 못 봄

drop policy if exists booths_select   on booths;
drop policy if exists visitors_insert on visitors;
drop policy if exists visitors_select on visitors;
drop policy if exists stamps_insert   on stamps;
drop policy if exists stamps_select   on stamps;
create policy booths_select   on booths   for select to anon using (true);




-- 3-1. 방문객 RPC: 설문 완료 표시 (anon 호출. 자기 id 만 알면 되고, 최초 1회만 기록·되돌리기 불가) ----
create or replace function visitor_survey_done(vid uuid) returns void
language sql security definer set search_path = public, extensions as $$
  update visitors set survey_done_at = now() where id = vid and survey_done_at is null;
$$;
grant execute on function visitor_survey_done(uuid) to anon;

-- 4. 관리자 RPC ---------------------------------------------------------
-- 내부용: 비번 틀리면 예외. 틀릴 때 0.5초 지연(무차별 대입 완화)
create or replace function admin_ok(pw text) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  if not exists (select 1 from admin_secret where pw_hash = crypt(pw, pw_hash)) then
    perform pg_sleep(0.5);
    raise exception 'ADMIN_UNAUTHORIZED';
  end if;
end $$;
revoke all on function admin_ok(text) from public, anon;

-- 로그인 검사
create or replace function admin_login(pw text) returns boolean
language plpgsql security definer set search_path = public, extensions as $$
begin perform admin_ok(pw); return true; end $$;

-- 비번 변경
create or replace function admin_set_password(pw text, new_pw text) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform admin_ok(pw);
  if length(new_pw) < 8 then raise exception 'PASSWORD_TOO_SHORT'; end if;   -- #/admin 은 추측 가능한 주소라 비번이 방어선
  update admin_secret set pw_hash = crypt(new_pw, gen_salt('bf')) where id = 1;
end $$;

-- ① 초기화: 방문객·스탬프 전부 삭제 (부스는 유지)
create or replace function admin_reset(pw text) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin perform admin_ok(pw); delete from stamps where true; delete from visitors where true; end $$;

-- ② 선물 지급/취소
create or replace function admin_set_gift(pw text, vid uuid, given boolean) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform admin_ok(pw);
  update visitors set gift_received_at = case when given then now() else null end where id = vid;
end $$;

-- ③ 부스 저장: 통째로 교체. rows = [{id,number,name,category,organization,description,sort_order,zone,video_url,pdf_url,image_url}, ...]
create or replace function admin_save_booths(pw text, rows jsonb) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform admin_ok(pw);
  delete from booths where true;   -- Supabase 는 WHERE 없는 DELETE 를 막음(safeupdate)
  insert into booths (id, number, name, category, organization, description, sort_order, zone, video_url, pdf_url, image_url)
  select r.id, r.number, r.name, r.category, r.organization, r.description, r.sort_order,
         coalesce(r.zone, ''), coalesce(r.video_url, ''), coalesce(r.pdf_url, ''), coalesce(r.image_url, '')
  from jsonb_to_recordset(rows) as r(id text, number text, name text, category text, organization text, description text, sort_order int,
                                     zone text, video_url text, pdf_url text, image_url text);
  perform ensure_booth_tokens();   -- 새 부스엔 QR 토큰 발급 (기존 토큰은 유지)
end $$;

grant execute on function admin_login(text), admin_set_password(text, text), admin_reset(text),
  admin_set_gift(text, uuid, boolean), admin_save_booths(text, jsonb) to anon;

-- 5. Storage (부스 PDF·사진). 업로드도 anon 으로 하므로 버킷에 anon 쓰기 허용 -----
insert into storage.buckets (id, name, public, file_size_limit)
values ('booth-files', 'booth-files', true, 20971520)
on conflict (id) do update set public = true, file_size_limit = 20971520;
drop policy if exists booth_files_read  on storage.objects;
drop policy if exists booth_files_write on storage.objects;
create policy booth_files_read  on storage.objects for select to anon using (bucket_id = 'booth-files');
create policy booth_files_write on storage.objects for insert to anon with check (bucket_id = 'booth-files');

-- 6. 치팅 방지 (2026-09-14) ---------------------------------------------
-- 문제: QR 이 ?b=7 뿐이면 주소창에 1~90 쳐서 1분 만에 완주 가능.
-- ① 부스 토큰: QR 주소가 ?b=7&t=xxxxxxxxxx. 토큰은 booth_tokens 에 있고 anon 은 못 읽음(정책 없음). add_stamp 가 검사.
--    토큰은 부스 저장 때 자동 발급, 한 번 발급된 건 안 바뀜(인쇄한 QR 유지). 관리자 › QR 시트가 admin_booth_tokens 로 받아 QR 에 넣음.
-- ② 시간 간격: 같은 사람의 도장 사이 최소 stamp_gap_sec() 초. 링크를 받아도 7개 찍는 데 10분 넘게 걸려 치팅 이득이 없음.
-- 도장은 이제 add_stamp RPC 로만 들어감. anon 의 stamps 직접 insert 는 막음.
create table if not exists booth_tokens (booth_id text primary key, token text not null);
alter table booth_tokens enable row level security;    -- 정책 없음 = API 로 못 읽음
drop policy if exists stamps_insert on stamps;          -- 직접 insert 차단

create or replace function stamp_gap_sec() returns int language sql immutable as $$ select 90 $$;   -- ★ 간격(초). 바꾸려면 숫자만 고치고 이 파일 다시 실행

create or replace function ensure_booth_tokens() returns void
language sql security definer set search_path = public, extensions as $$
  insert into booth_tokens (booth_id, token)
  select b.id, encode(gen_random_bytes(5), 'hex') from booths b
  left join booth_tokens t on t.booth_id = b.id where t.booth_id is null;
$$;
revoke all on function ensure_booth_tokens() from public, anon;

-- 관리자: QR 시트용 토큰 목록
create or replace function admin_booth_tokens(pw text) returns table(booth_id text, token text)
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform admin_ok(pw); perform ensure_booth_tokens();
  return query select t.booth_id, t.token from booth_tokens t;
end $$;
grant execute on function admin_booth_tokens(text) to anon;

-- 방문객: 도장 찍기. 반환 {ok,stamp} | {dup}. 예외 BAD_TOKEN / TOO_FAST:남은초
create or replace function add_stamp(vid uuid, bid text, tok text) returns jsonb
language plpgsql security definer set search_path = public, extensions as $$
declare last_at timestamptz; gap int := stamp_gap_sec(); wait int; row_json jsonb;
begin
  if exists (select 1 from stamps where visitor_id = vid and booth_id = bid) then return jsonb_build_object('dup', true); end if;
  if not exists (select 1 from booth_tokens where booth_id = bid and token = tok) then
    perform pg_sleep(0.3); raise exception 'BAD_TOKEN';
  end if;
  select max(created_at) into last_at from stamps where visitor_id = vid;
  if last_at is not null and last_at > now() - make_interval(secs => gap) then
    wait := ceil(extract(epoch from (last_at + make_interval(secs => gap) - now())));
    raise exception 'TOO_FAST:%', wait;
  end if;
  insert into stamps (visitor_id, booth_id) values (vid, bid) on conflict do nothing returning to_jsonb(stamps.*) into row_json;
  if row_json is null then return jsonb_build_object('dup', true); end if;
  return jsonb_build_object('ok', true, 'stamp', row_json);
end $$;
grant execute on function add_stamp(uuid, text, text) to anon;

-- 7. 행사 설정 (2026-09-14) ---------------------------------------------
-- 관리자 › 행사 설정 탭에서 저장. 행사명·일시·장소·완주 개수·설문 링크·교환 마감·문의·일정·자료 링크 (jsonb 하나).
-- anon 은 읽기만, 쓰기는 admin_save_settings(pw, data).
create table if not exists settings (id int primary key default 1 check (id = 1), data jsonb not null default '{}', updated_at timestamptz default now());
alter table settings enable row level security;
drop policy if exists settings_select on settings;
create policy settings_select on settings for select to anon using (true);
create or replace function admin_save_settings(pw text, data jsonb) returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform admin_ok(pw);
  insert into settings (id, data, updated_at) values (1, data, now()) on conflict (id) do update set data = excluded.data, updated_at = now();
end $$;
grant execute on function admin_save_settings(text, jsonb) to anon;

-- 8. 개인정보 잠금 · 기록 이어받기 · 수동 도장 (2026-09-14) -----------------
-- 전엔 anon 키로 visitors/stamps 를 누구나 읽을 수 있었음(명단 노출). 이제 방문객은 자기 uuid 로만, 관리자는 비번 RPC 로만 읽음.
drop policy if exists visitors_insert on visitors;   -- 등록도 RPC(visitor_create)로. 직접 insert 는 returning 에 select 권한이 필요해서 어차피 못 씀
drop policy if exists visitors_select on visitors;
drop policy if exists stamps_select   on stamps;
revoke all on visitor_stats from anon, authenticated;   -- 뷰는 소유자 권한으로 돌아 RLS 를 우회하므로 권한 자체를 뺌. booth_stats·hourly_stats 는 개인정보 없는 집계라 둠

-- 방문객 RPC (uuid 를 아는 사람 = 본인. uuid 는 추측 불가)
create or replace function visitor_create(nm text, school text, grade text, gender text) returns setof visitors
language sql security definer set search_path = public, extensions as $$
  insert into visitors (name, school, grade, gender, consented_at) values (left(nm, 20), left(coalesce(school, ''), 30), coalesce(grade, ''), coalesce(gender, ''), now()) returning *;
$$;
create or replace function visitor_get(vid uuid) returns setof visitors
language sql security definer set search_path = public, extensions stable as $$ select * from visitors where id = vid; $$;
create or replace function visitor_stamps(vid uuid) returns setof stamps
language sql security definer set search_path = public, extensions stable as $$ select * from stamps where visitor_id = vid order by created_at; $$;
-- 기록 이어받기: 6자리 코드(uuid 끝 6자리, 내 스탬프 화면에 표시) + 이름이 맞으면 그 방문객. 틀리면 0.3초 지연
create or replace function visitor_recover(code text, nm text) returns setof visitors
language plpgsql security definer set search_path = public, extensions as $$
begin
  return query select * from visitors v where right(replace(v.id::text, '-', ''), 6) = lower(trim(code)) and v.name = trim(nm) limit 1;
  if not found then perform pg_sleep(0.3); end if;
end $$;
grant execute on function visitor_create(text, text, text, text), visitor_get(uuid), visitor_stamps(uuid), visitor_recover(text, text) to anon;

-- 관리자 읽기 RPC (비번 동봉). 1000 행씩 페이징
create or replace function admin_counts(pw text) returns jsonb
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform admin_ok(pw);
  return jsonb_build_object('visitors', (select count(*) from visitors), 'active', (select count(distinct visitor_id) from stamps), 'stamps', (select count(*) from stamps));
end $$;
create or replace function admin_visitor_stats(pw text, min_n int, off int, lim int)
returns table(id uuid, name text, school text, grade text, gender text, created_at timestamptz, survey_done_at timestamptz, gift_received_at timestamptz, n int)
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform admin_ok(pw);
  return query select v.id, v.name, v.school, v.grade, v.gender, v.created_at, v.survey_done_at, v.gift_received_at, v.n
    from visitor_stats v where v.n >= min_n order by v.created_at desc offset off limit lim;
end $$;
create or replace function admin_visitors(pw text, off int, lim int) returns setof visitors
language plpgsql security definer set search_path = public, extensions as $$
begin perform admin_ok(pw); return query select * from visitors order by created_at offset off limit lim; end $$;
create or replace function admin_stamps(pw text, off int, lim int) returns setof stamps
language plpgsql security definer set search_path = public, extensions as $$
begin perform admin_ok(pw); return query select * from stamps order by id offset off limit lim; end $$;
-- 방문객 찾기(이름·학교·코드) — 폰 바뀐 사람 코드 알려주기, 수동 도장용
create or replace function admin_find_visitor(pw text, q text)
returns table(id uuid, name text, school text, grade text, gender text, created_at timestamptz, survey_done_at timestamptz, gift_received_at timestamptz, n int)
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform admin_ok(pw);
  return query select v.id, v.name, v.school, v.grade, v.gender, v.created_at, v.survey_done_at, v.gift_received_at, v.n
    from visitor_stats v where v.name ilike '%' || q || '%' or v.school ilike '%' || q || '%' or right(replace(v.id::text, '-', ''), 6) = lower(q)
    order by v.created_at desc limit 50;
end $$;
-- 수동 도장 (QR 훼손·카메라 안 되는 폰). 토큰·시간 간격 검사 없음
create or replace function admin_add_stamp(pw text, vid uuid, bid text) returns jsonb
language plpgsql security definer set search_path = public, extensions as $$
declare row_json jsonb;
begin
  perform admin_ok(pw);
  insert into stamps (visitor_id, booth_id) values (vid, bid) on conflict do nothing returning to_jsonb(stamps.*) into row_json;
  if row_json is null then return jsonb_build_object('dup', true); end if;
  return jsonb_build_object('ok', true, 'stamp', row_json);
end $$;
grant execute on function admin_counts(text), admin_visitor_stats(text, int, int, int), admin_visitors(text, int, int), admin_stamps(text, int, int),
  admin_find_visitor(text, text), admin_add_stamp(text, uuid, text) to anon;

-- 9. 앱 내 설문 (2026-09-15) ---------------------------------------------
-- 관리자 › 행사 설정의 '설문 링크'가 비어 있으면 앱 안의 설문 화면(#/survey)을 쓴다. 문항은 settings.survey (관리자 › 설문 탭).
-- 응답은 survey_answers 에 방문객 uuid 로만 저장(이름 없음). 제출하면 visitors.survey_done_at 도 같이 찍힘 → 교환권.
create table if not exists survey_answers (
  visitor_id uuid primary key references visitors(id) on delete cascade,
  answers jsonb not null,                 -- {문항id: 값}. 값은 숫자(척도)·문자열(단일/부스/주관식)·문자열 배열(복수)
  created_at timestamptz default now()
);
alter table survey_answers enable row level security;   -- 정책 없음 = RPC 로만

-- 방문객: 제출. 완주(도장 ≥ settings.stampGoal) 전이면 NOT_DONE. 두 번 제출하면 처음 것 유지
create or replace function visitor_survey_submit(vid uuid, ans jsonb) returns jsonb
language plpgsql security definer set search_path = public, extensions as $$
declare goal int; n int;
begin
  if not exists (select 1 from visitors where id = vid) then raise exception 'NO_VISITOR'; end if;
  goal := coalesce((select (data->>'stampGoal')::int from settings where id = 1), 7);
  select count(*) into n from stamps where visitor_id = vid;
  if n < goal then raise exception 'NOT_DONE'; end if;
  if pg_column_size(ans) > 8000 then raise exception 'TOO_LONG'; end if;
  insert into survey_answers (visitor_id, answers) values (vid, ans) on conflict (visitor_id) do nothing;
  update visitors set survey_done_at = coalesce(survey_done_at, now()) where id = vid;
  return jsonb_build_object('ok', true);
end $$;
grant execute on function visitor_survey_submit(uuid, jsonb) to anon;

-- 관리자: 응답 목록 (학교·학년·성별 동봉, 이름 없음). 1000행 페이징. 결과 집계·CSV 는 화면에서
create or replace function admin_survey_answers(pw text, off int, lim int)
returns table(visitor_id uuid, school text, grade text, gender text, created_at timestamptz, answers jsonb)
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform admin_ok(pw);
  return query select a.visitor_id, v.school, v.grade, v.gender, a.created_at, a.answers
    from survey_answers a join visitors v on v.id = a.visitor_id order by a.created_at offset off limit lim;
end $$;
grant execute on function admin_survey_answers(text, int, int) to anon;

-- 대시보드용: 숫자(척도) 문항 평균·응답 수. admin_dashboard 가 'survey' 키로 같이 내보냄
create or replace function survey_scale_summary() returns jsonb
language sql security definer set search_path = public, extensions stable as $$
  select jsonb_build_object('n', (select count(*) from survey_answers),
    'scales', coalesce((select jsonb_agg(jsonb_build_object('q', q, 'avg', a, 'n', n))
                        from (select key q, round(avg((value)::text::numeric), 2) a, count(*) n
                              from survey_answers, jsonb_each(answers) where jsonb_typeof(value) = 'number' group by key) x), '[]'));
$$;
revoke all on function survey_scale_summary() from public, anon;

-- 10. 운영 대시보드 (2026-09-15) ---------------------------------------------
-- 운영대시보드.html 이 15초마다 이 RPC 하나만 부른다. 방문객 이름 등 개인정보는 안 나가고 집계만.
-- goal(완주 개수)은 settings.stampGoal, 없으면 7.
create or replace function admin_dashboard(pw text) returns jsonb
language plpgsql security definer set search_path = public, extensions as $$
declare goal int; res jsonb;
begin
  perform admin_ok(pw);
  goal := coalesce((select (data->>'stampGoal')::int from settings where id = 1), 7);
  select jsonb_build_object(
    'at', now(), 'goal', goal,
    'visitors',    (select count(*) from visitors),
    'active',      (select count(distinct visitor_id) from stamps),
    'stamps',      (select count(*) from stamps),
    'new_15m',     (select count(*) from visitors where created_at > now() - interval '15 min'),
    'stamps_15m',  (select count(*) from stamps   where created_at > now() - interval '15 min'),
    'achievers',   (select count(*) from (select visitor_id from stamps group by visitor_id having count(*) >= goal) a),
    'survey_done', (select count(*) from visitors where survey_done_at is not null),
    'gift_done',   (select count(*) from visitors where gift_received_at is not null),
    'gift_15m',    (select count(*) from visitors where gift_received_at > now() - interval '15 min'),
    -- 부스별: 누적 n, 최근 15분 n15, 마지막 도장 시각
    'per_booth',   (select coalesce(jsonb_agg(jsonb_build_object('booth_id', booth_id, 'n', n, 'n15', n15, 'last_at', last_at)), '[]')
                    from (select booth_id, count(*) n, count(*) filter (where created_at > now() - interval '15 min') n15, max(created_at) last_at from stamps group by booth_id) b),
    -- 최근 6시간 10분 단위 도장 수
    'per_10min',   (select coalesce(jsonb_agg(jsonb_build_object('t', t, 'n', n) order by t), '[]')
                    from (select date_trunc('hour', created_at) + (extract(minute from created_at)::int / 10) * interval '10 min' t, count(*) n
                          from stamps where created_at > now() - interval '6 hours' group by 1) m),
    -- 시간대별 (KST)
    'per_hour',    (select coalesce(jsonb_agg(jsonb_build_object('h', h, 'n', n) order by h), '[]')
                    from (select extract(hour from created_at at time zone 'Asia/Seoul')::int h, count(*) n from stamps group by 1) x),
    -- 학년별·성별 등록 수, 학교 상위 10
    'by_grade',    (select coalesce(jsonb_agg(jsonb_build_object('g', g, 'n', n)), '[]') from (select coalesce(nullif(grade, ''), '미입력') g, count(*) n from visitors group by 1) x),
    'by_gender',   (select coalesce(jsonb_agg(jsonb_build_object('g', g, 'n', n)), '[]') from (select coalesce(nullif(gender, ''), '미입력') g, count(*) n from visitors group by 1) x),
    'top_schools', (select coalesce(jsonb_agg(jsonb_build_object('s', s, 'n', n) order by n desc), '[]') from (select school s, count(*) n from visitors where coalesce(school, '') <> '' group by 1 order by 2 desc limit 10) x),
    -- 도장 개수 분포 (goal 이상은 goal 으로 묶음). 0개는 visitors - active 로 화면에서 계산
    'dist',        (select coalesce(jsonb_agg(jsonb_build_object('k', k, 'n', n) order by k), '[]') from (select least(c, goal) k, count(*) n from (select count(*) c from stamps group by visitor_id) y group by 1) x),
    -- 최근 도장 30개 (부스·시각만)
    'recent',      (select coalesce(jsonb_agg(jsonb_build_object('booth_id', booth_id, 'at', created_at) order by created_at desc), '[]') from (select booth_id, created_at from stamps order by created_at desc limit 30) r),
    -- 앱 내 설문 척도 평균 (9절). 테이블이 아직 없으면 null
    'survey',      (case when to_regclass('public.survey_answers') is null then null else survey_scale_summary() end)
  ) into res;
  return res;
end $$;
grant execute on function admin_dashboard(text) to anon;

# 부스 QR 스탬프 랠리

![Vanilla JS](https://img.shields.io/badge/Vanilla%20JS-single%20HTML-F7DF1E?logo=javascript&logoColor=black)
![Supabase](https://img.shields.io/badge/Supabase-Postgres%20%2B%20REST%20%2B%20RPC-3FCF8E?logo=supabase&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-static%20hosting-black?logo=vercel)
![Playwright](https://img.shields.io/badge/tests-playwright%20e2e-45ba4b?logo=playwright&logoColor=white)
![Load](https://img.shields.io/badge/%EC%A7%80%EC%86%8D%20%ED%85%8C%EC%8A%A4%ED%8A%B8-11%2C558%20req%20%C2%B7%20%EC%97%90%EB%9F%AC%200-brightgreen)
![Cost](https://img.shields.io/badge/%EC%9A%B4%EC%98%81%EB%B9%84-0%EC%9B%90-blue)

**부스 90여 개에 QR 한 장씩 붙여 두면, 방문객이 폰으로 찍을 때마다 도장이 쌓이는 행사용 웹앱.**
7개를 모으면 앱 안에서 설문에 답하고 교환권을 받아 운영본부에서 선물을 받습니다. 운영본부는 대시보드로 현장을 실시간으로 봅니다.

> 실제 수학·과학 축전(부스 95개, 하루 최대 5만 명)에 쓰인 앱의 공개 버전입니다. 부스명·기관명은 더미 데이터이고 Supabase 주소·키는 자리표시자입니다.

<p align="center"><img src="assets/dashboard.png" width="100%" alt="운영 대시보드"></p>

## 왜 이렇게 만들었나

| 현장 조건 | 결정 |
|---|---|
| 방문객 수천 명, 앱 설치 요구 불가 | QR → 브라우저에서 바로. 파일은 HTML 하나 + JS 둘 |
| 예산 없음, 담당자가 개발자 아님 | Supabase 무료 플랜 + Vercel 정적. 행사 설정·부스·설문 문항은 관리자 화면에서 |
| 부스 측 인력이 없음 (도장 찍어줄 사람 없음) | 부스에 고정 QR만. 검증은 서버가: QR 마다 비밀 토큰 + 도장 간격 90초 |
| 미성년자 개인정보 | 이름·학교·학년·성별만. 익명 키로는 명단을 못 읽고 RPC 로만 |
| 운동장 통신 불안정 | 도장 실패·8초 초과 시 폰에 저장 후 자동 재전송 |
| 운영본부가 상황을 알아야 함 | 15초 갱신 대시보드: 어디가 붐비는지, 어느 QR 이 안 찍히는지 |

## 방문객 화면

<table>
  <tr>
    <td align="center"><img src="assets/home.png" width="150"><br><sub><b>홈</b><br>스탬프 카드·검색·분류</sub></td>
    <td align="center"><img src="assets/register.png" width="150"><br><sub><b>등록</b><br>학교·학년·이름·성별</sub></td>
    <td align="center"><img src="assets/map-phone.png" width="150"><br><sub><b>지도</b><br>실제 배치도·핀치줌</sub></td>
    <td align="center"><img src="assets/map-route.png" width="150"><br><sub><b>가는 길</b><br>정문→부스, 가까운 출구</sub></td>
    <td align="center"><img src="assets/booth.png" width="150"><br><sub><b>부스 소개</b><br>영상·PDF·운영 시간·대상</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/my-stamps-done.png" width="150"><br><sub><b>완주</b><br>7개 모으면 설문 안내</sub></td>
    <td align="center"><img src="assets/survey.png" width="150"><br><sub><b>앱 내 설문</b><br>별점·내 부스 고르기·객관식</sub></td>
    <td align="center"><img src="assets/voucher.png" width="150"><br><sub><b>교환권</b><br>제출 즉시 QR + 코드</sub></td>
    <td align="center" colspan="2"><img src="assets/map-pc.png" width="320"><br><sub><b>지도 (PC)</b><br>부스 95개 전체, 확대하면 이름표</sub></td>
  </tr>
</table>

## 운영본부 화면

대시보드는 TV 에 띄워 두는 별도 페이지(`/dashboard`). 관리자 화면은 앱 안 `#/admin`.

<table>
  <tr>
    <td width="50%"><img src="assets/dashboard-table.png"><br><sub><b>대시보드 · 부스 전체 표</b> — 열 제목 정렬·검색, 30분 넘게 도장 없으면 빨강</sub></td>
    <td width="50%"><img src="assets/admin-dash.png"><br><sub><b>관리자 · 현황</b> — 등록·도장·완주·수령, 시간대별, 부스별</sub></td>
  </tr>
  <tr>
    <td><img src="assets/admin-gift.png"><br><sub><b>선물 수령</b> — 교환권 QR 연속 스캔 또는 코드 검색으로 수령 처리, 방문객 찾기·수동 도장</sub></td>
    <td><img src="assets/admin-survey.png"><br><sub><b>설문</b> — 문항 편집(5가지 유형) + 결과 집계 + CSV</sub></td>
  </tr>
  <tr>
    <td><img src="assets/admin-booths.png"><br><sub><b>부스</b> — 카드 편집·순서·엑셀·PDF/사진, 운영 시간·대상(초등/중고등), 시간대 전환(오후엔 다른 부스로: 번호·자료·도장 유무까지)</sub></td>
    <td><img src="assets/admin-qr.png"><br><sub><b>QR 시트</b> — 부스별 토큰 포함 QR, A4 인쇄</sub></td>
  </tr>
  <tr>
    <td><img src="assets/admin-map.png"><br><sub><b>지도</b> — 화장실·휴지통 표시를 탭으로 놓고 지움, 방문객 지도에 바로 반영</sub></td>
    <td><img src="assets/admin-status.png"><br><sub><b>운영 상태</b> — 쉬는 부스를 한 화면에서 골라 적용, 방문객 폰엔 흐리게</sub></td>
  </tr>
  <tr>
    <td><img src="assets/admin-event.png"><br><sub><b>행사 설정</b> — 행사명·완주 개수·설문·긴급 공지·일정, 열린 폰에 2분 내 반영</sub></td>
    <td><img src="assets/soak-test.png"><br><sub><b>지속 테스트</b> — 초당 4명 × 10분, 에러 0 · p95 64ms</sub></td>
  </tr>
  <tr>
    <td><img src="assets/admin-time-sheet.png"><br><sub><b>시간대 전환</b> — 오전 운영본부 자리가 12:00 부터 체험 부스로: 바뀐 후 번호·이름·분류·운영 시간·QR 도장 유무·자료를 따로 지정. 시각은 24시간 입력 + 시·분 칩</sub></td>
    <td><img src="assets/booth-variant.png"><br><sub><b>전환 후 방문객 화면</b> — 같은 QR·같은 자리지만 번호 1·오후 부스로 보이고 "12:00 전엔 본1" 안내. 열린 폰도 20초 안에 갱신</sub></td>
  </tr>
</table>

## 흐름

```mermaid
flowchart LR
  QR[부스 QR<br/>?b=번호&t=토큰] --> S{등록됨?}
  S -- 아니오 --> R[등록<br/>학교·학년·이름·성별] --> ST
  S -- 예 --> ST[add_stamp RPC]
  ST -- 토큰 불일치 / 90초 안 --> X[거절 화면]
  ST -- 통신 실패 --> Q[폰에 저장<br/>자동 재전송]
  ST -- OK --> C{7개?}
  C -- 아니오 --> M[지도에서 다음 부스]
  C -- 예 --> SV[앱 내 설문] --> V[교환권 QR+코드] --> G[운영본부가 QR 스캔<br/>수령 처리]
```

## 아키텍처

```
 방문객 폰 (index.html)                       운영본부 (index.html#/admin · dashboard.html)
   │ anon 키                                    │ anon 키 + 관리자 비번(RPC 인자)
   ▼                                            ▼
 ┌────────────────────── Supabase (Postgres + PostgREST) ──────────────────────┐
 │ 직접 읽기  booths · settings · booth_stats · hourly_stats   (개인정보 없음)      │
 │ 방문객 RPC visitor_create / visitor_get / visitor_stamps / visitor_recover       │
 │           add_stamp(토큰·90초 검사) / visitor_survey_submit(완주 확인)            │
 │ 관리자 RPC admin_ok(비번 해시) 뒤에서만 — 집계·명단·선물·부스·설정·대시보드         │
 │ RLS       visitors · stamps · survey_answers · booth_tokens 정책 없음 = RPC 로만   │
 └────────────────────────────────────────────────────────────────────────────┘
```

- **한 파일 구조** — CONFIG → UTIL → STORAGE → DATA LAYER(LocalDB / SupabaseDB, 같은 인터페이스) → 상태 → 지도 기하 → 라우터 → 화면 → 스캐너 → 관리자 → BOOT. `CONFIG.supabaseUrl` 을 비우면 브라우저 저장소만으로 동작(데모).
- **설정은 서버에** — 행사명·완주 개수·설문 문항·공지·일정을 관리자가 저장하면 열린 폰에도 2분 안에 반영. 저장은 서버에서 키 단위로 병합해 관리자 둘이 다른 항목을 동시에 저장해도 서로 지우지 않음.
- **대시보드는 요청 하나** — `admin_dashboard` RPC 가 집계 전부를 jsonb 로 (이름 없음). 15초 갱신에 요청 1개. 부스 줄을 누르면 그 부스 참여자 명단(`admin_booth_visitors`)만 따로.
- **무료 한도 안에서 4~5만 명** — jsQR·qrcode 는 CDN 우선(3초 타임아웃 → 같은 서버 파일 폴백, 1년 immutable), HTML 만 no-cache, favicon 인라인, 부스 목록은 배포 시 HTML 에 박은 시드의 버전이 서버 `settings.boothsVersion` 과 같으면 요청 생략. 첫 방문·재방문 모두 Vercel 1건(HTML) · Supabase 1~3건(각 1KB 안팎). 4만 명 기준 Vercel Edge Requests 약 40만/100만, Supabase egress 약 1.5GB/5GB.
- **지도는 코드로** — 이미지 없이 스타디움 기하(직선+반원)를 계산해 SVG 로. 부스 번호·구역만 바꾸면 자리가 따라옴.

## 기술 스택

| 영역 | 선택 | 이유 |
|---|---|---|
| 프런트 | Vanilla JS, 단일 HTML, 인라인 SVG | 빌드 없이 파일 하나. 담당자가 그대로 열어볼 수 있음 |
| QR | jsQR(카메라) · qrcode.js(교환권·인쇄) | jsdelivr CDN 우선, 3초 안에 안 오면 같은 서버 파일로 폴백 |
| DB / API | Supabase Postgres + PostgREST + plpgsql RPC | Auth 없이 anon 키 하나. 쓰기·개인정보는 전부 `security definer` RPC 뒤 |
| 호스팅 | Vercel 정적 | 파일 4개 업로드가 전부. `vercel.json` 에 캐시 헤더(js immutable / html no-cache) |
| 테스트 | Playwright(Chrome) e2e · Node 부하/지속 스크립트 | 실서버로 등록→도장→설문→교환권→관리자까지 |

## 보안·개인정보

- anon(publishable) 키는 공개용. `service_role` 키·DB 비밀번호는 코드 어디에도 없음.
- 방문객 데이터는 **uuid 를 아는 폰 = 본인**. 폰을 바꾸면 6자리 코드 + 이름으로 이어받기.
- 관리자 비밀번호는 pgcrypto 해시로 서버 저장, 8자 이상 강제. 10분 안 10회 틀리면 1분 잠금 — 잠금은 **틀린 비밀번호에만** 걸리고 맞는 비밀번호는 잠금 중에도 통과(외부인이 관리자 주소에서 비밀번호를 반복해 틀려도 운영본부 기능이 멈추지 않음). 틀렸을 때 지연(`pg_sleep`)은 두지 않음 — 연결을 붙들어 DoS 통로가 됨.
- 치팅: QR 주소에 부스별 서버 토큰(`booth_tokens`, 읽기 불가, 32자) + 같은 사람 도장 간격 90초. 링크를 공유받아도 7개에 10분 넘게 걸림.
- 선물 수령은 서버가 '아직 안 받은 사람'만 처리하고 결과를 돌려줌 — 운영본부 여러 명이 같은 교환권을 동시에 처리해도 한 번만.
- 행사 후 관리자 › 데이터에서 개인정보 파기.

## 부하·지속 테스트 (Supabase 무료 플랜)

| | 폭주 테스트 | 지속 테스트 1차 | 지속 테스트 2차 |
|---|---|---|---|
| 모양 | N명이 3초 안에 동시 등록+도장 7개 | 초당 4명 도착 × 10분, 실제 RPC 흐름(토큰·90초 간격) + 대시보드 15초 폴링 | 초당 6명 도착 × 15분, 서로 다른 uuid + 유효 토큰, 대시보드 2대 폴링 |
| 결과 | 800명 동시까지 에러 0 · p95 < 1s, 2000명은 66% 타임아웃 | 방문객 2,344명 · 요청 11,558건 · **에러 0 · p50 53ms · p95 64ms**, 10분간 지연 상승 없음 | 방문객 5,242명 · 요청 35,314건 · **에러 0 · p95 73ms**. 초당 59건까지 평평, 65건에서 쓰기 p95 3~4초로 줄 섬(에러 없음) |

무료 컴퓨트의 한계는 대략 **초당 60건 쓰기**. 행사 실부하(하루 5만 명 = 초당 2~3명 등록, 부스 체류가 길어 도장은 초당 10~15건)보다 훨씬 높은 부하를 버텨 무료 플랜으로 충분하다고 판단. 위험은 개막 직후 순간 폭주뿐 — 그건 행사 며칠 전 Supabase Pro + 컴퓨트 Micro 로 올려두는 것으로 대비(컴퓨트 변경 시 약 2분 다운타임이라 당일 아침엔 하지 않음).

### 지속 테스트 2차 — 분 단위 실측 (`지속테스트_2026-09-15_15분_6ps.json`)

도착률을 고정(초당 6명)하면 누적 방문객이 늘면서 초당 요청이 선형으로 올라간다. 어디서 꺾이는지 보려고 분 단위로 기록했다.

<p align="center"><img src="assets/soak-by-minute.png" width="100%" alt="지속 테스트 2차 분 단위 실측 — 초당 요청 수와 쓰기/읽기 p95"></p>

| 구간 | 초당 요청 | p50 | p95 | 최대 | 대시보드 폴링 p50 | 에러 |
|---|---|---|---|---|---|---|
| 0~4분 | 9.6 → 27.6 | 53~57ms | 70~113ms | 308ms | 73~149ms | 0 |
| 5~6분 | 28.7 → 37.1 | 53~54ms | 98~267ms | 3.9s | 93~241ms | 0 |
| 7~13분 | 37.9 → 63.8 | 52~55ms | 63~68ms | 301ms | 133~263ms | 0 |
| 14분 | **64.9** | 54ms | **3.4s** | 6.1s | 327ms | 0 |

| 요청 종류 | 건수 | 에러 | p50 | 분 단위 p95 최댓값 |
|---|---|---|---|---|
| 등록 `visitor_register` | 5,242 | 0 | 54ms | 3.8s |
| 도장 `add_stamp` | 22,330 | 0 | 54ms | 4.2s |
| 재진입(내 정보·내 도장 조회) | 6,712 | 0 | 52ms | 249ms |
| 설문 제출 | 1,030 | 0 | 54ms | 3.1s |

- **p50 은 끝까지 52~57ms 로 평평**하고 꼬리(p95·최대)만 늘어난다 → 처리 자체가 느려진 게 아니라 쓰기 요청이 줄을 서는 형태. 읽기(재진입)는 포화 구간에서도 p95 249ms.
- 5~6분의 일시적 꼬리는 에러 없이 1분 안에 회복했고, 이후 초당 64건까지는 다시 p95 60ms 대로 돌아왔다.
- 전체 p99 는 2.3s — 마지막 1분(초당 65건)의 대기열이 만든 값이다. 그래서 한계를 "초당 약 60건 쓰기"로 잡았다.

**요청 수·전송량 (재방문 1회, Chrome 실측)**: Vercel HTML 1건(js 는 디스크 캐시) · Supabase 설정 1건(등록자는 내 정보·내 도장 포함 3건) · 404 없음. 5만 명 × 리로드 10회 ≈ Vercel 65만 요청, Supabase 전송 수백 MB.

## 행사 전 점검 (2026-10)

행사 사흘 전 방문객 흐름 · 관리자 · 지도 · 대시보드 · SQL · 보안으로 영역을 나눠 코드를 다시 읽고, 의심 지점마다 Playwright 재현 스크립트를 만들어 확인했다. 43건을 찾아 1건(Storage 익명 업로드 정책, 행사 후 회수)을 빼고 모두 수정했다. 주요 항목:

| 발견 | 수정 |
|---|---|
| QR 을 먼저 찍은 미등록 방문객이 등록 후 도장 화면으로 돌아오지 못함 — 라우터가 해시 전체를 디코딩해 복귀 주소(`%2Fstamp%2F7`)가 쪼개짐 | 조각별 디코딩. 회귀 테스트 `test_qr_first.mjs` 추가 |
| 관리자 잠금이 전역이라 외부인이 틀린 비밀번호를 반복하면 운영본부 기능까지 1분씩 멈춤 | 잠금은 틀린 비밀번호에만. 실서버 `test_lockout.mjs` 로 확인 |
| 설정 저장이 통째 교체라 관리자 둘이 다른 항목을 저장하면 먼저 저장한 변경이 사라짐 | 서버 키 병합 + 저장 직전 서버값 재읽기 |
| 교환권을 관리자 여러 명이 동시에 처리하면 중복 수령 | 서버가 미수령일 때만 처리하고 결과 반환, 처리 직전 재조회 |
| 부스 번호가 `onclick` 문자열에 그대로 들어가 따옴표 하나로 버튼이 깨짐 | `data-*` 속성 + 이벤트 위임, 번호는 한글·영문·숫자 6자 규칙 |
| 서버가 느리면 부팅 중 최대 20초 빈 화면 | 로딩 표시, 설정·내 정보 병렬 로드 |
| 대시보드 히트맵이 도장 없는 부스를 뺀 뒤 자리를 계산해 앱 지도와 어긋남 | 전체 목록 기준으로 자리 계산 |
| 시간대 전환 부스가 지도 색·대시보드에 반영되지 않음 | 지도·대시보드도 전환 규칙 공유 |
| 이어받기 화면의 \[새로 등록\] 버튼이 속성 따옴표 충돌로 동작하지 않음 | 핸들러로 교체, 복귀 주소 검증 |

그 밖에 오프라인 재전송 안내 문구, 전환 시각 직후 화면 갱신, 엑셀 불러오기 검증, 번호 `2`/`02` 중복, 지도 이름표가 정문을 가리는 문제 등 표시·편의 항목 27건.

## 파생 버전: booth-lite (소규모 부스 · 태블릿 수기 도장)

같은 코드베이스에서 파생한 **부스 7개짜리 소규모 행사용** 버전. 지도가 없고, 폰이 없는 저학년 어린이가 많아 **부스마다 둔 태블릿으로 직원이 도장을 찍는 운영**이 핵심이다. 서버·호스팅은 축전과 완전히 분리. 자세한 변경점·운영 흐름·동기화 절차는 [`booth-lite/README.md`](booth-lite/README.md).

<p align="center"><img src="assets/booth-lite/tablet-search.png" width="520"><br><sub>부스 태블릿 — 방금 다른 부스에서 도장 찍은 아이들 · 부스별 도장 칸 (더미 데이터)</sub></p>

| 바뀐 것 | 내용 |
|---|---|
| 미니 모드 | 지도 탭·배치도·대시보드 히트맵 제거 |
| 등록 항목 | 소속·나이·연락처, 관리자에서 항목별 사용/필수 토글. DB 열은 그대로 두고 뜻만 바꿔 SQL 변경 없음 |
| 부스 태블릿 | 부스 QR 한 번으로 고정 → 이름 두 글자 검색 → [도장] → 확인(5초 자동) → 다음. 처음 온 아이는 등록+도장 한 번에 |
| 상황 공유 | 카드마다 1~7 부스 칸(받은 부스·이미 찍음), "방금 다른 부스에서 도장 찍은 아이들" 목록(10분, 탭 한 번) |
| 동명이인 | 등록 직전 같은 이름 확인 → 이 아이예요 / 다른 아이예요 |
| 설문 | 사용/안 함 토글. 끄면 완주 즉시 교환권 |
| 동기화 | 축전 원본 + 치환 스크립트 11개(`booth-lite/sync/`)로 재생성 → 축전 쪽 수정이 그대로 따라옴 |

## 설치

1. **Supabase** 프로젝트 생성 → SQL Editor 에 `supabase_setup.sql` 통째로 붙여넣고 Run (다시 실행해도 됨).
2. `원주축전_스탬프앱_3.html` 의 `CONFIG.supabaseUrl` · `supabaseAnonKey` 채우기 (`운영대시보드.html` 도 같은 값).
3. 관리자 `#/admin` (초기 비번 `1234`) → 데이터 탭에서 비번 변경 → 부스 탭에서 저장(서버로 올라가며 QR 토큰 발급) → QR 시트 인쇄. 저장 안 한 부스 변경이 있으면 QR 시트가 먼저 저장하라고 안내.
4. 배포: `배포.ps1` (deploy/ 갱신 → `?v=DEV` 를 배포 시각으로 치환 → 서버 부스 목록·버전을 `SEED_BOOTHS`/`seedVersion` 에 박음 → `vercel deploy --prod`). 부스를 고친 뒤 재배포하면 방문객 폰이 부스 목록을 서버에서 받지 않음. 배포 주소가 바뀌면 QR 재인쇄.

로컬에서 그냥 열어보려면 `CONFIG.supabaseUrl` 을 비우면 됨 — 브라우저 저장소로 동작하고 관리자 › 데이터에 데모 데이터 버튼이 생김. `CONFIG.testStampInput: true` 면 카메라 대신 부스 번호 입력창(https 없는 로컬용, 배포 스크립트가 false 로 바꿈).

## 개발자 정보

### 구조
```
원주축전_스탬프앱_3.html   앱 전체 (방문객 + 관리자). 스크립트 맨 위에 설계 개요·데이터 흐름 주석
운영대시보드.html          운영본부 대시보드 (admin_dashboard RPC)
supabase_setup.sql         테이블·뷰·RLS·RPC·Storage. 1~17절, 재실행 가능
jsQR.js · qrcode.min.js    로컬 라이브러리 (배포 시 같이)
배포.ps1 · deploy/         Vercel 배포 (vercel.json: cleanUrls, html no-cache · js immutable / 배포.ps1 이 ?v= 버전 치환)
기능정리.md                요구사항·결정 사항·변경 이력의 단일 출처
tests/                     playwright e2e (test_v3 · test_survey · test_qr_first · test_media_sheet 등 12벌), soak.mjs 지속 테스트, soakchart.mjs 결과 차트, shots_public.mjs README 스크린샷
assets/                    README 스크린샷 (전부 더미 데이터)
```

### 명령
| 명령 | 설명 |
|---|---|
| `cd tests && npm i playwright` | 테스트 준비 (Chrome 채널 사용) |
| `$env:ADMIN_PW="관리자비번"` | 실서버 테스트(test_v3 · test_live_survey · soak · shots 대시보드) 전에 한 번. 없으면 바로 종료 |
| `node tests/test_v3.mjs` | 실서버 e2e: 설문 타이머·복귀 링크·탭 동기화·행사 설정·대시보드 |
| `node tests/test_survey.mjs` | 로컬 모드 e2e: 앱 내 설문 제출·관리자 문항 편집·결과·CSV |
| `node tests/test_gift_scan.mjs` · `test_booth_visitors.mjs` | 로컬 모드 e2e: 교환권 QR 연속 스캔 · 부스별 참여자 명단(현황 시트·대시보드 카드) |
| `node tests/test_seed.mjs` | 부스 시드 버전 매칭 · CDN 우선 로드 · CDN 차단/무응답 폴백 |
| `node tests/test_qr_first.mjs` | 로컬 모드 e2e: QR 먼저 찍은 미등록 방문객이 등록 후 도장 화면으로 돌아와 찍히는지(숫자·한글 부스 번호) |
| `node tests/test_lockout.mjs <비번>` (또는 ADMIN_PW) | 실서버: 틀린 비번 10회 → 1분 잠금, 잠금 중 맞는 비번 통과 → 해제 (지연 없음 확인) |
| `node tests/soak.mjs [분] [초당 도착] [접두어]` | 지속 테스트 → `지속테스트_날짜.json`, 이어서 `node tests/soakchart.mjs` 로 PNG. 테스트 데이터는 남김 |

### 설계 메모
- 화면 코드는 `DB.*` 만 부른다. LocalDB / SupabaseDB 가 같은 메서드를 구현하므로 저장소를 바꿔도 화면은 그대로.
- 서버 거절(BAD_TOKEN · TOO_FAST · NOT_DONE)은 통신 실패가 아니므로 오프라인 큐에 넣지 않고 안내 화면으로.
- 관리자 RPC 는 전부 `pw` 인자를 받아 `admin_ok(pw)` 로 시작. 비번이 바뀌면 다음 요청에서 자동 로그아웃.
- 설문은 세 가지 모드: 설문 링크 없음 → 앱 내 설문(기본) / 링크 있음 → 외부 폼 + 60초 뒤 자기신고 + `?survey` 복귀 링크 자동 완료 / 둘 다 없음 → 버튼만.
- DB 컬럼은 풀네임(`organization`, `sort_order`…), 앱 내부는 짧은 이름 — 변환은 `SupabaseDB._b()` 한 곳.
- 요구사항과 변경 이력은 `기능정리.md`.

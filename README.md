# 🎪 원주 수학과학축전 부스 스탬프 랠리

![Vanilla JS](https://img.shields.io/badge/Vanilla%20JS-single%20HTML-F7DF1E?logo=javascript&logoColor=black)
![Supabase](https://img.shields.io/badge/Supabase-Postgres%20%2B%20REST%20%2B%20RPC-3FCF8E?logo=supabase&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-static%20hosting-black?logo=vercel)
![Playwright](https://img.shields.io/badge/tests-playwright%20e2e-45ba4b?logo=playwright&logoColor=white)
![Load](https://img.shields.io/badge/%EC%A7%80%EC%86%8D%20%ED%85%8C%EC%8A%A4%ED%8A%B8-11%2C558%20req%20%C2%B7%20%EC%97%90%EB%9F%AC%200-brightgreen)
![Cost](https://img.shields.io/badge/%EC%9A%B4%EC%98%81%EB%B9%84-0%EC%9B%90-blue)

행사장 부스 90여 개에 QR을 붙여 두고, 방문객이 **폰으로 찍으면 도장이 쌓이는** 스탬프 랠리 웹앱입니다.
7개를 모으면 설문에 답하고 교환권을 받아 운영본부에서 선물을 받습니다. 운영본부는 대시보드로 현장을 실시간으로 봅니다.

- **설치 없음** — 방문객은 QR 찍으면 브라우저에서 바로. 앱 파일 하나(HTML) + JS 두 개
- **비용 0원** — Supabase 무료 플랜 + Vercel 정적 호스팅. 지속 테스트로 하루 5만 명 규모 검증
- **개인정보 최소·잠금** — 이름·학교·학년·성별만, 익명 키로는 명단을 읽을 수 없게 RPC 로만 접근
- **치팅 방지** — QR 마다 서버 토큰, 도장 사이 90초 간격을 서버가 검사

> 실제 행사에 쓰인 앱의 공개 버전입니다. 부스 목록·기관명은 더미 데이터로 바꿨고 Supabase 주소·키는 자리표시자입니다.

## 스크린샷

> 아래 그림의 방문객·응답은 모두 **테스트 데이터**입니다.

| | |
|---|---|
| **등록** — 학교·구분·학년·이름·성별, 동의 한 줄 ![등록](assets/register.png) | **지도(폰)** — 실제 배치도 기준 스타디움, 핀치줌·경로·출구 ![지도 폰](assets/map-phone.png) |
| **완주** — 7개 모으면 설문 안내 ![완주](assets/my-stamps-done.png) | **앱 내 설문** — 표정 5단계·내가 찍은 부스 고르기·객관식·자유답변 ![설문](assets/survey.png) |
| **교환권** — 제출 즉시 QR + 6자리 코드 ![교환권](assets/voucher.png) | **지도(PC)** — 부스 95개 전체 ![지도 PC](assets/map-pc.png) |

| | |
|---|---|
| **운영 대시보드** — 15초 갱신, 배치도 히트맵·추이·깔때기·학년·학교·설문 평균·부스 전체 표 ![대시보드](assets/dashboard.png) | **관리자 › 설문** — 문항 편집 + 결과 집계 + CSV ![관리자 설문](assets/admin-survey.png) |
| **관리자 › 선물 수령** — 코드로 찾아 수령 처리, 방문객 찾기·수동 도장 ![선물 수령](assets/admin-gift.png) | **관리자 › 행사 설정** — 행사명·완주 개수·설문·공지·일정을 서버에 저장 ![행사 설정](assets/admin-event.png) |

## 화면 구성

| 경로 | 화면 |
|---|---|
| `#/` | 홈: 스탬프 카드, 긴급 공지, 다음 일정, 부스 검색·분류 필터 |
| `#/map`, `#/map/번호` | 지도 (핀치줌·드래그, 경계 잠금), 부스 시트, 정문에서 가는 길, 가까운 출구 |
| `#/booth/번호` | 부스 소개 (사진·설명·위치·유튜브·PDF·도장 상태) |
| `#/stamp/번호` | QR 딥링크 도착 화면. 미등록이면 등록 후 복귀. 서버 거절(토큰·간격)이면 안내 |
| `#/my` | 내 스탬프. 6자리 코드(폰 바꿀 때 이어받기), 완주 시 설문 → 교환권 |
| `#/survey` | 앱 내 설문 (완주자만) |
| `#/register` | 등록 · 기록 이어받기 |
| `#/admin/…` | 관리자: 현황 · 선물 수령 · 부스 · QR 시트 · 행사 설정 · 설문 · 데이터 |
| `/dashboard` | 운영 대시보드 (별도 페이지, 관리자 비번) |

QR 형식 `주소?b=부스번호&t=토큰`, 입장용 `주소?join`.

## 아키텍처

```
 방문객 폰 (index.html)                      운영본부 (index.html#/admin · dashboard.html)
   │ anon 키                                   │ anon 키 + 관리자 비번(RPC 인자)
   ▼                                           ▼
 ┌──────────────────────── Supabase (Postgres + PostgREST) ────────────────────────┐
 │  직접 읽기: booths · settings · booth_stats · hourly_stats  (개인정보 없음)         │
 │  방문객 RPC: visitor_create / visitor_get / visitor_stamps / visitor_recover        │
 │             add_stamp(토큰·90초 검사) / visitor_survey_submit(완주 확인)             │
 │  관리자 RPC: admin_ok(비번 해시 비교) 뒤에서만 — 집계·명단·선물·부스·설정·대시보드     │
 │  RLS: visitors · stamps · survey_answers · booth_tokens 는 정책 없음 = RPC 로만       │
 └────────────────────────────────────────────────────────────────────────────────┘
```

- **한 파일 구조**: CONFIG → UTIL → STORAGE → DATA LAYER(LocalDB / SupabaseDB, 같은 인터페이스) → 상태 → 지도 기하 → 라우터 → 화면 → 스캐너 → 관리자 → BOOT. `CONFIG.supabaseUrl` 을 비우면 브라우저 로컬 저장소만으로 동작(목업·데모).
- **오프라인 큐**: 도장 전송이 실패하거나 8초를 넘기면 폰에 저장했다가 온라인 복귀·30초 주기·부팅 때 재전송.
- **설정은 서버에**: 행사명·완주 개수·설문 문항·공지·일정을 관리자가 저장하면 열린 폰에도 5분 안에 반영.
- **대시보드는 RPC 하나**: `admin_dashboard` 가 집계 전부를 jsonb 하나로 (이름 없음). 15초 갱신에 요청 1개.

## 기술 스택

| 영역 | 선택 | 이유 |
|---|---|---|
| 프런트 | Vanilla JS, 단일 HTML, 인라인 SVG 지도 | 빌드 없이 파일 하나 배포, 행사 담당자가 그대로 열어볼 수 있음 |
| QR | jsQR(카메라 스캔) · qrcode.js(교환권·인쇄 시트) | 로컬 파일 우선, 없으면 CDN 폴백 |
| DB / API | Supabase Postgres + PostgREST + plpgsql RPC | Auth 없이 anon 키 하나. 쓰기·개인정보는 전부 `security definer` RPC 뒤로 |
| 호스팅 | Vercel 정적 | HTML·JS 4개 업로드가 전부 |
| 테스트 | Playwright(Chrome) e2e · Node 부하/지속 스크립트 | 실서버로 등록→도장→설문→교환권→관리자까지 |

## 보안·개인정보

- anon(publishable) 키는 공개용. `service_role` 키와 DB 비밀번호는 코드 어디에도 없음.
- 방문객 데이터는 **uuid 를 아는 폰 = 본인** 원칙. 폰을 바꾸면 6자리 코드 + 이름으로 이어받기.
- 관리자 비밀번호는 pgcrypto 해시로 서버 저장, 틀리면 0.5초 지연. 8자 이상 강제.
- 치팅: QR 주소에 부스별 서버 토큰(`booth_tokens`, 읽기 불가) + 같은 사람 도장 간격 90초. 링크를 공유받아도 7개에 10분 넘게 걸림.
- 행사 후 관리자 › 데이터에서 개인정보 파기.

## 부하·지속 테스트 (Supabase 무료 플랜)

| | 폭주 테스트 (2026-09-14) | 지속 테스트 (2026-09-15) |
|---|---|---|
| 모양 | N명이 3초 안에 동시 등록+도장 7개 | 초당 4명 도착 × 10분, 실제 RPC 흐름(토큰·90초 간격) |
| 결과 | 800명 동시까지 에러 0 · p95 < 1s, 2000명은 66% 타임아웃 | 방문객 2,344명 · 요청 11,558건 · **에러 0 · p50 53ms · p95 64ms**, 지연 상승 없음 |

![지속 테스트](assets/soak-test.png)

행사 실부하(하루 5만 명 = 초당 2~3명 등록)보다 높은 부하를 10분간 버텨 무료 플랜으로 충분하다고 판단.

## 설치

1. **Supabase** 프로젝트 생성 → SQL Editor 에 `supabase_setup.sql` 통째로 붙여넣고 Run (다시 실행해도 됨).
2. `원주축전_스탬프앱_3.html` 의 `CONFIG.supabaseUrl` · `supabaseAnonKey` 채우기 (`운영대시보드.html` 도 같은 값).
3. 관리자 `#/admin` (초기 비번 `1234`) → 데이터 탭에서 비번 변경 → 부스 탭에서 저장(서버로 올라가며 QR 토큰 발급) → QR 시트 인쇄.
4. 배포: `배포.ps1` (deploy/ 폴더 갱신 후 `vercel deploy --prod`). 배포 주소가 바뀌면 QR 재인쇄.

로컬에서 그냥 열어보려면 `CONFIG.supabaseUrl` 을 비우면 됨 — 브라우저 저장소로 동작하고 관리자 › 데이터에 데모 데이터 버튼이 생김. `CONFIG.testStampInput: true` 면 카메라 대신 부스 번호 입력창(https 없는 로컬용, 배포 스크립트가 false 로 바꿈).

## 개발자 정보

### 구조
```
원주축전_스탬프앱_3.html   앱 전체 (방문객 + 관리자). 스크립트 맨 위에 설계 개요·데이터 흐름 주석
운영대시보드.html          운영본부 대시보드 (admin_dashboard RPC)
supabase_setup.sql         테이블·뷰·RLS·RPC·Storage. 1~10절, 재실행 가능
jsQR.js · qrcode.min.js    로컬 라이브러리 (배포 시 같이)
배포.ps1 · deploy/         Vercel 배포 (vercel.json: cleanUrls, no-cache)
기능정리.md                요구사항·결정 사항·변경 이력의 단일 출처
tests/                     playwright e2e (test_v3 · test_survey · test_live_survey), soak.mjs 지속 테스트, soakchart.mjs 결과 차트
assets/                    README 스크린샷
```

### 명령
| 명령 | 설명 |
|---|---|
| `cd tests && npm i playwright` | 테스트 준비 (Chrome 채널 사용) |
| `node tests/test_v3.mjs` | 실서버 e2e: 설문 타이머·복귀 링크·탭 동기화·행사 설정·대시보드 |
| `node tests/test_survey.mjs` | 로컬 모드 e2e: 앱 내 설문 제출·관리자 문항 편집·결과·CSV |
| `node tests/soak.mjs [분] [초당 도착]` | 지속 테스트 → `지속테스트_날짜.json`, 이어서 `node tests/soakchart.mjs` 로 PNG |

### 설계 메모
- 화면 코드는 `DB.*` 만 부른다. LocalDB / SupabaseDB 가 같은 메서드를 구현하므로 저장소를 바꿔도 화면은 그대로.
- 서버 거절(BAD_TOKEN · TOO_FAST · NOT_DONE)은 통신 실패가 아니므로 오프라인 큐에 넣지 않고 안내 화면으로.
- 관리자 RPC 는 전부 `pw` 인자를 받아 `admin_ok(pw)` 로 시작. 비번이 바뀌면 다음 요청에서 자동 로그아웃.
- 설문은 세 가지 모드: 설문 링크 없음 → 앱 내 설문(기본) / 링크 있음 → 외부 폼 + 60초 뒤 자기신고 + `?survey` 복귀 링크 자동 완료 / 둘 다 없음 → 버튼만.
- DB 컬럼은 풀네임(`organization`, `sort_order`…), 앱 내부는 짧은 이름 — 변환은 `SupabaseDB._b()` 한 곳.
- 요구사항과 변경 이력은 `기능정리.md`.

# 축전 앱 → booth-lite 동기화

축전 앱(C:\dev\stamp-rally-v3\원주축전_스탬프앱_3.html)이 바뀌면:
1. 축전 앱을 booth-lite_스탬프앱.html 로 복사
2. sync/ 의 1_ → 13_ 순서로 `python -I` 실행 (3·5는 대시보드가 이미 적용돼 있으면 'already patched' 로 끝남 — 정상)
3. CONFIG 의 supabaseUrl·supabaseAnonKey 를 booth-lite 값으로 다시 채움 (3번 스크립트는 대시보드 부분이 이미 적용돼 있으면 거기서 멈추는데, 앱 파일은 그 전에 저장됨)
4. 찾기 버튼 nowrap 스타일(`id="mGo"`) 확인

스크립트는 원문 문자열 치환이라 축전 앱 쪽 해당 줄이 바뀌면 assert 로 멈춤 → 그 치환만 손봐서 다시.

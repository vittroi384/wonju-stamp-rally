# 배포 폴더 갱신 + Vercel 업로드. 사용: PowerShell 에서  .\배포.ps1   (로그인 필요: npx vercel login)
# 주소: https://your-app.vercel.app  ·  대시보드 https://your-app.vercel.app/dashboard
# deploy/index.html   = 원주축전_스탬프앱_3.html (testStampInput false 로 바꾼 복사본)
# deploy/dashboard.html = 운영대시보드.html   → 주소/dashboard
$root = if($PSScriptRoot){ $PSScriptRoot }else{ Split-Path -Parent $MyInvocation.MyCommand.Path }
if(-not $root){ $root = (Get-Location).Path }
$utf8 = New-Object Text.UTF8Encoding $false
$src = Get-Content "$root\원주축전_스탬프앱_3.html" -Raw -Encoding UTF8
$src = $src -replace 'testStampInput: true,', 'testStampInput: false,'
$src = $src -replace '\?v=DEV', ('?v=' + (Get-Date -Format 'yyyyMMddHHmm'))   # js 캐시 무효화용 버전 (js 는 1년 immutable 캐시)
# 부스 시드 박기: 서버의 부스 목록 + settings.boothsVersion 을 HTML 에 넣어 앱이 부스 요청을 생략하게. 실패하면 경고만 하고 그대로 배포(앱은 서버에서 받음)
try {
  $url = [regex]::Match($src, "supabaseUrl: '([^']+)'").Groups[1].Value; $key = [regex]::Match($src, "supabaseAnonKey: '([^']+)'").Groups[1].Value
  $h = @{ apikey = $key; Authorization = "Bearer $key" }
  $ver = (Invoke-RestMethod -Uri "$url/rest/v1/settings?id=eq.1&select=data" -Headers $h)[0].data.boothsVersion
  $rows = Invoke-RestMethod -Uri "$url/rest/v1/booths?select=*&order=sort_order" -Headers $h
  if ($ver -and $rows.Count -gt 0) {
    $seed = @($rows | ForEach-Object { [ordered]@{ id = $_.id; n = $_.number; name = $_.name; cat = $_.category; org = $_.organization; zone = $_.zone; desc = $_.description; video = $_.video_url; pdf = $_.pdf_url; img = $_.image_url; hours = $_.operating_hours; variant = $_.time_variant } })
    $json = ($seed | ConvertTo-Json -Compress -Depth 4)
    if ($seed.Count -eq 1) { $json = "[$json]" }
    $src = [regex]::Replace($src, 'const SEED_BOOTHS = \[.*?\];', ('const SEED_BOOTHS = ' + $json.Replace('$', '$$') + ';'), 'Singleline')
    $src = $src -replace 'seedVersion: 0,', ("seedVersion: $ver,")
    Write-Host "부스 시드 박음: $($seed.Count)개, 버전 $ver"
  } else { Write-Host "부스 버전이 없어 시드 안 박음 (관리자 › 부스에서 한 번 저장하면 생김)" }
} catch { Write-Host "부스 시드 박기 실패(그대로 배포): $($_.Exception.Message)" }
[IO.File]::WriteAllText("$root\deploy\index.html", $src, $utf8)
Copy-Item "$root\운영대시보드.html" "$root\deploy\dashboard.html"
Copy-Item "$root\jsQR.js", "$root\qrcode.min.js" "$root\deploy\"
npx vercel deploy "$root\deploy" --prod --yes --name your-app

# 배포 폴더 갱신 + Vercel 업로드. 사용: PowerShell 에서  .\배포.ps1   (로그인 필요: npx vercel login)
# 주소: https://your-app.vercel.app  ·  대시보드 https://your-app.vercel.app/dashboard
# deploy/index.html   = 원주축전_스탬프앱_3.html (testStampInput false 로 바꾼 복사본)
# deploy/dashboard.html = 운영대시보드.html   → 주소/dashboard
$root = if($PSScriptRoot){ $PSScriptRoot }else{ Split-Path -Parent $MyInvocation.MyCommand.Path }
if(-not $root){ $root = (Get-Location).Path }
$utf8 = New-Object Text.UTF8Encoding $false
$src = Get-Content "$root\원주축전_스탬프앱_3.html" -Raw -Encoding UTF8
$src = $src -replace 'testStampInput: true,', 'testStampInput: false,'
[IO.File]::WriteAllText("$root\deploy\index.html", $src, $utf8)
Copy-Item "$root\운영대시보드.html" "$root\deploy\dashboard.html"
Copy-Item "$root\jsQR.js", "$root\qrcode.min.js" "$root\deploy\"
npx vercel deploy "$root\deploy" --prod --yes --name your-app

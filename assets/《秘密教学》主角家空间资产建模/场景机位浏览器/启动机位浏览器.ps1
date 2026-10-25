$ErrorActionPreference = 'Stop'
$studioRoot = $PSScriptRoot
$pythonCandidates = @("$env:USERPROFILE/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/pythonw.exe", "$env:USERPROFILE/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe")
$pythonExe = $pythonCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $pythonExe) { $pythonExe = (Get-Command pythonw.exe,python.exe -ErrorAction SilentlyContinue | Select-Object -First 1).Source }
if (-not $pythonExe) { throw '找不到Python，请安装Python 3.10或更新版本。' }
foreach ($studioPort in 8765..8785) {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:$studioPort/api/health" -TimeoutSec 1
        if ($health.app -eq $studioRoot) { Start-Process "http://127.0.0.1:$studioPort"; exit }
        continue
    } catch {}
    $listener = Get-NetTCPConnection -LocalPort $studioPort -State Listen -ErrorAction SilentlyContinue
    if ($listener) { continue }
    Start-Process -FilePath $pythonExe -ArgumentList @('"' + (Join-Path $studioRoot 'server.py') + '"', '--port', "$studioPort") -WorkingDirectory $studioRoot -WindowStyle Hidden
    exit
}
throw '机位浏览器端口正在使用，请关闭旧工作台后重试。'

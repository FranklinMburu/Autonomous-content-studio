# One-time setup of the laptop helper (clipping engine). Run in PowerShell from this folder:
#     powershell -ExecutionPolicy Bypass -File .\setup.ps1
# It asks before installing anything, and YOU type the GitHub token (it is never shown or sent anywhere but GitHub).
# Undo everything:  powershell -ExecutionPolicy Bypass -File .\setup.ps1 -Remove

param([switch]$Remove)
$ErrorActionPreference = "Stop"
$Home2 = Join-Path $env:USERPROFILE ".clips_agent"
$Task = "ClipsLaptopHelper"

if ($Remove) {
    Unregister-ScheduledTask -TaskName $Task -Confirm:$false -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $Home2 -ErrorAction SilentlyContinue
    Write-Host "Removed the scheduled task and $Home2 (yt-dlp and ffmpeg stay installed)."
    exit 0
}

Write-Host "== 1/5 Python"
$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py) { $py = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $py) { throw "Python not found. Install it from https://www.python.org/downloads/ (tick 'Add to PATH'), then run this again." }
& $py --version

Write-Host "== 2/5 yt-dlp (the downloader, pinned version)"
& $py -m pip install --user --quiet --upgrade "yt-dlp==2026.10.26"
& $py -m yt_dlp --version

Write-Host "== 3/5 ffmpeg (cuts the exact section)"
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    $a = Read-Host "ffmpeg is missing. Install it now with winget (Microsoft's installer, free)? [Y/N]"
    if ($a -match '^[Yy]') { winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements }
    else { throw "ffmpeg is needed. Run this again when you want to install it." }
    Write-Host "If 'ffmpeg' is still not found below, close and reopen PowerShell, then run setup again."
}
$ff = (Get-Command ffmpeg -ErrorAction SilentlyContinue).Source; if (-not $ff) { $ff = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Links\ffmpeg.exe" }; if (Test-Path $ff) { & $ff -version | Select-Object -First 1 } else { throw "ffmpeg not found yet: close PowerShell, open a new one, run setup again." }

Write-Host "== 4/5 GitHub token (you type it; it stays on this laptop)"
New-Item -ItemType Directory -Force -Path $Home2 | Out-Null
Copy-Item -Force (Join-Path $PSScriptRoot "agent.py") (Join-Path $Home2 "agent.py")
$tokFile = Join-Path $Home2 "token"
if (-not (Test-Path $tokFile)) {
    Write-Host "Create it at https://github.com/settings/personal-access-tokens/new :"
    Write-Host "  Repository access: Only select repositories -> Autonomous-content-studio"
    Write-Host "  Permissions: Contents -> Read and write. Expiration: 90 days. Nothing else."
    $sec = Read-Host "Paste the token (hidden)" -AsSecureString
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
    Set-Content -Path $tokFile -Value $plain -NoNewline -Encoding ascii
    $plain = $null
    icacls $tokFile /inheritance:r /grant:r "$($env:USERNAME):(R,W)" | Out-Null
}

Write-Host "== 5/5 Scheduled task: every 10 minutes, hidden, only while you're logged in"
$pyw = $py -replace 'python\.exe$', 'pythonw.exe'
if (-not (Test-Path $pyw)) { $pyw = $py }
$action = New-ScheduledTaskAction -Execute $pyw -Argument "`"$(Join-Path $Home2 'agent.py')`"" -WorkingDirectory $Home2
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 10)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 50)
Register-ScheduledTask -TaskName $Task -Action $action -Trigger $trigger -Settings $settings -Description "Downloads requested YouTube sections for the clipping pipeline" -Force | Out-Null

Write-Host "`nTest run (downloads nothing):"
& $py (Join-Path $Home2 "agent.py") --check
Write-Host "`nDone. Log: $Home2\agent.log   Remove later: .\setup.ps1 -Remove"

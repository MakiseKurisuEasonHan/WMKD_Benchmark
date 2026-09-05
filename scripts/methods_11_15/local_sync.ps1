param([string]$ProjectRoot = 'C:\Users\Eason\Desktop\WMKD_Benchmark')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $ProjectRoot
$syncDir = Join-Path $ProjectRoot 'tmp\methods_11_15_local_sync'
New-Item -ItemType Directory -Force -Path $syncDir | Out-Null
$syncLockPath = Join-Path $syncDir 'sync.lock'
try { $syncLock = [System.IO.File]::Open($syncLockPath, 'OpenOrCreate', 'ReadWrite', 'None') } catch { exit 0 }
$syncLog = Join-Path $syncDir 'sync.log'
$ackFile = Join-Path $syncDir 'local_sync_ack.json'
$remote = 'root@connect.westd.seetacloud.com'
$remoteAck = '/root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/local_sync_ack.json'
$failures = 0
while ($true) {
    try {
        $dirty = & git status --porcelain
        if ($LASTEXITCODE -ne 0) { throw 'git status failed' }
        if ($dirty) { Start-Sleep -Seconds 30; continue }
        & git fetch origin 2>&1 | Out-File -FilePath $syncLog -Append -Encoding utf8
        if ($LASTEXITCODE -ne 0) { throw 'git fetch failed' }
        $counts = (& git rev-list --left-right --count 'HEAD...origin/main').Trim() -split '\s+'
        if ($counts[0] -ne '0') { throw 'Local commits ahead; preserve work and wait for reconciliation' }
        & git merge --ff-only origin/main 2>&1 | Out-File -FilePath $syncLog -Append -Encoding utf8
        if ($LASTEXITCODE -ne 0) { throw 'Fast-forward failed; preserve work' }
        $head = (& git rev-parse HEAD).Trim()
        if (& git status --porcelain) { throw 'Local worktree changed during sync' }
        $remoteHead = & ssh -n -T -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -o BatchMode=yes -o ConnectTimeout=15 -p 32514 $remote 'git -C /root/autodl-tmp/WMKD_Benchmark rev-parse HEAD'
        if ($LASTEXITCODE -ne 0) { throw 'Remote unavailable' }
        if ($remoteHead.Trim() -ne $head) { Start-Sleep -Seconds 30; continue }
        $ack = @{head=$head; clean=$true; origin=(& git rev-parse origin/main).Trim(); ahead=0; behind=0; local_root=$ProjectRoot; timestamp=[DateTime]::UtcNow.ToString('o') } | ConvertTo-Json
        [System.IO.File]::WriteAllText($ackFile, $ack, [System.Text.UTF8Encoding]::new($false))
        & scp -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -o BatchMode=yes -o ConnectTimeout=15 -P 32514 $ackFile "${remote}:${remoteAck}.incoming" 2>&1 | Out-File -FilePath $syncLog -Append -Encoding utf8
        if ($LASTEXITCODE -ne 0) { throw 'Acknowledgement upload failed' }
        & ssh -n -T -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -o BatchMode=yes -o ConnectTimeout=15 -p 32514 $remote 'mv /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/local_sync_ack.json.incoming /root/autodl-tmp/WMKD_Benchmark_data/runs/methods_11_15/local_sync_ack.json'
        if ($LASTEXITCODE -ne 0) { throw 'Acknowledgement promotion failed' }
        $failures=0
        "$(Get-Date -Format o) synchronized $head" | Out-File -FilePath $syncLog -Append -Encoding utf8
        $shutdownFile = Join-Path $ProjectRoot 'results\methods_11_15_final_shutdown_state.json'
        if (Test-Path -LiteralPath $shutdownFile) {
            $shutdownState = Get-Content -LiteralPath $shutdownFile -Raw | ConvertFrom-Json
            if ($shutdownState.status -eq 'AUTO_SHUTDOWN_REQUESTED_BUT_PLATFORM_REJECTED') { break }
        }
    } catch {
        $failures++
        "$(Get-Date -Format o) $($_.Exception.Message)" | Out-File -FilePath $syncLog -Append -Encoding utf8
        $shutdownFile = Join-Path $ProjectRoot 'results\methods_11_15_final_shutdown_state.json'
        if ($failures -ge 3 -and (Test-Path -LiteralPath $shutdownFile)) {
            $shutdownState = Get-Content -LiteralPath $shutdownFile -Raw | ConvertFrom-Json
            if ($shutdownState.shutdown_requested) { break }
        }
    }
    Start-Sleep -Seconds 30
}
$syncLock.Dispose()

param(
    [string]$RepoPath,
    [string]$ServiceName = "",
    [string]$RestartCmd = ""
)

Set-StrictMode -Version Latest

function Write-Log {
    param([string]$Message)
    $ts = Get-Date -Format o
    Write-Host "[$ts] $Message"
}

if (-not $RepoPath) {
    Write-Log "No RepoPath provided. Usage: updater.ps1 <repoPath> [serviceName] [restartCmd]"
    exit 2
}

try {
    Write-Log "Pulling latest in $RepoPath"
    git -C $RepoPath pull 2>&1 | ForEach-Object { Write-Log $_ }
} catch {
    Write-Log "Git pull failed: $_"
    exit 3
}

if ($ServiceName) {
    try {
        Write-Log "Restarting service $ServiceName"
        Restart-Service -Name $ServiceName -Force -ErrorAction Stop
        Write-Log "Service restarted"
    } catch {
        Write-Log "Failed to restart service $ServiceName: $_"
        exit 4
    }
} elseif ($RestartCmd) {
    try {
        Write-Log "Running restart command: $RestartCmd"
        Invoke-Expression $RestartCmd
        Write-Log "Restart command executed"
    } catch {
        Write-Log "Restart command failed: $_"
        exit 5
    }
} else {
    Write-Log "No service name or restart command provided. Update completed but no restart performed."
}

Write-Log "Updater finished"
exit 0

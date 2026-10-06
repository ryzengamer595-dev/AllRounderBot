$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================="
Write-Host "       ALL-ROUNDER BOT AUTO PUSH"
Write-Host "========================================="
Write-Host ""
Write-Host "Watching for file changes..."
Write-Host "Press Ctrl + C to stop."
Write-Host ""

$folder = Get-Location

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $folder
$watcher.Filter = "*.*"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

$action = {
    $file = $Event.SourceEventArgs.FullPath

    # Git aur unnecessary files ignore
    if (
        $file -notlike "*\.git\*" -and
        $file -notlike "*\__pycache__\*" -and
        $file -notlike "*.pyc" -and
        $file -notlike "*.env"
    ) {

        Write-Host ""
        Write-Host "Change detected!"
        Write-Host "File: $file"

        Start-Sleep -Seconds 2

        git add .

        $time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

        git commit -m "Bot update $time"

        git push origin main

        Write-Host ""
        Write-Host "GitHub updated successfully!"
        Write-Host ""
    }
}

Register-ObjectEvent $watcher "Changed" -Action $action | Out-Null
Register-ObjectEvent $watcher "Created" -Action $action | Out-Null
Register-ObjectEvent $watcher "Deleted" -Action $action | Out-Null
Register-ObjectEvent $watcher "Renamed" -Action $action | Out-Null

while ($true) {
    Start-Sleep -Seconds 1
}
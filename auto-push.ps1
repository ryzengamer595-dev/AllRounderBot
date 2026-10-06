while ($true) {
    Start-Sleep -Seconds 3

    $changes = git status --porcelain

    if ($changes -ne "") {
        git add .
        git commit -m "Auto update"
        git push origin main
        Write-Host "GitHub updated!"
    }
}
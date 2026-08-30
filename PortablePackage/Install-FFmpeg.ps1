$ErrorActionPreference = "Stop"

if (Get-Command winget -ErrorAction SilentlyContinue) {
  Write-Host "Installing FFmpeg with winget..."
  winget install --id Gyan.FFmpeg.Shared --exact --accept-source-agreements --accept-package-agreements
  Write-Host "Installation completed. Restart the application."
  exit 0
}

Write-Host "winget was not found."
Write-Host "Please install FFmpeg manually and make sure ffmpeg.exe is in PATH."
Write-Host "Then run Check-Requirements.ps1 again."
exit 1

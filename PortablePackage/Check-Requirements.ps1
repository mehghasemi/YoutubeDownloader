$ErrorActionPreference = "SilentlyContinue"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$exe = Join-Path $root "YoutubeDownloader.exe"
$ffmpegLocal = Join-Path $root "ffmpeg\bin\ffmpeg.exe"
$ffmpegPath = Get-Command ffmpeg -ErrorAction SilentlyContinue

Write-Host "YoutubeDownloader portable package check"
Write-Host "----------------------------------------"
Write-Host ("Executable: " + $(if (Test-Path $exe) { "OK" } else { "MISSING" }))
if (Test-Path $ffmpegLocal) {
  Write-Host "FFmpeg: OK (bundled in package)"
} elseif ($ffmpegPath) {
  Write-Host ("FFmpeg: OK (PATH: " + $ffmpegPath.Source + ")")
} else {
  Write-Host "FFmpeg: NOT FOUND"
  Write-Host "MP4 merging and MP3 conversion may fail."
  Write-Host "Run Install-FFmpeg.ps1 as Administrator or install FFmpeg manually."
}
Write-Host ""
Write-Host "The EXE includes Python and yt-dlp; they do not need separate installation."
Read-Host "Press Enter to close"

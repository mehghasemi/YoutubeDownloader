@echo off
setlocal
cd /d "%~dp0"
if not exist "YoutubeDownloader.exe" (
  echo YoutubeDownloader.exe was not found in this folder.
  pause
  exit /b 1
)
start "" "%~dp0YoutubeDownloader.exe"
endlocal

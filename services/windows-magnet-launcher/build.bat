@echo off
echo Building windows-magnet-launcher...

go build -o magnet-launcher.exe -ldflags -H=windowsgui

if %ERRORLEVEL% EQU 0 (
    echo Build successful!
) else (
    echo Build failed!
    exit /b %ERRORLEVEL%
)

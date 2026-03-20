# Загрузчик медиафайлов - Скрипт запуска
Write-Host "Загрузчик медиафайлов" -ForegroundColor Green
Write-Host "====================" -ForegroundColor Green
Write-Host ""

# Проверка наличия Python
Write-Host "Проверка наличия Python..."
try {
    $pythonVersion = & python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Python не найден"
    }
    Write-Host "Python найден: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Ошибка: Python не найден!" -ForegroundColor Red
    Write-Host "Пожалуйста, установите Python 3.8 или выше" -ForegroundColor Yellow
    Write-Host "Скачайте с: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

# Проверка наличия yt-dlp
Write-Host "Проверка наличия yt-dlp..."
try {
    python -c "import yt_dlp" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "yt-dlp не найден"
    }
    Write-Host "yt-dlp найден" -ForegroundColor Green
} catch {
    Write-Host "yt-dlp не найден. Установка..." -ForegroundColor Yellow
    & pip install yt-dlp
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Ошибка установки yt-dlp!" -ForegroundColor Red
        Write-Host "Пожалуйста, установите вручную: pip install yt-dlp" -ForegroundColor Yellow
        Write-Host ""
        pause
        exit 1
    }
    Write-Host "yt-dlp успешно установлен" -ForegroundColor Green
}

# Запуск приложения
Write-Host "Запуск приложения..." -ForegroundColor Cyan
Write-Host ""

& python "$PSScriptRoot\main.py"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Ошибка при запуске приложения!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "Приложение завершено." -ForegroundColor Green
Write-Host "Нажмите любую клавишу для выхода..."
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
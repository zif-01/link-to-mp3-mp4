@echo off
TITLE Загрузчик медиафайлов
echo Загрузчик медиафайлов
echo ====================
echo.
echo Запуск приложения...
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ошибка: Python не найден!
    echo Пожалуйста, установите Python 3.8 или выше
    echo Скачайте с: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Проверка наличия yt-dlp
python -c "import yt_dlp" >nul 2>&1
if %errorlevel% neq 0 (
    echo Установка yt-dlp...
    pip install yt-dlp
    if %errorlevel% neq 0 (
        echo Ошибка установки yt-dlp!
        echo Пожалуйста, установите вручную: pip install yt-dlp
        echo.
        pause
        exit /b 1
    )
)

REM Запуск приложения
python "%~dp0main.py"

if %errorlevel% neq 0 (
    echo.
    echo Ошибка при запуске приложения!
    pause
    exit /b 1
)

echo.
echo Приложение завершено.
pause
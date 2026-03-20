#!/bin/bash

# Загрузчик медиафайлов - Скрипт запуска
echo "Загрузчик медиафайлов"
echo "===================="
echo ""

# Проверка наличия Python
echo "Проверка наличия Python..."
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Ошибка: Python не найден!"
    echo "Пожалуйста, установите Python 3.8 или выше"
    echo "Скачайте с: https://www.python.org/downloads/"
    echo ""
    read -p "Нажмите Enter для продолжения..."
    exit 1
fi

# Определение команды Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "Python найден: $($PYTHON_CMD --version)"

# Проверка наличия yt-dlp
echo "Проверка наличия yt-dlp..."
if ! $PYTHON_CMD -c "import yt_dlp" &> /dev/null; then
    echo "yt-dlp не найден. Установка..."
    pip install yt-dlp
    if [ $? -ne 0 ]; then
        echo "Ошибка установки yt-dlp!"
        echo "Пожалуйста, установите вручную: pip install yt-dlp"
        echo ""
        read -p "Нажмите Enter для продолжения..."
        exit 1
    fi
    echo "yt-dlp успешно установлен"
else
    echo "yt-dlp найден"
fi

# Запуск приложения
echo "Запуск приложения..."
echo ""

$PYTHON_CMD "$(dirname "$0")/main.py"

if [ $? -ne 0 ]; then
    echo ""
    echo "Ошибка при запуске приложения!"
    read -p "Нажмите Enter для продолжения..."
    exit 1
fi

echo ""
echo "Приложение завершено."
read -p "Нажмите Enter для выхода..."
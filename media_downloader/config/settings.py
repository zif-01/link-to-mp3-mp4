"""
Файл конфигурации приложения
"""
import os

# Базовые настройки приложения
APP_NAME = "Загрузчик медиафайлов"
APP_VERSION = "1.0.0"

# Настройки yt-dlp
YTDLP_DEFAULT_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'format': 'best[ext=mp4]/best',
}

# Настройки GUI
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400

# Директории
DEFAULT_DOWNLOAD_DIR = os.path.expanduser("~\\Downloads")
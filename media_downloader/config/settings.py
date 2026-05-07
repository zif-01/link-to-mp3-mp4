"""
Настройки приложения.
"""

__all__ = [
    'APP_NAME',
    'APP_VERSION',
    'YTDLP_DEFAULT_OPTS',
    'DEFAULT_DOWNLOAD_DIR',
]


APP_NAME: str = "Загрузчик медиафайлов"
APP_VERSION: str = "1.0.0"

YTDLP_DEFAULT_OPTS: dict = {
    'quiet': True,
    'no_warnings': True,
    'format': 'best[ext=mp4]/best',
}

DEFAULT_DOWNLOAD_DIR: str = None  # Определяется динамически

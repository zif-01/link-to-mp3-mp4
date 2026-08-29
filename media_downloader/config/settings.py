__all__ = [
    'APP_NAME',
    'APP_VERSION',
    'YTDLP_DEFAULT_OPTS',
    'DEFAULT_DOWNLOAD_DIR',
    'DEFAULT_PROXY_ENABLED',
    'DEFAULT_PROXY_PROTOCOL',
    'DEFAULT_PROXY_HOST',
    'DEFAULT_PROXY_PORT',
]


APP_NAME: str = "Загрузчик медиафайлов"
APP_VERSION: str = "1.0.0"

YTDLP_DEFAULT_OPTS: dict = {
    'quiet': True,
    'no_warnings': True,
    'format': 'best[ext=mp4]/best',
}

DEFAULT_DOWNLOAD_DIR: str = None

DEFAULT_PROXY_ENABLED: bool = False
DEFAULT_PROXY_PROTOCOL: str = "socks5"
DEFAULT_PROXY_HOST: str = "127.0.0.1"
DEFAULT_PROXY_PORT: int = 9050

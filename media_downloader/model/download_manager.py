"""
Менеджер загрузки медиафайлов с использованием yt-dlp
"""
import yt_dlp
import os
import threading
from typing import Callable, Optional
from ..model.download_model import DownloadModel


class DownloadManager:
    """
    Менеджер для загрузки медиафайлов через yt-dlp
    """

    def __init__(self):
        """
        Инициализация менеджера загрузки
        """
        self.ydl_opts = {}
        self.current_download_thread = None
        self.is_cancelled = False

    def configure_download(self, model: DownloadModel) -> dict:
        """
        Конфигурация параметров yt-dlp на основе модели

        Args:
            model (DownloadModel): Модель данных загрузки

        Returns:
            dict: Параметры для yt-dlp
        """
        # Базовые параметры
        ydl_opts = {
            'outtmpl': os.path.join(model.save_directory, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'logger': self._Logger(),
        }

        # Настройка параметров в зависимости от формата
        if model.format_type == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            })
        else:  # mp4
            ydl_opts.update({
                'format': 'best[ext=mp4]/best'
            })

        return ydl_opts

    def download_media(self, model: DownloadModel, progress_callback: Optional[Callable] = None) -> bool:
        """
        Загрузка медиафайла в отдельном потоке

        Args:
            model (DownloadModel): Модель данных загрузки
            progress_callback (Callable, optional): Функция обратного вызова для прогресса

        Returns:
            bool: True если загрузка успешна, False в случае ошибки
        """
        self.is_cancelled = False
        model.update_status("downloading")

        def download_thread():
            try:
                ydl_opts = self.configure_download(model)

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Сохраняем callback для использования в progress_hook
                    self._progress_callback = progress_callback

                    # Получаем информацию о видео
                    info = ydl.extract_info(model.url, download=False)
                    model.filename = info.get('title', 'unknown')

                    # Загружаем видео
                    if not self.is_cancelled:
                        ydl.download([model.url])

                if not self.is_cancelled:
                    model.update_status("completed")
                    model.update_progress(100)
                    if progress_callback:
                        progress_callback(model)

            except Exception as e:
                if not self.is_cancelled:
                    model.update_status("failed")
                    model.filename = str(e)
                    if progress_callback:
                        progress_callback(model)
                return False

            return True

        # Запуск загрузки в отдельном потоке
        self.current_download_thread = threading.Thread(target=download_thread, daemon=True)
        self.current_download_thread.start()
        return True

    def cancel_download(self):
        """
        Отмена текущей загрузки
        """
        self.is_cancelled = True
        if self.current_download_thread and self.current_download_thread.is_alive():
            # Примечание: мягкая отмена, так как мы не можем принудительно остановить yt-dlp
            pass

    def _progress_hook(self, data):
        """
        Обработчик прогресса от yt-dlp

        Args:
            data (dict): Данные о прогрессе загрузки
        """
        if self.is_cancelled:
            raise yt_dlp.DownloadCancelled("Download was cancelled")

        if data['status'] == 'downloading' and hasattr(self, '_progress_callback'):
            progress_str = data.get('_percent_str', '0%')
            # Извлечение числового значения из строки прогресса
            try:
                progress = float(progress_str.replace('%', '').strip())
            except ValueError:
                progress = 0

            # Обновляем модель через callback если он есть
            if self._progress_callback:
                # Передаем данные прогресса в callback
                progress_data = {
                    'progress': progress,
                    'speed': data.get('_speed_str', ''),
                    'eta': data.get('_eta_str', '')
                }
                self._progress_callback(progress_data)

    class _Logger:
        """
        Внутренний класс для логирования yt-dlp
        """
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(f"Ошибка yt-dlp: {msg}")
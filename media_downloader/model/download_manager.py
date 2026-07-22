"""
Менеджер загрузки медиафайлов с использованием yt-dlp.
"""

__all__ = ['DownloadManager']

import os
import yt_dlp # type: ignore
import urllib.parse
import threading
from typing import Optional, Callable
from ..model.download_model import DownloadModel


class DownloadManager:
    """Отвечает за процессы загрузки и отмены."""

    def __init__(self) -> None:
        """Инициализация менеджера."""
        self.ydl_opts: dict = {}
        self.current_download_thread: Optional[threading.Thread] = None
        self.is_cancelled: bool = False

    def configure_download(self, model: DownloadModel) -> dict:
        """
        Конфигурация опций для yt-dlp.

        Args:
            model: Модель с данными о загрузке

        Returns:
            Словарь опций yt-dlp
        """
        ydl_opts: dict = {
            'outtmpl': os.path.join(
                model.save_directory, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'logger': self._Logger(),
        }

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

    def download_media(
        self,
        model: DownloadModel,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        Запускает загрузку медиафайла.

        Args:
            model: Модель с данными о загрузке
            progress_callback: Обратный вызов для обновления прогресса

        Returns:
            True если загрузка началась
        """
        self.is_cancelled = False
        model.update_status("downloading")

        def download_thread() -> None:
            try:
                ydl_opts = self.configure_download(model)

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(model.url, download=False)
                    model.filename = info.get('title', 'unknown')

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
                return

        self.current_download_thread = threading.Thread(
            target=download_thread,
            daemon=True
        )
        self.current_download_thread.start()
        return True

    def cancel_download(self) -> None:
        """Отменяет текущую загрузку."""
        self.is_cancelled = True
        if self.current_download_thread and self.current_download_thread.is_alive():
            self.current_download_thread.join()

    def _progress_hook(self, data: dict) -> None:
        """
        Обратный вызов для обновления прогресса.

        Args:
            data: Данные о прогрессе
        """
        if self.is_cancelled:
            raise yt_dlp.DownloadCancelled("Download was cancelled")

        if (
            data['status'] == 'downloading'
            and hasattr(self, '_progress_callback')
        ):
            progress_str = data.get('_percent_str', '0%')

            try:
                progress = float(progress_str.replace('%', '').strip())
            except ValueError:
                progress = 0

            if self._progress_callback:
                progress_data = {
                    'progress': progress,
                    'speed': data.get('_speed_str', ''),
                    'eta': data.get('_eta_str', '')
                }
                self._progress_callback(progress_data)

    class _Logger:
        """Молчаливый логгер для yt-dlp."""

        def debug(self, msg: str) -> None:
            pass

        def warning(self, msg: str) -> None:
            pass

        def error(self, msg: str) -> None:
            print(f"Ошибка yt-dlp: {msg}")

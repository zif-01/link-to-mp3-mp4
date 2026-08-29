__all__ = ['DownloadManager']

import os
import yt_dlp
import urllib.parse
import threading
from typing import Optional, Callable
from ..model.download_model import DownloadModel


class DownloadManager:

    def __init__(self) -> None:
        self.ydl_opts: dict = {}
        self.current_download_thread: Optional[threading.Thread] = None
        self.is_cancelled: bool = False
        self.proxy_url: Optional[str] = None

    def configure_download(self, model: DownloadModel) -> dict:
        ydl_opts: dict = {
            'outtmpl': os.path.join(
                model.save_directory, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'logger': self._Logger(),
        }

        if self.proxy_url:
            ydl_opts['proxy'] = self.proxy_url

        if model.format_type == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            })
        else:
            ydl_opts.update({
                'format': 'best[ext=mp4]/best'
            })

        return ydl_opts

    def download_media(
        self,
        model: DownloadModel,
        progress_callback: Optional[Callable] = None
    ) -> bool:
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
        self.is_cancelled = True
        if self.current_download_thread and self.current_download_thread.is_alive():
            self.current_download_thread.join()

    def _progress_hook(self, data: dict) -> None:
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

        def debug(self, msg: str) -> None:
            pass

        def warning(self, msg: str) -> None:
            pass

        def error(self, msg: str) -> None:
            print(f"Ошибка yt-dlp: {msg}")

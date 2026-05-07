"""
Контроллер приложения — связующее между видом и моделью.
"""

__all__ = ['AppController']

from typing import Optional, Callable
import os
from ..model.download_model import DownloadModel
from ..model.download_manager import DownloadManager


class AppController:
    """Управляет состоянием и взаимодействием между компонентами."""

    def __init__(self, view: Optional['MainWindow'] = None) -> None:
        """
        Инициализация контроллера.

        Args:
            view: Ссылка на главное окно для обратных вызовов
        """
        self.view: Optional[MainWindow] = view
        self.download_manager: DownloadManager = DownloadManager()
        self.current_model: Optional[DownloadModel] = None

    def handle_download_request(
        self, url: str, format_type: str, save_dir: str
    ) -> bool:
        """
        Обрабатывает запрос на загрузку.

        Args:
            url: URL медиафайла
            format_type: 'mp3' или 'mp4'
            save_dir: Директория для сохранения

        Returns:
            True если загрузка началась, False если валидация провалилась
        """
        if not self.validate_inputs(url, save_dir):
            return False

        self.current_model = DownloadModel(url, format_type, save_dir)

        self.download_manager.download_media(
            self.current_model,
            self._progress_callback
        )

        return True

    def handle_cancel_request(self) -> None:
        """Отменяет текущую загрузку."""
        self.download_manager.cancel_download()
        if self.current_model:
            self.current_model.update_status("failed")
            self.current_model.filename = "Загрузка отменена пользователем"

    def validate_inputs(self, url: str, save_dir: str) -> bool:
        """
        Валидация входных данных.

        Args:
            url: URL для проверки
            save_dir: Путь для сохранения

        Returns:
            True если все данные валидны
        """
        if (
            not url
            or not isinstance(url, str)
            or len(url.strip()) == 0
        ):
            if self.view:
                self.view.show_error("Введите корректный URL")
            return False

        if (
            not save_dir
            or not isinstance(save_dir, str)
        ):
            if self.view:
                self.view.show_error("Выберите директорию для сохранения")
            return False

        if not os.path.exists(save_dir):
            if self.view:
                self.view.show_error("Выбранная директория не существует")
            return False

        if not os.path.isdir(save_dir):
            if self.view:
                self.view.show_error("Выбранный путь не является директорией")
            return False

        return True

    def _progress_callback(self, progress_data: dict) -> None:
        """
        Обратный вызов при обновлении прогресса.

        Args:
            progress_data: Данные о прогрессе
        """
        if self.current_model and self.view:
            if isinstance(progress_data, dict):
                self.current_model.update_progress(
                    int(progress_data.get('progress', 0))
                )
                self.current_model.speed = progress_data.get('speed', '')
                self.current_model.eta = progress_data.get('eta', '')
            elif isinstance(progress_data, DownloadModel):
                pass  # Игнорируем старые формат обратного вызова

            # Обновление GUI
            self.view.update_progress(self.current_model)

    def get_current_model(self) -> Optional[DownloadModel]:
        """Возвращает текущую модель загрузки."""
        return self.current_model

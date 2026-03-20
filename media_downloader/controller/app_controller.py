"""
Контроллер приложения для управления взаимодействием между моделью и представлением
"""
import os
import urllib.parse
from typing import Optional, Callable
from ..model.download_model import DownloadModel
from ..model.download_manager import DownloadManager


class AppController:
    """
    Контроллер основного приложения
    """

    def __init__(self, view=None):
        """
        Инициализация контроллера

        Args:
            view: Объект представления (GUI)
        """
        self.view = view
        self.download_manager = DownloadManager()
        self.current_model: Optional[DownloadModel] = None

    def handle_download_request(self, url: str, format_type: str, save_dir: str) -> bool:
        """
        Обработка запроса на загрузку

        Args:
            url (str): URL для скачивания
            format_type (str): Тип формата ('mp3' или 'mp4')
            save_dir (str): Директория для сохранения

        Returns:
            bool: True если запрос принят, False если есть ошибки
        """
        # Валидация входных данных
        if not self.validate_inputs(url, save_dir):
            return False

        # Создание модели данных
        self.current_model = DownloadModel(url, format_type, save_dir)

        # Запуск загрузки
        self.download_manager.download_media(
            self.current_model,
            self._progress_callback
        )

        return True

    def handle_cancel_request(self):
        """
        Обработка запроса на отмену загрузки
        """
        self.download_manager.cancel_download()
        if self.current_model:
            self.current_model.update_status("failed")
            self.current_model.filename = "Загрузка отменена пользователем"

    def validate_inputs(self, url: str, save_dir: str) -> bool:
        """
        Валидация входных данных

        Args:
            url (str): URL для проверки
            save_dir (str): Директория для проверки

        Returns:
            bool: True если данные валидны
        """
        # Проверка URL
        if not url or not isinstance(url, str) or len(url.strip()) == 0:
            if self.view:
                self.view.show_error("Введите корректный URL")
            return False

        # Проверка директории сохранения
        if not save_dir or not isinstance(save_dir, str):
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

    def _progress_callback(self, progress_data):
        """
        Обратный вызов для обновления прогресса

        Args:
            progress_data: Данные о прогрессе загрузки
        """
        if self.current_model and self.view:
            if isinstance(progress_data, dict):
                # Обновление прогресса из менеджера загрузки
                self.current_model.update_progress(int(progress_data.get('progress', 0)))
                self.current_model.speed = progress_data.get('speed', '')
                self.current_model.eta = progress_data.get('eta', '')
            elif isinstance(progress_data, DownloadModel):
                # Обновление статуса из менеджера загрузки
                pass

            # Обновление GUI
            self.view.update_progress(self.current_model)

    def get_current_model(self) -> Optional[DownloadModel]:
        """
        Получение текущей модели данных

        Returns:
            DownloadModel: Текущая модель или None
        """
        return self.current_model
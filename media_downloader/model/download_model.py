"""
Модель данных для задач загрузки медиафайлов.
"""

__all__ = ['DownloadModel']


class DownloadModel:
    """Модель данных для одной задачи загрузки."""

    def __init__(
        self, url: str, format_type: str, save_directory: str
    ) -> None:
        """
        Инициализация модели загрузки.

        Args:
            url: Ссылка на медиафайл
            format_type: 'mp3' или 'mp4'
            save_directory: Путь для сохранения файла
        """
        self.url = url
        self.format_type = format_type
        self.save_directory = save_directory
        self.status: str = "pending"
        self.progress: int = 0
        self.filename: str = ""
        self.filesize: int = 0
        self.speed: str = ""
        self.eta: str = ""

    def update_progress(self, progress: int) -> None:
        """Обновление прогресса загрузки."""
        self.progress = max(0, min(100, progress))

    def update_status(self, status: str) -> None:
        """Установление статуса загрузки."""
        valid_statuses = ["pending", "downloading", "completed", "failed"]
        if status in valid_statuses:
            self.status = status

    def get_status_display(self) -> str:
        """Возвращает отображаемый текст статуса."""
        status_texts = {
            "pending": "Ожидание",
            "downloading": "Загрузка",
            "completed": "Завершено",
            "failed": "Ошибка"
        }
        return status_texts.get(self.status, self.status)

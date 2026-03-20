"""
Модель данных для загрузки медиафайлов
"""


class DownloadModel:
    """
    Модель данных для хранения информации о загрузке
    """

    def __init__(self, url: str, format_type: str, save_directory: str):
        """
        Инициализация модели данных загрузки

        Args:
            url (str): URL для скачивания
            format_type (str): Тип формата ('mp3' или 'mp4')
            save_directory (str): Директория для сохранения файла
        """
        self.url = url
        self.format_type = format_type  # 'mp3' или 'mp4'
        self.save_directory = save_directory
        self.status = "pending"  # pending, downloading, completed, failed
        self.progress = 0  # 0-100
        self.filename = ""
        self.filesize = 0
        self.speed = ""
        self.eta = ""

    def update_progress(self, progress: int):
        """
        Обновление прогресса загрузки

        Args:
            progress (int): Процент выполнения (0-100)
        """
        self.progress = max(0, min(100, progress))

    def update_status(self, status: str):
        """
        Обновление статуса загрузки

        Args:
            status (str): Новый статус загрузки
        """
        valid_statuses = ["pending", "downloading", "completed", "failed"]
        if status in valid_statuses:
            self.status = status

    def get_status_display(self) -> str:
        """
        Получение отображаемого текста статуса

        Returns:
            str: Текстовое описание статуса
        """
        status_texts = {
            "pending": "Ожидание",
            "downloading": "Загрузка",
            "completed": "Завершено",
            "failed": "Ошибка"
        }
        return status_texts.get(self.status, self.status)
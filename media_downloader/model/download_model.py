__all__ = ['DownloadModel']


class DownloadModel:

    def __init__(
        self, url: str, format_type: str, save_directory: str
    ) -> None:
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
        self.progress = max(0, min(100, progress))

    def update_status(self, status: str) -> None:
        valid_statuses = ["pending", "downloading", "completed", "failed"]
        if status in valid_statuses:
            self.status = status

    def get_status_display(self) -> str:
        status_texts = {
            "pending": "Ожидание",
            "downloading": "Загрузка",
            "completed": "Завершено",
            "failed": "Ошибка"
        }
        return status_texts.get(self.status, self.status)

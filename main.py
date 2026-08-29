import sys
import os

from media_downloader.view.main_window import MainWindow
from media_downloader.controller.app_controller import AppController
import tkinter as tk
from tkinter import messagebox


def main() -> None:
    try:
        controller = AppController()
        app = MainWindow(controller)
        controller.view = app

        app.mainloop()

    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        messagebox.showerror("Ошибка", f"Не удалось запустить приложение: {e}")


if __name__ == "__main__":
    main()

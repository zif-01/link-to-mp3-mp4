"""
Точка входа в приложение для скачивания медиафайлов
"""
import sys
import os

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from media_downloader.view.main_window import MainWindow
from media_downloader.controller.app_controller import AppController
import tkinter as tk
from tkinter import messagebox


def main():
    """
    Основная функция запуска приложения
    """
    try:
        # Создание контроллера
        controller = AppController()

        # Создание главного окна с передачей контроллера
        app = MainWindow(controller)
        controller.view = app

        # Запуск главного цикла обработки событий
        app.mainloop()

    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        messagebox.showerror("Ошибка", f"Не удалось запустить приложение: {e}")


if __name__ == "__main__":
    main()
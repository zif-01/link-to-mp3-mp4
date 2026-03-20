"""
Главное окно приложения с графическим интерфейсом
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from typing import TYPE_CHECKING
import os

if TYPE_CHECKING:
    from media_downloader.controller.app_controller import AppController
    from media_downloader.model.download_model import DownloadModel


class MainWindow(tk.Tk):
    """
    Главное окно приложения для скачивания медиафайлов
    """

    def __init__(self, controller: 'AppController'):
        """
        Инициализация главного окна

        Args:
            controller (AppController): Контроллер приложения
        """
        super().__init__()
        self.controller = controller

        # Настройка окна
        self.title("Загрузчик медиафайлов")
        self.geometry("600x400")
        self.resizable(True, True)

        # Переменные для хранения значений
        self.url_var = tk.StringVar()
        self.format_var = tk.StringVar(value="mp4")
        self.directory_var = tk.StringVar()

        # Создание виджетов
        self.create_widgets()

        # Центрирование окна
        self.center_window()

    def center_window(self):
        """
        Центрирование окна на экране
        """
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """
        Создание всех виджетов окна
        """
        # Создание основного фрейма
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка сетки
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Заголовок
        title_label = ttk.Label(main_frame, text="Загрузчик медиафайлов", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Поле ввода URL
        ttk.Label(main_frame, text="URL видео:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))

        # Выбор формата
        ttk.Label(main_frame, text="Формат:").grid(row=2, column=0, sticky=tk.W, pady=5)
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Radiobutton(format_frame, text="MP4 (Видео)", variable=self.format_var, value="mp4").pack(side=tk.LEFT)
        ttk.Radiobutton(format_frame, text="MP3 (Аудио)", variable=self.format_var, value="mp3").pack(side=tk.LEFT, padx=(20, 0))

        # Выбор директории сохранения
        ttk.Label(main_frame, text="Сохранить в:").grid(row=3, column=0, sticky=tk.W, pady=5)
        directory_frame = ttk.Frame(main_frame)
        directory_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.directory_entry = ttk.Entry(directory_frame, textvariable=self.directory_var, state="readonly")
        self.directory_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.browse_button = ttk.Button(directory_frame, text="Обзор...", command=self.browse_directory)
        self.browse_button.pack(side=tk.RIGHT, padx=(5, 0))

        # Прогресс бар
        ttk.Label(main_frame, text="Прогресс:").grid(row=4, column=0, sticky=tk.W, pady=(20, 5))
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Статус
        self.status_label = ttk.Label(main_frame, text="Готово к загрузке", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=20)

        self.download_button = ttk.Button(button_frame, text="Загрузить", command=self.start_download)
        self.download_button.pack(side=tk.LEFT, padx=(0, 10))

        self.cancel_button = ttk.Button(button_frame, text="Отмена", command=self.cancel_download, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT)

        # Установка начальной директории
        home_dir = os.path.expanduser("~")
        self.directory_var.set(home_dir)
        self.directory_entry.config(state="normal")
        self.directory_entry.delete(0, tk.END)
        self.directory_entry.insert(0, home_dir)
        self.directory_entry.config(state="readonly")

    def browse_directory(self):
        """
        Открытие диалога выбора директории
        """
        directory = filedialog.askdirectory(title="Выберите директорию для сохранения")
        if directory:
            self.directory_var.set(directory)
            # Обновляем отображение
            self.directory_entry.config(state="normal")
            self.directory_entry.delete(0, tk.END)
            self.directory_entry.insert(0, directory)
            self.directory_entry.config(state="readonly")

    def start_download(self):
        """
        Запуск процесса загрузки
        """
        url = self.url_var.get().strip()
        format_type = self.format_var.get()
        save_dir = self.directory_var.get()

        if not url:
            self.show_error("Введите URL для загрузки")
            return

        if not save_dir or save_dir == ".":
            # Если директория не выбрана, используем текущую
            save_dir = "."

        # Блокируем кнопки во время загрузки
        self.download_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.url_entry.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.DISABLED)

        # Запуск загрузки через контроллер
        success = self.controller.handle_download_request(url, format_type, save_dir)

        if not success:
            # Разблокируем кнопки если загрузка не началась
            self.download_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            self.url_entry.config(state=tk.NORMAL)
            self.browse_button.config(state=tk.NORMAL)

    def cancel_download(self):
        """
        Отмена процесса загрузки
        """
        self.controller.handle_cancel_request()
        self.reset_ui_state()

    def reset_ui_state(self):
        """
        Сброс состояния интерфейса
        """
        self.download_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.url_entry.config(state=tk.NORMAL)
        self.browse_button.config(state=tk.NORMAL)

    def update_progress(self, model: 'DownloadModel'):
        """
        Обновление прогресса загрузки в интерфейсе

        Args:
            model (DownloadModel): Модель данных загрузки
        """
        # Обновление прогресс бара
        self.progress_var.set(model.progress)

        # Обновление статуса
        status_text = model.get_status_display()
        if model.status == "downloading":
            if model.speed and model.eta:
                status_text += f" - {model.progress:.1f}% ({model.speed}, ETA: {model.eta})"
            elif model.speed:
                status_text += f" - {model.progress:.1f}% ({model.speed})"
            else:
                status_text += f" - {model.progress:.1f}%"

        if model.filename:
            status_text += f"\nФайл: {model.filename}"

        self.status_label.config(text=status_text)

        # Обновление интерфейса
        self.update_idletasks()

        # Если загрузка завершена или произошла ошибка, разблокируем кнопки
        if model.status in ["completed", "failed"]:
            self.reset_ui_state()

            # Показываем сообщение об успехе или ошибке
            if model.status == "completed":
                self.show_success(f"Загрузка завершена успешно!\nФайл: {model.filename}")
            elif model.status == "failed":
                self.show_error(f"Ошибка загрузки: {model.filename}")

    def show_error(self, message: str):
        """
        Отображение сообщения об ошибке

        Args:
            message (str): Текст сообщения об ошибке
        """
        messagebox.showerror("Ошибка", message)

    def show_success(self, message: str):
        """
        Отображение сообщения об успехе

        Args:
            message (str): Текст сообщения об успехе
        """
        messagebox.showinfo("Успех", message)

    def show_warning(self, message: str):
        """
        Отображение предупреждения

        Args:
            message (str): Текст предупреждения
        """
        messagebox.showwarning("Предупреждение", message)
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from typing import TYPE_CHECKING
from media_downloader.utils.preference_manager import PreferenceManager

if TYPE_CHECKING:
    from media_downloader.controller.app_controller import AppController
    from media_downloader.model.download_model import DownloadModel


def _get_resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class EntryWithContextMenu(ttk.Entry):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._create_context_menu()
        self._bind_events()

    def _create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Вырезать", command=self._cut)
        self.context_menu.add_command(label="Копировать", command=self._copy)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Вставить", command=self._paste)

    def _bind_events(self):
        self.bind("<Button-3>", self._show_context_menu)
        self.bind("<Button-2>", self._show_context_menu)
        self.bind("<KeyPress>", self._handle_key_press)
        self.bind("<Control-a>", self._select_all)
        self.bind("<Alt-a>", self._select_all)
        self.bind("<Shift-Home>", self._select_to_home)
        self.bind("<Shift-End>", self._select_to_end)

    def _handle_key_press(self, event):
        ctrl = (event.state & 0x4) != 0

        if event.keycode == 86 and ctrl:
            self._paste()
            return "break"
        elif event.keycode == 67 and ctrl:
            self._copy()
            return "break"
        elif event.keycode == 88 and ctrl:
            self._cut()
            return "break"

    def _show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _cut(self):
        self.event_generate("<<Cut>>")

    def _copy(self):
        self.event_generate("<<Copy>>")

    def _paste(self):
        self.event_generate("<<Paste>>")

    def _select_all(self, event):
        self.select_range(0, tk.END)
        return "break"

    def _select_to_home(self, event):
        try:
            current_pos = self.index(tk.INSERT)
            self.select_range(0, current_pos)
        except tk.TclError:
            pass
        return "break"

    def _select_to_end(self, event):
        try:
            current_pos = self.index(tk.INSERT)
            self.select_range(current_pos, tk.END)
        except tk.TclError:
            pass
        return "break"


class MainWindow(tk.Tk):

    def __init__(self, controller: 'AppController'):
        super().__init__()
        self.controller = controller

        self.title("LTMP")

        try:
            icon_path = _get_resource_path("icon.ico")
            self.iconbitmap(icon_path)
        except tk.TclError:
            pass

        self.geometry("600x400")
        self.resizable(True, True)

        self.url_var = tk.StringVar()
        self.format_var = tk.StringVar(value="mp4")
        self.directory_var = tk.StringVar()

        self.proxy_enabled_var = tk.BooleanVar(value=False)
        self.proxy_protocol_var = tk.StringVar(value="socks5")
        self.proxy_host_var = tk.StringVar(value="127.0.0.1")
        self.proxy_port_var = tk.StringVar(value="9050")

        self.create_widgets()

        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def reset_ui_state(self):
        self.download_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.url_entry.config(state=tk.NORMAL)
        self.browse_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_label.config(text="Готово к загрузке")
        self.update_idletasks()

    def create_widgets(self):
        self.pref_manager = PreferenceManager()

        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        title_label = ttk.Label(main_frame, text="Загрузчик медиафайлов", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        ttk.Label(main_frame, text="URL видео:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.url_entry = EntryWithContextMenu(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))

        ttk.Label(main_frame, text="Формат:").grid(row=2, column=0, sticky=tk.W, pady=5)
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Radiobutton(format_frame, text="MP4 (Видео)", variable=self.format_var, value="mp4").pack(side=tk.LEFT)
        ttk.Radiobutton(format_frame, text="MP3 (Аудио)", variable=self.format_var, value="mp3").pack(side=tk.LEFT, padx=(20, 0))

        ttk.Label(main_frame, text="Сохранить в:").grid(row=3, column=0, sticky=tk.W, pady=5)
        directory_frame = ttk.Frame(main_frame)
        directory_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.directory_entry = ttk.Entry(directory_frame, textvariable=self.directory_var)
        self.directory_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.directory_entry.bind("<FocusOut>", self.on_directory_change)

        self.browse_button = ttk.Button(directory_frame, text="Обзор...", command=self.browse_directory)
        self.browse_button.pack(side=tk.RIGHT, padx=(5, 0))

        self.recent_dir_var = tk.StringVar()
        self.recent_dir_combo = ttk.Combobox(directory_frame, textvariable=self.recent_dir_var, state="readonly", width=20)
        self.recent_dir_combo.pack(side=tk.RIGHT, padx=(5, 0))
        self.recent_dir_combo.bind("<<ComboboxSelected>>", self.on_recent_dir_selected)
        recent_dirs = self.pref_manager.get_recent_directories()
        self.recent_dir_combo['values'] = recent_dirs

        proxy_frame = ttk.LabelFrame(main_frame, text="Proxy", padding="5")
        proxy_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.proxy_enabled_var = tk.BooleanVar(value=self.pref_manager.get("proxy_enabled", False))
        ttk.Checkbutton(proxy_frame, text="Использовать proxy", variable=self.proxy_enabled_var).grid(row=0, column=0, columnspan=2, sticky=tk.W)

        ttk.Label(proxy_frame, text="Протокол:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.proxy_protocol_combo = ttk.Combobox(proxy_frame, textvariable=self.proxy_protocol_var, values=["http", "https", "socks4", "socks5"], state="readonly", width=10)
        self.proxy_protocol_combo.grid(row=1, column=1, sticky=tk.W, padx=(0, 5))
        self.proxy_protocol_var.set(self.pref_manager.get("proxy_protocol", "socks5"))

        ttk.Label(proxy_frame, text="Host:").grid(row=1, column=2, sticky=tk.W, padx=(10, 5))
        self.proxy_host_entry = ttk.Entry(proxy_frame, textvariable=self.proxy_host_var, width=15)
        self.proxy_host_entry.grid(row=1, column=3, sticky=tk.W, padx=(0, 5))
        self.proxy_host_var.set(self.pref_manager.get("proxy_host", "127.0.0.1"))

        ttk.Label(proxy_frame, text="Порт:").grid(row=1, column=4, sticky=tk.W, padx=(10, 5))
        self.proxy_port_entry = ttk.Entry(proxy_frame, textvariable=self.proxy_port_var, width=8)
        self.proxy_port_entry.grid(row=1, column=5, sticky=tk.W, padx=(0, 5))
        self.proxy_port_var.set(str(self.pref_manager.get("proxy_port", 9050)))

        ttk.Label(main_frame, text="Прогресс:").grid(row=5, column=0, sticky=tk.W, pady=(20, 5))
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.status_label = ttk.Label(main_frame, text="Готово к загрузке", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=3, pady=20)

        self.download_button = ttk.Button(button_frame, text="Загрузить", command=self.start_download)
        self.download_button.pack(side=tk.LEFT, padx=(0, 10))

        self.cancel_button = ttk.Button(button_frame, text="Отмена", command=self.cancel_download, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT)

        last_dir = self.pref_manager.get("last_directory", os.path.expanduser("~"))
        self.directory_var.set(last_dir)

        recent_dirs = self.pref_manager.get_recent_directories()
        if hasattr(self, 'recent_dir_combo'):
            self.recent_dir_combo['values'] = recent_dirs

    def get_proxy_url(self) -> str:
        if self.proxy_enabled_var.get():
            protocol = self.proxy_protocol_var.get()
            host = self.proxy_host_var.get()
            port = self.proxy_port_var.get()
            return f"{protocol}://{host}:{port}"
        return ""

    def save_proxy_settings(self) -> None:
        self.pref_manager.set("proxy_enabled", self.proxy_enabled_var.get())
        self.pref_manager.set("proxy_protocol", self.proxy_protocol_var.get())
        self.pref_manager.set("proxy_host", self.proxy_host_var.get())
        self.pref_manager.set("proxy_port", int(self.proxy_port_var.get()))

    def browse_directory(self):
        directory = filedialog.askdirectory(title="Выберите директорию для сохранения")
        if directory:
            self.directory_var.set(directory)
            self.pref_manager.set("last_directory", directory)
            self.pref_manager.add_recent_directory(directory)
            recent_dirs = self.pref_manager.get_recent_directories()
            if hasattr(self, 'recent_dir_combo'):
                self.recent_dir_combo['values'] = recent_dirs

    def start_download(self):
        url = self.url_var.get().strip()
        format_type = self.format_var.get()
        save_dir = self.directory_var.get()

        if not url:
            self.show_error("Введите URL для загрузки")
            return

        if not save_dir or save_dir == ".":
            save_dir = "."

        self.download_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.url_entry.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.DISABLED)

        self.save_proxy_settings()

        proxy_url = self.get_proxy_url()

        success = self.controller.handle_download_request(url, format_type, save_dir, proxy_url)

        if not success:
            self.download_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            self.url_entry.config(state=tk.NORMAL)
            self.browse_button.config(state=tk.NORMAL)

    def cancel_download(self):
        self.controller.handle_cancel_request()
        self.reset_ui_state()

    def on_recent_dir_selected(self, event):
        selected = self.recent_dir_var.get()
        if selected:
            self.directory_var.set(selected)
            self.pref_manager.set("last_directory", selected)
            self.pref_manager.add_recent_directory(selected)
            recent_dirs = self.pref_manager.get_recent_directories()
            if hasattr(self, 'recent_dir_combo'):
                self.recent_dir_combo['values'] = recent_dirs

    def on_directory_change(self, event):
        directory = self.directory_var.get()
        if directory:
            if os.path.exists(directory) and os.path.isdir(directory):
                self.pref_manager.set("last_directory", directory)
                self.pref_manager.add_recent_directory(directory)
                recent_dirs = self.pref_manager.get_recent_directories()
                if hasattr(self, 'recent_dir_combo'):
                    self.recent_dir_combo['values'] = recent_dirs
            else:
                self.show_warning("Указанная директория не существует")

    def update_progress(self, model: 'DownloadModel'):
        self.progress_var.set(model.progress)

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

        self.update_idletasks()

        if model.status in ["completed", "failed"]:
            self.reset_ui_state()

            if model.status == "completed":
                self.show_success(f"Загрузка завершена успешно!\nФайл: {model.filename}")
            elif model.status == "failed":
                self.show_error(f"Ошибка загрузки: {model.filename}")

    def show_error(self, message: str):
        messagebox.showerror("Ошибка", message)

    def show_success(self, message: str):
        messagebox.showinfo("Успех", message)

    def show_warning(self, message: str):
        messagebox.showwarning("Предупреждение", message)

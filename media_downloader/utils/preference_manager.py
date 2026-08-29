__all__ = ['PreferenceManager']

import os
import json
import platform
from typing import List, Any


class PreferenceManager:

    def __init__(self, app_name: str = "MediaDownloader") -> None:
        self.app_name = app_name
        self.preferences_file = self._get_preferences_path()
        self.preferences: dict = self._load_preferences()

    def _get_preferences_path(self) -> str:
        system = platform.system()
        if system == "Windows":
            base_path = os.environ.get('APPDATA') or os.path.expanduser(
                r'~\AppData\Roaming')
        elif system == "Darwin":
            base_path = os.path.expanduser('~/Library/Application Support')
        else:
            base_path = os.environ.get(
                'XDG_CONFIG_HOME') or os.path.expanduser('~/.config')

        app_path = os.path.join(base_path, self.app_name)
        os.makedirs(app_path, exist_ok=True)
        return os.path.join(app_path, 'preferences.json')

    def _load_preferences(self) -> dict:
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def get(self, key: str, default: Any = None) -> Any:
        return self.preferences.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.preferences[key] = value
        self._save_preferences()

    def _save_preferences(self) -> None:
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
        except IOError:
            pass

    def add_recent_directory(
        self, directory: str, max_history: int = 10
    ) -> None:
        recent_dirs: List[str] = self.get('recent_directories', [])

        if directory in recent_dirs:
            recent_dirs.remove(directory)

        recent_dirs.insert(0, directory)

        if len(recent_dirs) > max_history:
            recent_dirs = recent_dirs[:max_history]

        self.set('recent_directories', recent_dirs)

    def get_recent_directories(self) -> List[str]:
        return self.get('recent_directories', [])

    def clear_recent_directories(self) -> None:
        self.set('recent_directories', [])

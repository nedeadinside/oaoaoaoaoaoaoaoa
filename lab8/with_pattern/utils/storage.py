import os
import json
from utils import handle_errors


class Storage:
    """Класс для управления хранением данных: настройки, закладки, сессия"""

    def __init__(self, settings_dir=".settings"):
        self.settings_dir = settings_dir

        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir)

        self.settings_file = os.path.join(settings_dir, "settings.json")
        self.bookmarks_file = os.path.join(settings_dir, "bookmarks.json")
        self.session_file = os.path.join(settings_dir, "session.json")

        self.settings = {"font_size": 12, "theme": "light"}
        self.bookmarks = []
        self.session = {}

        # Загружаем данные
        self._load_settings()
        self._load_bookmarks()
        self._load_session()

    @handle_errors
    def _load_settings(self):
        """Загрузка настроек из файла"""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.settings = {
                    "font_size": data.get("font_size", 12),
                    "theme": data.get("theme", "light"),
                }

    @handle_errors
    def save_settings(self):
        """Сохранение настроек в файл"""
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    @handle_errors
    def _load_bookmarks(self):
        """Загрузка закладок из файла"""
        if os.path.exists(self.bookmarks_file):
            with open(self.bookmarks_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.bookmarks = data.get("bookmarks", [])

    @handle_errors
    def save_bookmarks(self):
        """Сохранение закладок в файл"""
        data = {"bookmarks": self.bookmarks}
        with open(self.bookmarks_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @handle_errors
    def _load_session(self):
        """Загрузка данных последней сессии"""
        if os.path.exists(self.session_file):
            with open(self.session_file, "r", encoding="utf-8") as f:
                self.session = json.load(f)

    @handle_errors
    def save_session(self, book_id=None, page=0):
        """Сохранение данных текущей сессии"""
        if book_id:
            self.session = {"book_id": book_id, "page": page}
        else:
            self.session = {}

        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump(self.session, f, ensure_ascii=False, indent=2)

    def get_font_size(self) -> int:
        """Получение текущего размера шрифта"""
        return self.settings.get("font_size", 12)

    def set_font_size(self, size):
        """Установка размера шрифта"""
        self.settings["font_size"] = size
        self.save_settings()

    def get_theme(self) -> str:
        """Получение текущей темы оформления"""
        return self.settings.get("theme", "light")

    def set_theme(self, theme):
        """Установка темы оформления"""
        self.settings["theme"] = theme
        self.save_settings()

    def add_bookmark(self, bookmark_data):
        """Добавление новой закладки"""
        self.bookmarks.append(bookmark_data)
        self.save_bookmarks()

    def remove_bookmark(self, index) -> bool:
        """Удаление закладки по индексу"""
        if 0 <= index < len(self.bookmarks):
            del self.bookmarks[index]
            self.save_bookmarks()
            return True
        return False

    def get_bookmarks(self) -> list:
        """Получение всех закладок"""
        return self.bookmarks

    def get_last_session(self) -> tuple[int]:
        """Получение данных последней сессии"""
        return self.session.get("book_id"), self.session.get("page", 0)

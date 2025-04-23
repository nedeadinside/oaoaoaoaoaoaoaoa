import os
from PySide6.QtGui import QPalette, QColor
from utils import handle_errors


class ThemeManager:
    """Класс для управления темами оформления приложения"""

    @staticmethod
    def apply_theme(widget, theme_name):
        """Применить тему к виджету"""
        palette = QPalette()

        if theme_name == "dark":
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
            palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
            palette.setColor(QPalette.Text, QColor(255, 255, 255))
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

        widget.setPalette(palette)


class FileUtils:
    """Утилиты для работы с файлами"""

    @staticmethod
    @handle_errors
    def get_file_extension(file_path):
        """Получить расширение файла"""
        _, extension = os.path.splitext(file_path)
        return extension.lower()

    @staticmethod
    @handle_errors
    def is_fb2_file(file_path):
        """Проверить, является ли файл FB2 книгой"""
        return FileUtils.get_file_extension(file_path) == ".fb2"

    @staticmethod
    @handle_errors
    def create_directory_if_not_exists(directory_path):
        """Создать директорию, если она не существует"""
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            return True
        return False


class TextUtils:
    """Утилиты для работы с текстом"""

    @staticmethod
    def truncate_text(text, max_length=100):
        """Обрезать текст до указанной длины с добавлением многоточия"""
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    @staticmethod
    def html_escape(text):
        """Экранирование HTML-символов в тексте"""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    @staticmethod
    def plain_text_to_html(text):
        """Преобразование простого текста в HTML"""
        escaped = TextUtils.html_escape(text)
        return escaped.replace("\n", "<br>")

import os
import datetime

from parsers import AbstractFormatter
from utils import handle_errors


class Book:
    def __init__(self, path, formatter: AbstractFormatter, book_id=None):
        self.path = path
        self.title = "Неизвестная книга"
        self.author = "Неизвестный автор"
        self.date_added = datetime.datetime.now().isoformat()
        self.cover_image = None
        self.id = book_id or os.path.basename(path)
        self.current_page = 0
        self.total_pages = 0
        self.content = []

        self._formatter = formatter
        self.parse_book()

    def parse_book(self):
        result = self._formatter.parse(self.path)
        if result:
            self.title = result["metadata"].get("title", "Неизвестная книга")
            self.author = result["metadata"].get("author", "Неизвестный автор")

            self.content = result["content"]
            self.total_pages = result["total_pages"]

            self.cover_image = result["cover"]

    def get_current_page_content(self):
        if not self.content or self.current_page >= len(self.content):
            return "Нет содержимого для отображения."
        return self.content[self.current_page]

    def get_page(self, page_num):
        """Получение содержимого указанной страницы"""
        if page_num < 0 or page_num >= self.total_pages:
            return None
        self.current_page = page_num
        return self.content[page_num]

    def next_page(self):
        """Переход на следующую страницу"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
        return self.get_current_page_content()

    def prev_page(self):
        """Переход на предыдущую страницу"""
        if self.current_page > 0:
            self.current_page -= 1
        return self.get_current_page_content()

    @handle_errors
    def get_icon(self):
        """Получение иконки книги из обложки"""
        return self._formatter.get_icon_from_cover(self.cover_image)

    def get_cover_image(self):
        """Получение данных обложки"""
        return self.cover_image

    def to_dict(self):
        """Сериализация книги в словарь для сохранения"""
        return {
            "id": self.id,
            "path": self.path,
            "title": self.title,
            "author": self.author,
            "date_added": self.date_added,
            "current_page": self.current_page,
        }

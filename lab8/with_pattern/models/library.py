import os
import json

from .book import Book
from utils import handle_errors
from typing import List, Dict, Type
from parsers import AbstractFormatter
from parsers.fb2 import FB2Formatter


class Library:
    def __init__(self, settings_dir=".settings"):
        self.books = []
        self.settings_dir = settings_dir
        self._formatters: Dict[str, Type[AbstractFormatter]] = {".fb2": FB2Formatter}

        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir)

        self.library_file = os.path.join(settings_dir, "library.json")
        self.load_library()

    def _get_formatter(self, file_path: str) -> AbstractFormatter:
        _, ext = os.path.splitext(file_path.lower())
        formatter_class = self._formatters.get(ext)

        if formatter_class:
            return formatter_class()
        return None

    @handle_errors
    def add_book(self, file_path) -> Book:
        for book in self.books:
            if book.path == file_path:
                return book
        formatter = self._get_formatter(file_path)
        if not formatter:
            raise ValueError(f"Неподдерживаемый формат файла: {file_path}")

        book = Book(file_path, formatter)
        self.books.append(book)
        self.save_library()
        return book

    def get_books(self) -> List[Book]:
        return self.books

    def get_book_by_index(self, index) -> Book:
        if 0 <= index < len(self.books):
            return self.books[index]
        return None

    def search_books(self, query) -> List[Book]:
        query = query.lower()
        results = []

        for book in self.books:
            if query in book.title.lower() or query in book.author.lower():
                results.append(book)

        return results

    def sort_books(self, sort_option) -> List[Book]:
        """
        Сортирует и возвращает копию списка книг без изменения
        исходного порядка книг в библиотеке
        """
        sorted_books = list(self.books)

        if sort_option == "По названию (А-Я)":
            sorted_books.sort(key=lambda x: x.title)
        elif sort_option == "По названию (Я-А)":
            sorted_books.sort(key=lambda x: x.title, reverse=True)
        elif sort_option == "По автору (А-Я)":
            sorted_books.sort(key=lambda x: x.author)
        elif sort_option == "По автору (Я-А)":
            sorted_books.sort(key=lambda x: x.author, reverse=True)
        elif sort_option == "По дате добавления (сначала новые)":
            sorted_books.sort(key=lambda x: x.date_added, reverse=True)
        elif sort_option == "По дате добавления (сначала старые)":
            sorted_books.sort(key=lambda x: x.date_added)

        return sorted_books

    @handle_errors
    def load_library(self):
        if not os.path.exists(self.library_file):
            return

        with open(self.library_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.books = []
            for book_data in data.get("books", []):
                book_path = book_data.get("path", "")
                formatter = self._get_formatter(book_path)
                if formatter:
                    book = Book(book_path, formatter, book_data.get("id"))
                    book.title = book_data.get("title", "Неизвестная книга")
                    book.author = book_data.get("author", "Неизвестный автор")
                    book.date_added = book_data.get("date_added", "")
                    book.current_page = book_data.get("current_page", 0)
                    self.books.append(book)

    @handle_errors
    def save_library(self):
        data = {"books": [book.to_dict() for book in self.books]}

        with open(self.library_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

import os
import json

from .book import Book
from utils import handle_errors


class Library:
    def __init__(self, settings_dir=".settings"):
        self.books = []
        self.settings_dir = settings_dir

        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir)

        self.library_file = os.path.join(settings_dir, "library.json")
        self.load_library()

    @handle_errors
    def add_book(self, file_path):
        for book in self.books:
            if book.path == file_path:
                return book

        book = Book(file_path)
        self.books.append(book)
        self.save_library()
        return book

    def get_books(self):
        return self.books

    def get_book_by_index(self, index):
        if 0 <= index < len(self.books):
            return self.books[index]
        return None

    def search_books(self, query):
        query = query.lower()
        results = []

        for book in self.books:
            if query in book.title.lower() or query in book.author.lower():
                results.append(book)

        return results

    def sort_books(self, sort_option):
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
                book = Book.from_dict(book_data)
                self.books.append(book)

    @handle_errors
    def save_library(self):
        data = {"books": [book.to_dict() for book in self.books]}

        with open(self.library_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

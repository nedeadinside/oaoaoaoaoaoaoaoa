from ui.window import MainWindow

from models import Library

from utils.storage import Storage
from utils.helpers import FileUtils
from PySide6.QtWidgets import QApplication, QFontDialog

import sys


class EReaderApp:
    def __init__(
        self, library: Library, storage: Storage, main_window: MainWindow, app=None
    ):
        self.app = app
        self.main_window = main_window

        self.storage = storage
        self.library = library

        self._connect_signals()
        self._load_initial_data()

    def _connect_signals(self):
        self.main_window.open_action.triggered.connect(self._open_book_dialog)
        self.main_window.exit_action.triggered.connect(self.app.quit)
        self.main_window.light_theme_action.triggered.connect(
            lambda: self._change_theme("light")
        )
        self.main_window.dark_theme_action.triggered.connect(
            lambda: self._change_theme("dark")
        )
        self.main_window.add_bookmark_action.triggered.connect(self._add_bookmark)

        self.main_window.add_book_button.clicked.connect(self._open_book_dialog)
        self.main_window.next_page_button.clicked.connect(self._next_page)
        self.main_window.prev_page_button.clicked.connect(self._prev_page)
        self.main_window.goto_bookmark_button.clicked.connect(self._goto_bookmark)
        self.main_window.delete_bookmark_button.clicked.connect(self._delete_bookmark)

        self.main_window.books_list.itemDoubleClicked.connect(
            lambda: self._open_book(self.main_window.get_selected_book_index())
        )
        self.main_window.font_size_slider.valueChanged.connect(self._change_font_size)
        self.main_window.search_input.textChanged.connect(self._search_books)
        self.main_window.sort_combo.currentTextChanged.connect(self._sort_books)
        self.main_window.font_action.triggered.connect(self._show_font_dialog)

    def _load_initial_data(self):

        font_size = self.storage.get_font_size()
        self.main_window.set_font_size(font_size)

        theme = self.storage.get_theme()
        self.main_window.apply_theme(theme)

        books_data = []
        for book in self.library.get_books():
            books_data.append(
                {"title": book.title, "author": book.author, "icon": book.get_icon()}
            )
        self.main_window.populate_books_list(books_data)

        self.main_window.update_bookmarks_list(self.storage.get_bookmarks())
        book_id, page = self.storage.get_last_session()
        if book_id:
            for index, book in enumerate(self.library.get_books()):
                if book.id == book_id:
                    self._open_book(index)
                    break

    def _open_book_dialog(self):
        file_path = self.main_window.show_file_dialog()
        if file_path:
            if not FileUtils.is_fb2_file(file_path):
                self.main_window.show_error(
                    "Ошибка", f"Файл {file_path} не является книгой в формате FB2."
                )
                return

            book = self.library.add_book(file_path)

            books_data = []
            for book in self.library.get_books():
                books_data.append(
                    {
                        "title": book.title,
                        "author": book.author,
                        "icon": book.get_icon(),
                    }
                )
            self.main_window.populate_books_list(books_data)

            for index, b in enumerate(self.library.get_books()):
                if b.path == file_path:
                    self._open_book(index)
                    break

    def _open_book(self, index):
        if index is None:
            return

        book = self.library.get_book_by_index(index)
        if book:
            content = book.get_current_page_content()
            self.main_window.set_current_book_content(
                content, book.current_page + 1, book.total_pages
            )

            self.storage.save_session(book.id, book.current_page)

            self.main_window.statusBar.showMessage(f"Открыта книга: {book.title}")

    def _next_page(self):
        """Переход на следующую страницу"""
        for book in self.library.get_books():
            book_id, current_page = self.storage.get_last_session()
            if book.id == book_id:
                content = book.next_page()
                self.main_window.set_current_book_content(
                    content, book.current_page + 1, book.total_pages
                )
                self.storage.save_session(book.id, book.current_page)
                break

    def _prev_page(self):
        """Переход на предыдущую страницу"""
        for book in self.library.get_books():
            book_id, current_page = self.storage.get_last_session()
            if book.id == book_id:
                content = book.prev_page()
                self.main_window.set_current_book_content(
                    content, book.current_page + 1, book.total_pages
                )
                self.storage.save_session(book.id, book.current_page)
                break

    def _add_bookmark(self):
        """Добавление закладки"""
        selected_text = self.main_window.get_selected_text()
        if not selected_text:
            self.main_window.show_info(
                "Закладка", "Выделите текст для создания закладки."
            )
            return

        for book in self.library.get_books():
            book_id, current_page = self.storage.get_last_session()
            if book.id == book_id:
                bookmark_data = {
                    "text": selected_text,
                    "book": book.title,
                    "author": book.author,
                    "book_id": book.id,
                    "page": book.current_page,
                }

                self.storage.add_bookmark(bookmark_data)
                self.main_window.update_bookmarks_list(self.storage.get_bookmarks())

                self.main_window.show_info("Закладка", "Закладка успешно добавлена.")
                break

    def _goto_bookmark(self):
        """Переход к закладке"""
        index = self.main_window.get_selected_bookmark_index()
        if index is None:
            return

        bookmarks = self.storage.get_bookmarks()
        if 0 <= index < len(bookmarks):
            bookmark = bookmarks[index]
            book_id = bookmark.get("book_id")
            page = bookmark.get("page", 0)

            for book in self.library.get_books():
                if book.id == book_id:
                    content = book.get_page(page)
                    self.main_window.set_current_book_content(
                        content, book.current_page + 1, book.total_pages
                    )
                    self.storage.save_session(book.id, book.current_page)
                    break

    def _delete_bookmark(self):
        """Удаление закладки"""
        index = self.main_window.get_selected_bookmark_index()
        if index is None:
            return

        if self.storage.remove_bookmark(index):
            self.main_window.update_bookmarks_list(self.storage.get_bookmarks())
            self.main_window.show_info("Закладка", "Закладка успешно удалена.")

    def _search_books(self, query):
        """Поиск книг по запросу"""
        if not query:
            books_data = []
            for book in self.library.get_books():
                books_data.append(
                    {
                        "title": book.title,
                        "author": book.author,
                        "icon": book.get_icon(),
                    }
                )
            self.main_window.populate_books_list(books_data)
            return

        results = self.library.search_books(query)
        books_data = []
        for book in results:
            books_data.append(
                {"title": book.title, "author": book.author, "icon": book.get_icon()}
            )
        self.main_window.populate_books_list(books_data)

    def _sort_books(self, sort_option):
        """Сортировка книг по выбранному критерию"""
        sorted_books = self.library.sort_books(sort_option)

        books_data = []
        for book in sorted_books:
            books_data.append(
                {"title": book.title, "author": book.author, "icon": book.get_icon()}
            )

        self.main_window.populate_books_list(books_data)

    def _change_font_size(self, size):
        """Изменение размера шрифта"""
        self.main_window.set_font_size(size)
        self.storage.set_font_size(size)

    def _change_theme(self, theme):
        """Изменение темы оформления"""
        self.main_window.apply_theme(theme)
        self.storage.set_theme(theme)

    def _show_font_dialog(self):
        """Отображение диалога выбора шрифта"""
        current_font = self.main_window.text_area.font()
        font_dialog = QFontDialog(self.main_window)
        font_dialog.setCurrentFont(current_font)

        if font_dialog.exec():
            selected_font = font_dialog.selectedFont()
            self.main_window.text_area.setFont(selected_font)
            self.storage.set_font_size(selected_font.pointSize())
            self.main_window.set_font_size(selected_font.pointSize())

    def run(self):
        """Запуск приложения"""
        self.main_window.show()
        return self.app.exec()


if __name__ == "__main__":
    settings_dir = ".settings"

    app = QApplication(sys.argv)

    library = Library(settings_dir)
    storage = Storage(settings_dir)
    main_window = MainWindow()

    ereader_app = EReaderApp(
        library=library, storage=storage, main_window=main_window, app=app
    )
    sys.exit(ereader_app.run())

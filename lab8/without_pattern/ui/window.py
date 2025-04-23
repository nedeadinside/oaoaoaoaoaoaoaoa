from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QTabWidget,
    QMenuBar,
    QMenu,
    QLabel,
    QStatusBar,
    QMessageBox,
    QFileDialog,
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, Slot

from .widgets import (
    BookListWidget,
    BookmarkListWidget,
    ReadingTextBrowser,
    FontSizeSlider,
    NavigationButton,
    SearchInput,
    SortComboBox,
    PageInfoLabel,
)
from utils.helpers import ThemeManager


class MainWindow(QMainWindow):
    """Главное окно приложения электронной читалки"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Электронная читалка")
        self.setMinimumSize(1000, 700)

        self._create_menu()

        # Создание центрального виджета
        self._create_central_widget()
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Готово")

    def _create_menu(self):
        """Создание меню приложения"""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # Меню "Файл"
        file_menu = QMenu("Файл", self)
        menu_bar.addMenu(file_menu)

        self.open_action = QAction("Открыть книгу...", self)
        self.open_action.setShortcut("Ctrl+O")
        file_menu.addAction(self.open_action)

        file_menu.addSeparator()

        self.exit_action = QAction("Выход", self)
        self.exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(self.exit_action)

        # Меню "Вид"
        view_menu = QMenu("Вид", self)
        menu_bar.addMenu(view_menu)

        self.font_action = QAction("Выбрать шрифт...", self)
        view_menu.addAction(self.font_action)

        view_menu.addSeparator()

        theme_menu = QMenu("Тема оформления", self)
        view_menu.addMenu(theme_menu)

        self.light_theme_action = QAction("Светлая", self)
        self.light_theme_action.setCheckable(True)
        self.light_theme_action.setChecked(True)
        theme_menu.addAction(self.light_theme_action)

        self.dark_theme_action = QAction("Тёмная", self)
        self.dark_theme_action.setCheckable(True)
        theme_menu.addAction(self.dark_theme_action)

        # Меню "Закладки"
        bookmarks_menu = QMenu("Закладки", self)
        menu_bar.addMenu(bookmarks_menu)

        self.add_bookmark_action = QAction("Добавить закладку", self)
        self.add_bookmark_action.setShortcut("Ctrl+B")
        bookmarks_menu.addAction(self.add_bookmark_action)

        # Меню "Помощь"
        help_menu = QMenu("Помощь", self)
        menu_bar.addMenu(help_menu)

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_central_widget(self):
        """Создание центрального виджета"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Левая панель: Библиотека и закладки
        left_panel = QTabWidget()

        # Вкладка "Библиотека"
        library_tab = QWidget()
        library_layout = QVBoxLayout(library_tab)

        # Поиск и сортировка
        search_layout = QHBoxLayout()
        self.search_input = SearchInput()
        self.sort_combo = SortComboBox()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.sort_combo)
        library_layout.addLayout(search_layout)

        # Список книг
        self.books_list = BookListWidget()
        library_layout.addWidget(self.books_list)

        # Кнопка добавления книги
        self.add_book_button = NavigationButton("Добавить книгу")
        library_layout.addWidget(self.add_book_button)

        left_panel.addTab(library_tab, "Библиотека")

        # Вкладка "Закладки"
        bookmarks_tab = QWidget()
        bookmarks_layout = QVBoxLayout(bookmarks_tab)

        self.bookmarks_list = BookmarkListWidget()
        bookmarks_layout.addWidget(self.bookmarks_list)

        bookmarks_buttons_layout = QHBoxLayout()
        self.goto_bookmark_button = NavigationButton("Перейти")
        self.delete_bookmark_button = NavigationButton("Удалить")

        bookmarks_buttons_layout.addWidget(self.goto_bookmark_button)
        bookmarks_buttons_layout.addWidget(self.delete_bookmark_button)
        bookmarks_layout.addLayout(bookmarks_buttons_layout)

        left_panel.addTab(bookmarks_tab, "Закладки")

        # Правая панель: Чтение
        right_panel = QWidget()
        reading_layout = QVBoxLayout(right_panel)

        # Текстовый браузер для отображения книги
        self.text_area = ReadingTextBrowser()
        reading_layout.addWidget(self.text_area)

        # Навигация по страницам
        navigation_layout = QHBoxLayout()
        self.prev_page_button = NavigationButton("Предыдущая")
        self.page_info_label = PageInfoLabel()
        self.next_page_button = NavigationButton("Следующая")

        navigation_layout.addWidget(self.prev_page_button)
        navigation_layout.addWidget(self.page_info_label)
        navigation_layout.addWidget(self.next_page_button)
        reading_layout.addLayout(navigation_layout)

        # Настройка размера шрифта
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("Размер шрифта:")
        self.font_size_slider = FontSizeSlider()
        self.font_size_value_label = QLabel("12")
        self.font_size_slider.valueChanged.connect(
            lambda value: self.font_size_value_label.setText(str(value))
        )

        font_size_layout.addWidget(font_size_label)
        font_size_layout.addWidget(self.font_size_slider)
        font_size_layout.addWidget(self.font_size_value_label)
        reading_layout.addLayout(font_size_layout)

        # Добавление панелей в сплиттер
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])

        main_layout.addWidget(splitter)

    @Slot()
    def _show_about(self):
        QMessageBox.about(self, "О программе", "<h3>Электронная читалка</h3>")

    def populate_books_list(self, books):
        """Заполнить список книг"""
        self.books_list.clear()

        for book in books:
            title = book.get("title", "Неизвестная книга")
            author = book.get("author", "Неизвестный автор")
            icon = book.get("icon")
            self.books_list.add_book_item(title, author, icon)

    def update_bookmarks_list(self, bookmarks):
        """Обновить список закладок"""
        self.bookmarks_list.clear()

        for bookmark in bookmarks:
            text = bookmark.get("text", "")
            book_title = bookmark.get("book", "")
            page = bookmark.get("page", 0)
            self.bookmarks_list.add_bookmark_item(text, book_title, page)

    def set_current_book_content(self, content, current_page, total_pages):
        """Установить содержимое текущей книги"""
        if content:
            self.text_area.setHtml(content)
            self.page_info_label.update_page_info(current_page, total_pages)

    def get_selected_book_index(self):
        """Получить индекс выбранной книги"""
        selected_items = self.books_list.selectedItems()
        if selected_items:
            return self.books_list.row(selected_items[0])
        return None

    def get_selected_bookmark_index(self):
        """Получить индекс выбранной закладки"""
        selected_items = self.bookmarks_list.selectedItems()
        if selected_items:
            return self.bookmarks_list.row(selected_items[0])
        return None

    def get_selected_text(self):
        """Получить выделенный текст"""
        return self.text_area.textCursor().selectedText()

    def show_file_dialog(self):
        """Показать диалог выбора файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть книгу", "", "FB2 файлы (*.fb2);;Все файлы (*.*)"
        )
        return file_path

    def apply_theme(self, theme_name):
        """Применить тему оформления"""
        ThemeManager.apply_theme(self, theme_name)

        # Обновить состояние меню
        is_dark = theme_name == "dark"
        self.dark_theme_action.setChecked(is_dark)
        self.light_theme_action.setChecked(not is_dark)

    def set_font_size(self, size):
        """Установить размер шрифта"""
        self.font_size_slider.setValue(size)
        self.font_size_value_label.setText(str(size))

        # Применить размер шрифта к тексту
        font = self.text_area.font()
        font.setPointSize(size)
        self.text_area.setFont(font)

    def show_error(self, title, message):
        """Показать сообщение об ошибке"""
        QMessageBox.critical(self, title, message)

    def show_info(self, title, message):
        """Показать информационное сообщение"""
        QMessageBox.information(self, title, message)

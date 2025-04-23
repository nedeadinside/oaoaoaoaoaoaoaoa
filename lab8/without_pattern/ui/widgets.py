from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QTextBrowser,
    QSlider,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, Signal


class BookListWidget(QListWidget):
    """Виджет для отображения списка книг"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def add_book_item(self, title, author, icon=None):
        """Добавить элемент книги в список"""
        item = QListWidgetItem(self)
        item.setText(f"{title}\n{author}")

        if icon:
            item.setIcon(icon)
        else:
            # Использовать стандартную иконку, если обложка не найдена
            item.setIcon(QIcon.fromTheme("document-new"))

        self.addItem(item)


class BookmarkListWidget(QListWidget):
    """Виджет для отображения списка закладок"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)

    def add_bookmark_item(self, text, book_title, page_num):
        """Добавить закладку в список"""
        item = QListWidgetItem(self)
        item.setText(f"{text[:50]}...\n{book_title} (стр. {page_num + 1})")
        self.addItem(item)


class ReadingTextBrowser(QTextBrowser):
    """Виджет для отображения текста книги с возможностью выделения текста"""

    textSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setOpenLinks(False)
        self.setFont(QFont("Times New Roman", 12))

    def selectionChanged(self):
        """Обработка изменения выделения текста"""
        super().selectionChanged()
        selected_text = self.textCursor().selectedText()
        if selected_text:
            self.textSelected.emit(selected_text)


class FontSizeSlider(QSlider):
    """Слайдер для изменения размера шрифта"""

    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setMinimum(8)
        self.setMaximum(24)
        self.setValue(12)
        self.setTickPosition(QSlider.TicksBelow)
        self.setTickInterval(2)


class NavigationButton(QPushButton):
    """Кнопка навигации по страницам книги"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumWidth(120)


class SearchInput(QLineEdit):
    """Поле для поиска по библиотеке"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Поиск по названию или автору...")
        self.setClearButtonEnabled(True)


class SortComboBox(QComboBox):
    """Выпадающий список для сортировки книг"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addItems(
            [
                "По названию (А-Я)",
                "По названию (Я-А)",
                "По автору (А-Я)",
                "По автору (Я-А)",
                "По дате добавления (сначала новые)",
                "По дате добавления (сначала старые)",
            ]
        )


class PageInfoLabel(QLabel):
    """Метка для отображения информации о текущей странице"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Страница 0 из 0")

    def update_page_info(self, current, total):
        """Обновить информацию о текущей странице"""
        self.setText(f"Страница {current} из {total}")

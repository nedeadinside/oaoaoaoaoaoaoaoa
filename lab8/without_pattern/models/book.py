import os
import datetime
import base64
from lxml import etree
from PySide6.QtGui import QIcon, QPixmap

from utils import FB2_NS, handle_errors

CHARS_PER_PAGE = 1500


class Book:
    def __init__(self, path, book_id=None):
        self.path = path
        self.title = "Неизвестная книга"
        self.author = "Неизвестный автор"
        self.date_added = datetime.datetime.now().isoformat()
        self.cover_image = None
        self.id = book_id or os.path.basename(path)
        self.current_page = 0
        self.total_pages = 0
        self.content = []
        self._namespaces = FB2_NS
        self._root = None

        self.parse_book()

    def parse_book(self):
        """Парсинг книги из файла"""
        try:
            with open(self.path, "rb") as f:
                fb2_content = f.read()

            parser = etree.XMLParser(recover=True, remove_blank_text=True)
            self._root = etree.fromstring(fb2_content, parser=parser)

            if self._root is None:
                raise ValueError(f"Не удалось распарсить файл: {self.path}")

            self._extract_metadata()
            elements = self._extract_content()
            self.content = self._format_content_into_pages(elements)
            self.total_pages = len(self.content)
            self.cover_image = self._extract_cover()

        except Exception as e:
            print(f"Ошибка при парсинге FB2 файла: {e}")
            self.title = "Ошибка"
            self.author = "Ошибка при загрузке файла"
            self.content = ["<p>Ошибка: Не удалось обработать содержимое книги.</p>"]
            self.total_pages = 1
            self.cover_image = None

    @handle_errors
    def _extract_metadata(self):
        """Извлечение метаданных из книги"""
        title_element = self._root.xpath(
            "//fb:description/fb:title-info/fb:book-title", namespaces=self._namespaces
        )
        if title_element and title_element[0].text:
            self.title = title_element[0].text.strip()

        authors_elements = self._root.xpath(
            "//fb:description/fb:title-info/fb:author", namespaces=self._namespaces
        )
        authors_list = []
        if authors_elements:
            for author_element in authors_elements:
                first = author_element.xpath(
                    ".//fb:first-name/text()", namespaces=self._namespaces
                )
                last = author_element.xpath(
                    ".//fb:last-name/text()", namespaces=self._namespaces
                )
                nick = author_element.xpath(
                    ".//fb:nickname/text()", namespaces=self._namespaces
                )

                first_name = first[0].strip() if first else ""
                last_name = last[0].strip() if last else ""
                nickname = nick[0].strip() if nick else ""

                full_name = f"{first_name} {last_name}".strip()
                if full_name:
                    authors_list.append(full_name)
                elif nickname:
                    authors_list.append(nickname)

            if authors_list:
                self.author = ", ".join(authors_list)

    @handle_errors
    def _extract_content(self):
        """Извлечение содержимого книги без использования итератора"""
        if self._root is None:
            return []

        elements = []
        body_nodes = self._root.xpath("//fb:body", namespaces=self._namespaces)

        if body_nodes and len(body_nodes) > 0:
            self._extract_elements_from_node(body_nodes[0], elements)

        return elements

    def _extract_elements_from_node(self, start_node, elements):
        """Извлекаем элементы из XML-дерева без использования итератора"""
        if start_node is None:
            return

        sections = start_node.xpath("./fb:section", namespaces=self._namespaces)

        if not sections:
            self._process_node_content(start_node, elements)
        else:
            for section in sections:
                titles = section.xpath("./fb:title", namespaces=self._namespaces)
                for title in titles:
                    html_content = self._render_element(title)
                    html_content = " ".join(html_content.split())
                    text_len = len(
                        etree.tostring(
                            title, method="text", encoding="unicode", with_tail=False
                        )
                    )
                    elements.append(
                        {"type": "title", "html": html_content, "text_len": text_len}
                    )

                paragraphs = section.xpath(
                    "./fb:p | ./fb:subtitle | ./fb:epigraph | ./fb:empty-line",
                    namespaces=self._namespaces,
                )
                for p in paragraphs:
                    tag = etree.QName(p.tag).localname
                    html_content = self._render_element(p)
                    html_content = " ".join(html_content.split())
                    text_len = len(
                        etree.tostring(
                            p, method="text", encoding="unicode", with_tail=False
                        )
                    )
                    elements.append(
                        {"type": tag, "html": html_content, "text_len": text_len}
                    )

                self._process_nested_sections(section, elements)

    def _process_nested_sections(self, section, elements):
        """Обработка вложенных секций без использования итератора"""
        nested_sections = section.xpath("./fb:section", namespaces=self._namespaces)
        for nested_section in nested_sections:
            titles = nested_section.xpath("./fb:title", namespaces=self._namespaces)
            for title in titles:
                html_content = self._render_element(title)
                html_content = " ".join(html_content.split())
                text_len = len(
                    etree.tostring(
                        title, method="text", encoding="unicode", with_tail=False
                    )
                )
                elements.append(
                    {"type": "title", "html": html_content, "text_len": text_len}
                )

            paragraphs = nested_section.xpath(
                "./fb:p | ./fb:subtitle | ./fb:epigraph | ./fb:empty-line",
                namespaces=self._namespaces,
            )
            for p in paragraphs:
                tag = etree.QName(p.tag).localname
                html_content = self._render_element(p)
                html_content = " ".join(html_content.split())
                text_len = len(
                    etree.tostring(
                        p, method="text", encoding="unicode", with_tail=False
                    )
                )
                elements.append(
                    {"type": tag, "html": html_content, "text_len": text_len}
                )

            self._process_nested_sections(nested_section, elements)

    def _process_node_content(self, node, elements):
        """Обработка содержимого узла, если нет секций"""
        node_elements = node.xpath(
            "./fb:p | ./fb:title | ./fb:subtitle | ./fb:epigraph | ./fb:empty-line",
            namespaces=self._namespaces,
        )
        for element in node_elements:
            tag = etree.QName(element.tag).localname
            html_content = self._render_element(element)
            html_content = " ".join(html_content.split())
            text_len = len(
                etree.tostring(
                    element, method="text", encoding="unicode", with_tail=False
                )
            )
            elements.append({"type": tag, "html": html_content, "text_len": text_len})

    def _render_element(self, element):
        """Преобразование XML элемента в HTML"""
        if element is None:
            return ""

        tag = etree.QName(element.tag).localname
        text = element.text or ""
        tail = element.tail or ""

        content = ""

        if tag == "p":
            content = f"<p>{text}"
            for child in element:
                content += self._render_element(child)
            content += "</p>"
        elif tag == "emphasis":
            content = f"<i>{text}"
            for child in element:
                content += self._render_element(child)
            content += "</i>"
        elif tag == "strong":
            content = f"<b>{text}"
            for child in element:
                content += self._render_element(child)
            content += "</b>"
        elif tag == "title":
            content = f"<h2>{text}"
            for child in element:
                content += self._render_element(child)
            content += "</h2>"
        elif tag == "subtitle":
            content = f"<h3>{text}"
            for child in element:
                content += self._render_element(child)
            content += "</h3>"
        elif tag == "empty-line":
            content = "<br>" + text
            for child in element:
                content += self._render_element(child)
        else:
            content = text
            for child in element:
                content += self._render_element(child)

        content += tail
        return content.replace("\n", " ").strip()

    @handle_errors
    def _format_content_into_pages(self, elements):
        """Форматирование элементов контента в страницы"""
        if not elements:
            return ["<p>Не удалось извлечь содержимое книги (содержимое пусто).</p>"]

        pages = []
        current_page_html = []
        current_page_chars = 0

        for element in elements:
            element_text_len = element["text_len"]
            element_html = element["html"]

            cost = element_text_len

            if current_page_chars > 0 and (current_page_chars + cost > CHARS_PER_PAGE):
                pages.append("".join(current_page_html))
                current_page_html = [element_html]
                current_page_chars = cost
            elif cost > CHARS_PER_PAGE and not current_page_html:
                pages.append(element_html)
                current_page_html = []
                current_page_chars = 0
            else:
                current_page_html.append(element_html)
                current_page_chars += cost

        if current_page_html:
            pages.append("".join(current_page_html))

        return pages if pages else ["<p>Содержимое не найдено.</p>"]

    @handle_errors
    def _extract_cover(self):
        """Извлечение обложки книги"""
        if self._root is None:
            return None

        cover_href = self._root.xpath(
            "//fb:description/fb:title-info/fb:coverpage/fb:image/@l:href",
            namespaces=self._namespaces,
        )

        if cover_href:
            cover_id = cover_href[0].lstrip("#")
            binary_elements = self._root.xpath(
                f"//fb:binary[@id='{cover_id}']", namespaces=self._namespaces
            )

            if binary_elements:
                binary_element = binary_elements[0]
                content_type = binary_element.get(
                    "content-type", "application/octet-stream"
                )
                base64_data = binary_element.text

                if base64_data:
                    image_data = base64.b64decode(base64_data.strip())
                    return {
                        "data": image_data,
                        "content_type": content_type,
                    }
        return None

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
        if self.cover_image and "data" in self.cover_image:
            image_data = self.cover_image.get("data")
            if isinstance(image_data, bytes):
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                return QIcon(pixmap)
        return None

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

    @staticmethod
    def from_dict(data):
        """Создание книги из словаря"""
        book = Book(data["path"], data["id"])
        book.title = data["title"]
        book.author = data["author"]
        book.date_added = data["date_added"]
        book.current_page = data["current_page"]
        return book

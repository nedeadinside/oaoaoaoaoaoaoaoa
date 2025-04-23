from lxml import etree
import base64

from utils import FB2_NS, handle_errors
from parsers import BookIterator, AbstractFormatter

from PySide6.QtGui import QIcon, QPixmap

CHARS_PER_PAGE = 1500


class FB2ContentIterator(BookIterator):
    def __init__(self, root_element, namespaces):
        self._nodes = root_element.xpath("//fb:body", namespaces=namespaces)
        self._namespaces = namespaces
        self._elements = []
        self._position = 0

        if self._nodes and len(self._nodes) > 0:
            self._extract_elements(self._nodes[0])

    def _extract_elements(self, start_node):
        """Извлекаем элементы из XML-дерева"""
        if start_node is None:
            return

        sections = start_node.xpath("./fb:section", namespaces=self._namespaces)

        if not sections:
            self._process_node_content(start_node)
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
                    self._elements.append(
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
                    self._elements.append(
                        {"type": tag, "html": html_content, "text_len": text_len}
                    )

                self._process_nested_sections(section)

    def _process_nested_sections(self, section):
        """Обработка вложенных секций"""
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
                self._elements.append(
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
                self._elements.append(
                    {"type": tag, "html": html_content, "text_len": text_len}
                )

            self._process_nested_sections(nested_section)

    def _process_node_content(self, node):
        """Обработка содержимого узла, если нет секций"""
        elements = node.xpath(
            "./fb:p | ./fb:title | ./fb:subtitle | ./fb:epigraph | ./fb:empty-line",
            namespaces=self._namespaces,
        )
        for element in elements:
            tag = etree.QName(element.tag).localname
            html_content = self._render_element(element)
            html_content = " ".join(html_content.split())
            text_len = len(
                etree.tostring(
                    element, method="text", encoding="unicode", with_tail=False
                )
            )
            self._elements.append(
                {"type": tag, "html": html_content, "text_len": text_len}
            )

    def _render_element(self, element):
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

    def __iter__(self):
        """Возвращает себя как итератор"""
        return self

    def __next__(self):
        if self._position >= len(self._elements):
            raise StopIteration

        element = self._elements[self._position]
        self._position += 1
        return element

    def reset(self):
        self._position = 0


class FB2Formatter(AbstractFormatter):
    """Класс для парсинга FB2 файлов"""

    def __init__(self):
        self._namespaces = FB2_NS

    def parse(self, file_path):
        """Парсинг FB2 файла и извлечение данных"""
        try:
            with open(file_path, "rb") as f:
                fb2_content = f.read()

            parser = etree.XMLParser(recover=True, remove_blank_text=True)
            root = etree.fromstring(fb2_content, parser=parser)
            content_iterator = FB2ContentIterator(root, self._namespaces)
            if root is None:
                raise ValueError(f"Не удалось распарсить файл: {file_path}")

            metadata = self._extract_metadata(root)
            content_pages = self._format_content_into_pages(content_iterator)
            cover = self._extract_cover(root)

            return {
                "root": root,
                "metadata": metadata,
                "content": content_pages,
                "total_pages": len(content_pages),
                "cover": cover,
            }
        except Exception as e:
            print(f"Ошибка при парсинге FB2 файла: {e}")
            return {
                "metadata": {"title": "Ошибка", "author": "Ошибка при загрузке файла"},
                "content": ["<p>Ошибка: Не удалось обработать содержимое книги.</p>"],
                "total_pages": 1,
                "cover": None,
            }

    @handle_errors
    def _extract_metadata(self, root):
        """Извлечение метаданных из книги"""
        metadata = {"title": "Неизвестная книга", "author": "Неизвестный автор"}

        title_element = root.xpath(
            "//fb:description/fb:title-info/fb:book-title", namespaces=self._namespaces
        )
        if title_element and title_element[0].text:
            metadata["title"] = title_element[0].text.strip()

        authors_elements = root.xpath(
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
                metadata["author"] = ", ".join(authors_list)

        return metadata

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
    def _extract_cover(self, root):
        """Извлечение обложки книги"""
        if root is None:
            return None

        cover_href = root.xpath(
            "//fb:description/fb:title-info/fb:coverpage/fb:image/@l:href",
            namespaces=self._namespaces,
        )

        if cover_href:
            cover_id = cover_href[0].lstrip("#")
            binary_elements = root.xpath(
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

    def get_icon_from_cover(self, cover_data):
        """Создание иконки из данных обложки"""
        if cover_data and "data" in cover_data:
            image_data = cover_data.get("data")
            if isinstance(image_data, bytes):
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                return QIcon(pixmap)
        return None

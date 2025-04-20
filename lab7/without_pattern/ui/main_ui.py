from PySide6.QtCore import QCoreApplication, QDateTime, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QCheckBox, QFrame, QLabel,
                               QPushButton, QScrollArea, QTabWidget, QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, 
                               QListWidget, QLineEdit, QDateTimeEdit, QFormLayout, QStackedWidget, QGroupBox)


class UiDialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(900, 600)
        Dialog.setMinimumSize(QSize(900, 600))
        Dialog.setMaximumSize(QSize(900, 600))
        Dialog.setSizeIncrement(QSize(0, 0))
        self.tabWidget = QTabWidget(Dialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(0, 10, 895, 580))
        self.tabWidget.setMinimumSize(QSize(895, 580))
        self.tabWidget.setMaximumSize(QSize(895, 580))
        self.TaskManager = QWidget()
        self.TaskManager.setObjectName(u"TaskManager")
        self.TaskManager.setMinimumSize(QSize(895, 560))
        self.TaskManager.setMaximumSize(QSize(895, 560))
        
        # Вертикальная линия-разделитель
        self.line_2 = QFrame(self.TaskManager)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setGeometry(QRect(230, -140, 15, 700))
        self.line_2.setFrameShape(QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)
        
        # Левая панель со списком задач
        self.scrollArea = QScrollArea(self.TaskManager)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setGeometry(QRect(0, 40, 231, 480))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 229, 478))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        
        # Заголовок для списка задач
        self.label_3 = QLabel(self.TaskManager)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 10, 211, 31))
        font = QFont()
        font.setFamilies([u"Consolas"])
        font.setPointSize(12)
        font.setBold(True)
        self.label_3.setFont(font)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Список задач и кнопка создания новой задачи
        self.task_list = QListWidget(self.scrollAreaWidgetContents)
        self.task_list.setObjectName("task_list")
        
        self.create_task_button = QPushButton("Создать новую задачу", self.TaskManager)
        self.create_task_button.setObjectName("create_task_button")
        self.create_task_button.setGeometry(QRect(10, 520, 211, 30))

        # Добавляем список задач в скроллируемую область
        self.left_panel_layout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.left_panel_layout.addWidget(self.task_list)
        
        # Правая панель с деталями задачи
        self.task_details_panel = QWidget(self.TaskManager)
        self.task_details_panel.setObjectName("task_details_panel")
        self.task_details_panel.setGeometry(QRect(250, 10, 635, 540))
        
        # Создаем стек виджетов для разных режимов (просмотр/редактирование/создание)
        self.details_stack = QStackedWidget(self.task_details_panel)
        self.details_stack.setObjectName("details_stack")
        
        # 1. Страница просмотра задачи
        self.view_page = QWidget()
        self.view_page.setObjectName("view_page")
        
        # 2. Страница редактирования/создания задачи
        self.edit_page = QWidget()
        self.edit_page.setObjectName("edit_page")
        
        # Добавляем страницы в стек
        self.details_stack.addWidget(self.view_page)
        self.details_stack.addWidget(self.edit_page)
        
        # Настраиваем страницу просмотра
        self.view_task_title_label = QLabel("Название задачи", self.view_page)
        self.view_task_title_label.setObjectName("view_task_title_label")
        self.view_task_title_label.setFont(font)
        
        self.view_task_date_label = QLabel("Дата и время:", self.view_page)
        self.view_task_date_value = QLabel("", self.view_page)
        
        self.view_task_description_label = QLabel("Описание задачи:", self.view_page)
        self.view_task_description_value = QTextEdit(self.view_page)
        self.view_task_description_value.setReadOnly(True)
        
        self.edit_task_button = QPushButton("Редактировать", self.view_page)
        self.delete_task_button = QPushButton("Удалить", self.view_page)
        
        # Размещаем элементы на странице просмотра
        view_layout = QVBoxLayout(self.view_page)
        view_layout.addWidget(self.view_task_title_label)
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(self.view_task_date_label)
        date_layout.addWidget(self.view_task_date_value)
        date_layout.addStretch(1)
        view_layout.addLayout(date_layout)
        
        view_layout.addWidget(self.view_task_description_label)
        view_layout.addWidget(self.view_task_description_value)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.edit_task_button)
        button_layout.addWidget(self.delete_task_button)
        view_layout.addLayout(button_layout)
        
        # Настраиваем страницу редактирования/создания
        self.edit_form = QGroupBox("Данные задачи", self.edit_page)
        
        self.task_title_label = QLabel("Название задачи:", self.edit_form)
        self.task_title_input = QLineEdit(self.edit_form)
        
        self.task_date_label = QLabel("Дата и время:", self.edit_form)
        self.task_date_input = QDateTimeEdit(self.edit_form)
        self.task_date_input.setCalendarPopup(True)
        self.task_date_input.setDateTime(QDateTime.currentDateTime())
        
        self.task_description_label = QLabel("Описание задачи:", self.edit_form)
        self.task_description_input = QTextEdit(self.edit_form)
        
        self.save_task_button = QPushButton("Сохранить", self.edit_form)
        self.cancel_edit_button = QPushButton("Отмена", self.edit_form)
        
        # Размещаем элементы на странице редактирования
        form_layout = QFormLayout(self.edit_form)
        form_layout.addRow(self.task_title_label, self.task_title_input)
        form_layout.addRow(self.task_date_label, self.task_date_input)
        form_layout.addRow(self.task_description_label, self.task_description_input)
        
        edit_button_layout = QHBoxLayout()
        edit_button_layout.addWidget(self.save_task_button)
        edit_button_layout.addWidget(self.cancel_edit_button)
        form_layout.addRow("", edit_button_layout)
        
        edit_layout = QVBoxLayout(self.edit_page)
        edit_layout.addWidget(self.edit_form)
        
        # Размещаем стек на правой панели
        details_layout = QVBoxLayout(self.task_details_panel)
        details_layout.addWidget(self.details_stack)
        
        # Основной layout для страницы TaskManager
        self.tabWidget.addTab(self.TaskManager, "")
        
        # ProfileManager (без изменений)
        self.ProfileManager = QWidget()
        self.ProfileManager.setObjectName(u"ProfileManager")
        self.line = QFrame(self.ProfileManager)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(230, -140, 15, 700))
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.label = QLabel(self.ProfileManager)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 20, 221, 100))
        self.label.setFont(font)
        self.label_2 = QLabel(self.ProfileManager)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 170, 221, 100))
        self.label_2.setFont(font)
        self.checkBox = QCheckBox(self.ProfileManager)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setGeometry(QRect(530, 50, 251, 41))
        font1 = QFont()
        font1.setFamilies([u"Consolas"])
        font1.setPointSize(10)
        font1.setBold(True)
        self.checkBox.setFont(font1)
        self.checkBox_2 = QCheckBox(self.ProfileManager)
        self.checkBox_2.setObjectName(u"checkBox_2")
        self.checkBox_2.setGeometry(QRect(530, 200, 251, 41))
        self.checkBox_2.setFont(font1)
        self.textEdit = QTextEdit(self.ProfileManager)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(260, 200, 251, 41))
        self.textEdit_2 = QTextEdit(self.ProfileManager)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setGeometry(QRect(260, 50, 251, 41))
        self.pushButton = QPushButton(self.ProfileManager)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(804, 520, 81, 24))
        self.tabWidget.addTab(self.ProfileManager, "")

        self.retranslateUi(Dialog)

        self.tabWidget.setCurrentIndex(0)
        self.details_stack.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Менеджер задач", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Задачи", None))
        self.create_task_button.setText(QCoreApplication.translate("Dialog", u"Создать новую задачу", None))
        self.edit_task_button.setText(QCoreApplication.translate("Dialog", u"Редактировать", None))
        self.delete_task_button.setText(QCoreApplication.translate("Dialog", u"Удалить", None))
        self.save_task_button.setText(QCoreApplication.translate("Dialog", u"Сохранить", None))
        self.cancel_edit_button.setText(QCoreApplication.translate("Dialog", u"Отмена", None))
        self.task_title_label.setText(QCoreApplication.translate("Dialog", u"Название задачи:", None))
        self.task_date_label.setText(QCoreApplication.translate("Dialog", u"Дата и время:", None))
        self.task_description_label.setText(QCoreApplication.translate("Dialog", u"Описание задачи:", None))
        self.view_task_date_label.setText(QCoreApplication.translate("Dialog", u"Дата и время:", None))
        self.view_task_description_label.setText(QCoreApplication.translate("Dialog", u"Описание задачи:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.TaskManager), QCoreApplication.translate("Dialog", u"Управление задачами", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Адрес электронной почты", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Аккаунт телеграм", None))
        self.checkBox.setText(QCoreApplication.translate("Dialog", u"Присылать уведомления на почту?", None))
        self.checkBox_2.setText(QCoreApplication.translate("Dialog", u"Присылать увеомления в телеграм?", None))
        self.textEdit.setPlaceholderText(QCoreApplication.translate("Dialog", u"id аккаунта телеграм", None))
        self.textEdit_2.setPlaceholderText(QCoreApplication.translate("Dialog", u"example@mail.com", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog", u"Сохранить", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.ProfileManager), QCoreApplication.translate("Dialog", u"Управление профилем", None))
        
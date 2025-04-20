from dataclasses import dataclass

from PySide6.QtWidgets import (
            QSystemTrayIcon, QMenu, QMessageBox, QLabel,
            QDialog, QApplication, QListWidgetItem,
            QLineEdit, QVBoxLayout, QPushButton
)
from PySide6.QtCore import QDateTime, QTimer, Qt
from PySide6.QtGui import QIcon, QAction

from src.notification_logic import NotificationManager

@dataclass
class Task:
    id: int
    title: str
    description: str
    datetime: str
    is_completed: bool = False
    
    def get_qdatetime(self):
        return QDateTime.fromString(self.datetime, "yyyy-MM-dd HH:mm")


class Menu(QDialog):
    def __init__(self,
                 db_manager,
                 ui_dialog,
                 user_id: str,
                 username: str,
                 icon_path: str
            ):
        super().__init__()
        self.ui = ui_dialog
        self.ui.setupUi(self)
        
        self._icon_path = icon_path
        self.user_id = user_id
        self.username = username
        self.db = db_manager
        
        self.tasks: dict[int, Task]= {}
        self.current_task_id = None
        self.notification_timers = {}
        self.notification_manager = None
        
        self.setup_tray_icon()
        
        self.load_tasks()
        self.load_user_profile()
        
        self.ui.create_task_button.clicked.connect(self.create_new_task)
        self.ui.edit_task_button.clicked.connect(self.edit_task)
        self.ui.delete_task_button.clicked.connect(self.delete_task)
        self.ui.save_task_button.clicked.connect(self.save_task)
        self.ui.cancel_edit_button.clicked.connect(self.cancel_edit)
        self.ui.task_list.itemClicked.connect(self.show_task_details)
        self.ui.pushButton.clicked.connect(self.save_user_profile)
        
        self.ui.edit_task_button.setEnabled(False)
        self.ui.delete_task_button.setEnabled(False)
        
        self.setWindowTitle(f"Менеджер задач - {self.username}")
        
        
    def setup_tray_icon(self):
        tray_icon = QIcon(self._icon_path)
        self.tray_icon = QSystemTrayIcon(tray_icon, self)
        
        tray_menu = QMenu()
        show_action = QAction("Показать", self)
        quit_action = QAction("Выйти", self)
        
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.quit_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
        
        
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.activateWindow()
            
            
    def quit_application(self):
        QApplication.quit()
        
        
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        
        self.tray_icon.showMessage(
            "Менеджер задач",
            "Приложение свёрнуто в трей. Нажмите на иконку для открытия.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )


    def load_tasks(self):
        user_tasks = self.db.get_user_tasks(self.user_id)
        self.ui.task_list.clear()
        self.tasks = {}
        
        for task_data in user_tasks:
            task = Task(
                id=task_data['id'],
                title=task_data['title'],
                description=task_data['description'],
                datetime=task_data['datetime'],
                is_completed=task_data['is_completed']
            )
            
            item = QListWidgetItem(task.title)
            if task.is_completed:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                
            self.ui.task_list.addItem(item)
            self.tasks[id(item)] = task
            
            if not task.is_completed:
                self.schedule_task_notification(id(item))


    def create_new_task(self):
        self.ui.task_title_input.setText("")
        self.ui.task_description_input.setText("")
        self.ui.task_date_input.setDateTime(QDateTime.currentDateTime())
        self.current_task_id = None
        self.ui.details_stack.setCurrentIndex(1)


    def edit_task(self):
        if self.current_task_id is not None:
            task = self.tasks.get(self.current_task_id)
            if task:
                self.ui.task_title_input.setText(task.title)
                self.ui.task_description_input.setText(task.description)
                
                dt = QDateTime.fromString(task.datetime, "yyyy-MM-dd HH:mm")
                if not dt.isValid():
                    dt = QDateTime.currentDateTime()
                self.ui.task_date_input.setDateTime(dt)
                
                self.ui.details_stack.setCurrentIndex(1)


    def save_task(self):
        title = self.ui.task_title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Ошибка", "Название задачи не может быть пустым")
            return
            
        description = self.ui.task_description_input.toPlainText()
        datetime = self.ui.task_date_input.dateTime().toString("yyyy-MM-dd HH:mm")
        
        if self.current_task_id is None:
            task_id = self.db.create_task(self.user_id, title, description, datetime)
            
            if task_id:
                item = QListWidgetItem(title)
                self.ui.task_list.addItem(item)
                self.tasks[id(item)] = Task(id=task_id, title=title, description=description, datetime=datetime)
                self.current_task_id = id(item)
                self.schedule_task_notification(self.current_task_id)
        else:
            task = self.tasks[self.current_task_id]
            result = self.db.update_task(task.id, title=title, description=description, datetime=datetime)
            
            if result:
                task.title = title
                task.description = description
                task.datetime = datetime
                
                for i in range(self.ui.task_list.count()):
                    if id(self.ui.task_list.item(i)) == self.current_task_id:
                        self.ui.task_list.item(i).setText(title)
                        break
                self.schedule_task_notification(self.current_task_id)

        self.update_view_page()
        self.ui.details_stack.setCurrentIndex(0)


    def schedule_task_notification(self, task_id):
        if task_id in self.notification_timers:
            if self.notification_timers[task_id]:
                self.notification_timers[task_id].stop()
            del self.notification_timers[task_id]
            
        task = self.tasks[task_id]
        task_dt = task.get_qdatetime()
        
        current_time = QDateTime.currentDateTime()
        
        user_info = self.db.get_user_info(self.user_id)
        
        email = user_info.get('email') if user_info.get('email_notify') else None
        telegram_id = user_info.get('telegram_id') if user_info.get('telegram_notify') else None
        
        # Создаем или обновляем менеджер уведомлений с текущими настройками
        self.notification_manager = NotificationManager(
            self,
            user_email=email,
            telegram_chat_id=telegram_id
        )
        
        if task_dt > current_time:
            ms_to_task = current_time.msecsTo(task_dt)
            
            exact_timer = QTimer(self)
            exact_timer.setSingleShot(True)
            exact_timer.setInterval(ms_to_task)
            
            exact_timer.timeout.connect(lambda: self.notification_manager.notify(task))
            
            self.notification_timers[task_id] = exact_timer
            exact_timer.start()
        else:
            self.notification_manager.notify(task)


    def delete_task(self):
        if self.current_task_id is not None:
            task = self.tasks.get(self.current_task_id)
            
            if task:
                self.db.delete_task(task.id)
                
                if self.current_task_id in self.notification_timers:
                    if self.notification_timers[self.current_task_id]:
                        self.notification_timers[self.current_task_id].stop()
                    del self.notification_timers[self.current_task_id]
                    
                for i in range(self.ui.task_list.count()):
                    if id(self.ui.task_list.item(i)) == self.current_task_id:
                        self.ui.task_list.takeItem(i)
                        break
                        
                del self.tasks[self.current_task_id]
                
                self.current_task_id = None
                self.ui.view_task_title_label.setText("Выберите задачу")
                self.ui.view_task_date_value.setText("")
                self.ui.view_task_description_value.setText("")
                self.ui.edit_task_button.setEnabled(False)
                self.ui.delete_task_button.setEnabled(False)


    def cancel_edit(self):
        self.ui.details_stack.setCurrentIndex(0)
        if self.current_task_id is not None:
            self.update_view_page()


    def show_task_details(self, item):
        self.current_task_id = id(item)
        self.update_view_page()
        self.ui.details_stack.setCurrentIndex(0)
        self.ui.edit_task_button.setEnabled(True)
        self.ui.delete_task_button.setEnabled(True)


    def update_view_page(self):
        if self.current_task_id is not None and self.current_task_id in self.tasks:
            task = self.tasks[self.current_task_id]
            self.ui.view_task_title_label.setText(task.title)
            self.ui.view_task_date_value.setText(task.datetime)
            self.ui.view_task_description_value.setText(task.description)
            
            
    def load_user_profile(self):
        """Загрузка профиля пользователя из базы данных"""
        user_profile = self.db.get_user_info(self.user_id)
        
        if user_profile:
            if user_profile['email']:
                self.ui.textEdit_2.setPlainText(user_profile['email'])
            
            if user_profile['telegram_id']:
                self.ui.textEdit.setPlainText(user_profile['telegram_id'])
            
            self.ui.checkBox.setChecked(user_profile.get('email_notify', False))
            self.ui.checkBox_2.setChecked(user_profile.get('telegram_notify', False))
    
    
    def save_user_profile(self):
        """Сохранение профиля пользователя в базу данных"""
        email = self.ui.textEdit_2.toPlainText()
        telegram_id = self.ui.textEdit.toPlainText()
        
        email_notifications = self.ui.checkBox.isChecked()
        telegram_notifications = self.ui.checkBox_2.isChecked()
        
        result = self.db.update_user_notification_settings(
            self.user_id, 
            email=email, 
            email_notify=email_notifications,
            telegram_id=telegram_id,
            telegram_notify=telegram_notifications
        )
        
        if result:
            QMessageBox.information(self, "Успех", "Профиль успешно обновлен")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось обновить профиль")


class LoginDialog(QDialog):
    def __init__(self, database):
        super().__init__()
        self.user_id = None
        self.exit = False
        self.database = database
        
        self.setWindowTitle("Вход")
        self.username_label = QLabel("Имя пользователя:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.accept)
        
        self.exit_button = QPushButton("Выйти")
        self.exit_button.clicked.connect(self.exit_application)

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.exit_button)
        self.setLayout(layout)


    def exit_application(self):
        self.exit = True
        self.reject()


    def _get_credentials(self):
        return self.username_input.text(), self.password_input.text()


    def _validate_credentials(self):
        credentials = {
            'user_id': None,
            'username': None,
            'password': None
        }
        username, password = self._get_credentials()
        
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Пустые поля")
            return

        self.user_id = self.database.authenticate_user(username, password)
        
        if not self.user_id:
            if self.database.user_exists(username):
                QMessageBox.warning(self, "Ошибка", "Неправильный пароль")
                return None
            else:
                self.database.create_user(username, password)
                self.user_id = self.database.authenticate_user(username, password)
        
        credentials["user_id"] = self.user_id
        credentials["username"] = username
        credentials["password"] = password
        self.accept()
        
        return credentials
    
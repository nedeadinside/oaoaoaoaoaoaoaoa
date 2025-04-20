from abc import ABC, abstractmethod
import smtplib
import requests
import os

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv, find_dotenv
from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtCore import Qt

load_dotenv(find_dotenv())
BOT_TOKEN = os.getenv("BOT_TOKEN")
MAIL_ADDR = os.getenv("MAIL_ADDR")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")


class Notifier(ABC):
    """Базовый интерфейс для всех уведомлений"""

    @abstractmethod
    def notify(self, task):
        """Отправляет уведомление о задаче"""
        pass

    @abstractmethod
    def format_message(self, task):
        """Форматирует сообщение уведомления"""
        pass

    @abstractmethod
    def mark_task_completed(self, task):
        """Отмечает задачу как выполненную"""
        pass


class TrayNotifier(Notifier):
    def __init__(self, parent):
        self.parent = parent
        self.tray_icon = parent.tray_icon
        self.db = parent.db
        self.notification_timers = parent.notification_timers
        self.ui = parent.ui
        self.user_id = parent.user_id

    def format_message(self, task):
        title = f"Напоминание о задаче: {task.title}"
        message = (
            f"Время выполнить: Задача в {task.datetime}\n"
            f"Описание: {task.description}"
        )
        return title, message

    def notify(self, task):
        title, message = self.format_message(task)
        self.tray_icon.showMessage(
            title, message, QSystemTrayIcon.MessageIcon.Information, 5000
        )
        self.mark_task_completed(task)

    def mark_task_completed(self, task):
        if task.id in self.notification_timers:
            if self.notification_timers[task.id]:
                self.notification_timers[task.id].stop()
            del self.notification_timers[task.id]

        result = self.db.update_task(task.id, is_completed=True)
        if result:
            task.is_completed = True
            for i in range(self.ui.task_list.count()):
                item = self.ui.task_list.item(i)
                if id(item) == task.id:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                    break


class NotifierDecorator(Notifier):
    """Базовый класс декоратора для уведомлений"""

    def __init__(self, wrapped_notifier: Notifier):
        self.wrapped_notifier = wrapped_notifier

    def notify(self, task):
        self.wrapped_notifier.notify(task)

    def format_message(self, task):
        return self.wrapped_notifier.format_message(task)

    def mark_task_completed(self, task):
        self.wrapped_notifier.mark_task_completed(task)


class EmailNotifier(NotifierDecorator):
    """Декоратор для отправки уведомлений по электронной почте"""

    def __init__(self, wrapped_notifier: Notifier, user_email: str):
        super().__init__(wrapped_notifier)
        self.user_email = user_email
        self.bot_email = MAIL_ADDR
        self.bot_password = MAIL_PASSWORD

    def notify(self, task):
        self.wrapped_notifier.notify(task)
        title, message = self.format_message(task)
        try:
            msg = MIMEMultipart()
            msg["From"] = self.bot_email
            msg["To"] = self.user_email
            msg["Subject"] = title

            body = f"{title}\n\n{message}"
            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP_SSL("smtp.yandex.ru", 465)
            server.login(self.bot_email, self.bot_password)
            server.sendmail(self.bot_email, self.user_email, msg.as_string())
            server.quit()
        except Exception as e:
            print(f"Ошибка отправки уведомления по почте: {e}")


class TelegramNotifier(NotifierDecorator):
    """Декоратор для отправки уведомлений в Telegram"""

    def __init__(self, wrapped_notifier: Notifier, chat_id: str):
        super().__init__(wrapped_notifier)
        self.chat_id = chat_id
        self.bot_token = BOT_TOKEN

    def notify(self, task):
        self.wrapped_notifier.notify(task)
        title, message = self.format_message(task)
        try:
            params = {
                "chat_id": self.chat_id,
                "text": f"<b>{title}</b>\n\n{message}",
                "parse_mode": "HTML",
            }
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            response = requests.post(url, json=params)
            if response.status_code != 200:
                print(
                    f"Ошибка отправки уведомления в Telegram, статус: {response.status_code}"
                )
        except Exception as e:
            print(f"Ошибка отправки уведомления в Telegram: {e}")

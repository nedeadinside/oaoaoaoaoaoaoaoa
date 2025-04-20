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


class NotificationManager:
    def __init__(self, parent, user_email=None, telegram_chat_id=None):
        # Базовые параметры из родителя
        self.parent = parent
        self.tray_icon = parent.tray_icon
        self.db = parent.db
        self.notification_timers = parent.notification_timers
        self.ui = parent.ui
        self.user_id = parent.user_id
        
        # Настройки каналов уведомлений
        self.use_tray = True
        self.use_email = user_email is not None
        self.use_telegram = telegram_chat_id is not None
        
        # Данные для email уведомлений
        self.user_email = user_email
        self.bot_email = MAIL_ADDR
        self.bot_password = MAIL_PASSWORD
        
        # Данные для Telegram уведомлений
        self.telegram_chat_id = telegram_chat_id
        self.bot_token = BOT_TOKEN
    
    def format_message(self, task):
        """Форматирует сообщение уведомления"""
        title = f"Напоминание о задаче: {task.title}"
        message = f"Время выполнить: Задача в {task.datetime}\n" \
                  f"Описание: {task.description}"
        return title, message
    
    def notify(self, task):
        """Отправка уведомлений по всем настроенным каналам"""
        title, message = self.format_message(task)
        
        # Отправка уведомлений через доступные каналы
        if self.use_tray:
            self.send_tray_notification(title, message, task)
        
        if self.use_email:
            self.send_email_notification(title, message)
        
        if self.use_telegram:
            self.send_telegram_notification(title, message)
            
        # Отметить задачу как выполненную
        self.mark_task_completed(task)
    
    def send_tray_notification(self, title, message, task):
        """Отправка уведомления в системный трей"""
        self.tray_icon.showMessage(
            title, 
            message, 
            QSystemTrayIcon.MessageIcon.Information, 
            5000
        )
    
    def send_email_notification(self, title, message):
        """Отправка уведомления по электронной почте"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.bot_email
            msg['To'] = self.user_email
            msg['Subject'] = title
            
            body = f"{title}\n\n{message}"
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
            server.login(self.bot_email, self.bot_password)
            server.sendmail(self.bot_email, self.user_email, msg.as_string())
            server.quit()
        except Exception as e:
            print(f"Ошибка отправки уведомления по почте: {e}")
    
    def send_telegram_notification(self, title, message):
        """Отправка уведомления в Telegram"""
        try:
            params = {
                "chat_id": self.telegram_chat_id,
                "text": f"<b>{title}</b>\n\n{message}",
                "parse_mode": "HTML"
            }
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            response = requests.post(url, json=params)
            if response.status_code != 200:
                print(f"Ошибка отправки уведомления в Telegram, статус: {response.status_code}")
        except Exception as e:
            print(f"Ошибка отправки уведомления в Telegram: {e}")
    
    def mark_task_completed(self, task):
        """Отмечает задачу как выполненную"""
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
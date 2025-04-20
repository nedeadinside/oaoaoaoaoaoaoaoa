import os
import sys
import threading
from dotenv import find_dotenv, load_dotenv

from src import DatabaseManager
from ui import UiDialog, Menu, LoginDialog
from tg_bot import bot_dispatcher

from PySide6.QtWidgets import QDialog, QApplication
from PySide6.QtGui import QIcon


load_dotenv(find_dotenv())
DB_PATH = os.getenv("DB_PATH")
ICON_PATH = os.getenv("ICON_PATH")
MAIL_ADDR = os.getenv("MAIL_ADDR")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

BOT_TOKEN = os.getenv("BOT_TOKEN")


def main_app():
    app = QApplication(sys.argv)
    dialog_form = UiDialog()
    app.setWindowIcon(QIcon(ICON_PATH))

    db = DatabaseManager(DB_PATH)
    login_dialog = LoginDialog(database=db)

    credentials = None
    while not credentials and not login_dialog.exit:
        if login_dialog.exec() == QDialog.Accepted:
            credentials = login_dialog._validate_credentials()

    if not credentials:
        sys.exit(0)

    dialog = Menu(
        db, dialog_form, credentials["user_id"], credentials["username"], ICON_PATH
    )
    dialog.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    thr1 = threading.Thread(target=bot_dispatcher, daemon=True)
    thr2 = threading.Thread(target=main_app)

    thr1.start()
    thr2.start()

    thr2.join()

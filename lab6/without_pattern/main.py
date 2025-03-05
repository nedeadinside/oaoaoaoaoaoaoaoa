from src.class_logic import MovieManager
from src.ui import MoviePlayerUI
import sys
import os

from PySide6.QtWidgets import QApplication

from dotenv import load_dotenv, find_dotenv

find_dotenv('.env')
load_dotenv()

PATH = os.getenv("MOVIES_WITHOUT_PATTERN")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    movie_manager = MovieManager(PATH)
    ui = MoviePlayerUI(movie_manager)
    ui.show()
    sys.exit(app.exec())
from dotenv import load_dotenv, find_dotenv
from src.class_logic import MovieManager
from src.ui import MoviePlayerUI
import sys
import os

from PySide6.QtWidgets import QApplication

find_dotenv('.env')
load_dotenv()

PATH = os.getenv("MOVIES_PATH")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    movie_player = MovieManager(PATH)
    window = MoviePlayerUI(movie_player)
    sys.exit(app.exec())
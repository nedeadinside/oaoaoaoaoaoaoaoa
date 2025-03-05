from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QPushButton, QSlider, QVBoxLayout
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtUiTools import QUiLoader

from dotenv import load_dotenv, find_dotenv
import os

find_dotenv('.env')
load_dotenv()
UI = os.getenv("UI_WITHOUT_PATTERN")


class MoviePlayerUI(QWidget):
    def __init__(self, movie_manager):
        super().__init__()
        self.movie_manager = movie_manager
        self.current_movie = None
        self.current_lang = None
        self.subtitles = None

        loader = QUiLoader()
        self.ui = loader.load(UI)

        self.setFixedSize(self.ui.size())

        self.video_canvas = self.ui.findChild(QWidget, "VideoCanvas")
        self.sub_canvas = self.ui.findChild(QWidget, "SubCanvas")
        self.film_combo = self.ui.findChild(QComboBox, "FilmComboBox")
        self.lang_combo = self.ui.findChild(QComboBox, "LanguageComboBox")
        self.play_button = self.ui.findChild(QPushButton, "PlayPushButton")
        self.pause_button = self.ui.findChild(QPushButton, "PausePushButton")
        self.volume_slider = self.ui.findChild(QSlider, "VolumeSlider")
        self.film_slider = self.ui.findChild(QSlider, "FilmSlider")

        self.video_widget = QVideoWidget(self.video_canvas)
        self.video_widget.setGeometry(self.video_canvas.rect())

        self.subtitle_label = QLabel(self.sub_canvas)
        self.subtitle_label.setGeometry(self.sub_canvas.rect())
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.5); color: white; font-family: Consolas; font-size: 24px; font-weight: bold;"
        )

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        self.audio_output.setVolume(0.5)
        self.volume_slider.setValue(50)

        self.timer = QTimer(self)
        self.timer.setInterval(100)

        self.film_combo.currentTextChanged.connect(self._on_movie_change)
        self.lang_combo.currentTextChanged.connect(self._on_lang_change)
        self.play_button.clicked.connect(self._play_movie)
        self.pause_button.clicked.connect(self.media_player.pause)
        self.volume_slider.valueChanged.connect(self._set_volume)
        self.film_slider.sliderMoved.connect(self._seek)
        self.media_player.positionChanged.connect(self._update_position)
        self.media_player.durationChanged.connect(self._update_duration)
        self.timer.timeout.connect(self._update_subtitles)

        self._load_movies()

        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
        self.setLayout(layout)

    def _load_movies(self):
        self.film_combo.clear()
        for movie in self.movie_manager.get_movie_list():
            languages = self.movie_manager.get_languages(movie)
            for lang in languages:
                combo_text = f"{movie}_{lang}"
                self.film_combo.addItem(combo_text)
    
    def _on_movie_change(self, combo_text):
        if not combo_text:
            return
        parts = combo_text.split("_")
        if len(parts) != 2:
            return
        
        self.current_movie, self.current_lang_video = parts 

        video_path = self.movie_manager.get_video_path(self.current_movie, self.current_lang_video)
        self.media_player.setSource(QUrl.fromLocalFile(video_path))

        subtitle_langs = self.movie_manager.get_languages(self.current_movie)
        self.lang_combo.clear()
        self.lang_combo.addItems(subtitle_langs)
        if subtitle_langs:
            self.lang_combo.setCurrentIndex(0)

    def _on_lang_change(self, lang_sub):
        if not self.current_movie or not lang_sub:
            return
        self.subtitles = self.movie_manager.load_subtitles(self.current_movie, lang_sub)
        if self.subtitles and self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.timer.start()
    
    def _play_movie(self):
        if not self.current_movie or not self.current_lang_video:
            return
        self.media_player.play()
        if self.subtitles:
            self.timer.start()

    def _set_volume(self, value):
        self.audio_output.setVolume(value / 100.0)

    def _seek(self, position):
        self.media_player.setPosition(position)

    def _update_position(self, position):
        if not self.film_slider.isSliderDown():
            self.film_slider.setValue(position)

    def _update_duration(self, duration):
        self.film_slider.setRange(0, duration)

    def _update_subtitles(self):
        if not self.subtitles:
            self.subtitle_label.clear()
            return
        position = self.media_player.position()
        for sub in self.subtitles:
            if sub.start.ordinal <= position <= sub.end.ordinal:
                self.subtitle_label.setText(sub.text)
                return
        self.subtitle_label.clear()
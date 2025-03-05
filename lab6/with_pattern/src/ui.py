from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QPushButton, QSlider, QVBoxLayout
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader

from dotenv import load_dotenv, find_dotenv
import os

find_dotenv('.env')
load_dotenv()
UI = os.getenv("UI_WITH_PATTERN")


class MoviePlayerUI(QWidget):
    def __init__(self, movie_player):
        super().__init__()
        self.movie_player = movie_player

        loader = QUiLoader()
        self.ui = loader.load(UI)

        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
        self.setLayout(layout)
        self.setFixedSize(self.ui.size())

        self._setup_widgets()
        self._setup_media_player()

        # Таймер для обновления субтитров
        self.timer = QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_subtitle)
        self.subs = None

        self._connect_signals()
        self.populate_movie_list()
        self.show()


    def _setup_widgets(self):
        self.VideoCanvas = self.ui.findChild(QWidget, "VideoCanvas")
        self.video_widget = QVideoWidget(self.VideoCanvas)
        self.video_widget.setGeometry(self.VideoCanvas.rect())

        self.SubCanvas = self.ui.findChild(QWidget, "SubCanvas")
        self.subtitle_label = QLabel(self.SubCanvas)
        self.subtitle_label.setGeometry(self.SubCanvas.rect())
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.5); color: white; font-family: Consolas; font-size: 24px; font-weight: bold;"
        )

        self.FilmComboBox = self.ui.findChild(QComboBox, "FilmComboBox")
        self.LanguageComboBox = self.ui.findChild(QComboBox, "LanguageComboBox")
        self.PlayPushButton = self.ui.findChild(QPushButton, "PlayPushButton")
        self.PausePushButton = self.ui.findChild(QPushButton, "PausePushButton")
        self.VolumeSlider = self.ui.findChild(QSlider, "VolumeSlider")
        self.FilmSlider = self.ui.findChild(QSlider, "FilmSlider")


    def _setup_media_player(self):
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)
        self.VolumeSlider.setValue(50)
        self.media_player.setVideoOutput(self.video_widget)


    def _connect_signals(self):
        self.FilmComboBox.currentIndexChanged.connect(self.on_movie_selected)
        self.LanguageComboBox.currentIndexChanged.connect(self.on_language_selected)
        self.PlayPushButton.clicked.connect(self.play_movie)
        self.PausePushButton.clicked.connect(self.media_player.pause)
        self.FilmSlider.sliderMoved.connect(self.seek_video)
        self.VolumeSlider.valueChanged.connect(self.adjust_volume)
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)


    def populate_movie_list(self):
        for movie_name in self.movie_player.get_available_movies():
            self.FilmComboBox.addItem(movie_name)


    def on_movie_selected(self, index):
        self.movie_name = self.FilmComboBox.itemText(index)
        
        self.LanguageComboBox.blockSignals(True)
        self.LanguageComboBox.clear()
        languages = self.movie_player.get_available_languages(self.movie_name)
        for lang in languages:
            self.LanguageComboBox.addItem(lang)
        self.LanguageComboBox.blockSignals(False)
        
        self.language = self.LanguageComboBox.currentText()


    def on_language_selected(self, index):
        new_language = self.LanguageComboBox.itemText(index)
        if self.movie_name and new_language != self.language:
            current_position = self.media_player.position()
            is_playing = self.media_player.playbackState() == QMediaPlayer.PlayingState

            self.language = new_language
            movie = self.movie_player.create_movie(self.movie_name, self.language)
            self.media_player.setSource(QUrl.fromLocalFile(movie.get_video_path()))
            subtitles = self.movie_player.create_subtitles(self.movie_name, self.language)
            self.subs = subtitles.get_subtitles() if subtitles else None

            self.media_player.mediaStatusChanged.connect(
                lambda status: self.restore_state(status, current_position, is_playing)
            )
            if self.subs:
                self.timer.start()
            else:
                self.timer.stop()
                self.subtitle_label.clear()
        else:
            self.language = new_language


    def restore_state(self, status, position, is_playing):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.media_player.setPosition(position)
            if is_playing:
                self.media_player.play()
            self.media_player.mediaStatusChanged.disconnect()


    def play_movie(self):
        if self.media_player.playbackState() == QMediaPlayer.PausedState:
            self.media_player.play()
            if self.subs:
                self.timer.start()
            return

        movie = self.movie_player.create_movie(self.movie_name, self.language)
        self.media_player.setSource(QUrl.fromLocalFile(movie.get_video_path()))
        subtitles = self.movie_player.create_subtitles(self.movie_name, self.language)
        self.subs = subtitles.get_subtitles() if subtitles else None

        self.media_player.play()
        if self.subs and len(self.subs) > 0:
            self.timer.start()
        else:
            self.subtitle_label.clear()
            self.timer.stop()


    def update_subtitle(self):
        if not self.subs:
            return
        current_ms = self.media_player.position()
        for item in self.subs:
            if item.start.ordinal <= current_ms <= item.end.ordinal:
                self.subtitle_label.setText(item.text)
                return
        self.subtitle_label.setText("")


    def seek_video(self, position):
        self.media_player.setPosition(position)


    def adjust_volume(self, value):
        self.audio_output.setVolume(value / 100.0)


    def position_changed(self, position):
        if not self.FilmSlider.isSliderDown():
            self.FilmSlider.setValue(position)
            
            
    def duration_changed(self, duration):
        self.FilmSlider.setRange(0, duration)


    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.timer.stop()
            self.subtitle_label.clear()


    def closeEvent(self, event):
        QApplication.quit()
        event.accept()
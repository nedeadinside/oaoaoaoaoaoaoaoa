import sys
import torch
import numpy as np

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QImage

from form import Ui_MainWindow, DrawingWidget
from model import CNN


class MainApplication(QMainWindow):
    probabilities_updated = Signal(list)

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.drawing_widget = DrawingWidget(self, canvas_size=740)
        self.drawing_widget.setGeometry(self.ui.frame.geometry())
        self.ui.frame.setVisible(False)
        self.recognition_timer = QTimer(self)
        self.recognition_timer.setInterval(1)
        self.recognition_timer.setSingleShot(True)
        self.drawing_widget.drawing_updated.connect(self.recognition_timer.start)
        self.recognition_timer.timeout.connect(self.recognize_drawing)

        self.model = CNN()
        self.model.load_model(r".\cnn_mnist.pth")

        self.ui.clearButton.clicked.connect(self.on_clear)

        self.progress_bars = [
            self.ui.progressBar_0,
            self.ui.progressBar_1,
            self.ui.progressBar_2,
            self.ui.progressBar_3,
            self.ui.progressBar_4,
            self.ui.progressBar_5,
            self.ui.progressBar_6,
            self.ui.progressBar_7,
            self.ui.progressBar_8,
            self.ui.progressBar_9,
        ]

        self.reset_probabilities()
        self.probabilities_updated.connect(self.update_probabilities)

    def on_clear(self):
        self.drawing_widget.clear()
        self.reset_probabilities()

    def reset_probabilities(self):
        for progress_bar in self.progress_bars:
            progress_bar.setValue(0)

    def convert_canvas_to_mnist_tensor(self, target_size=28):
        pixmap = self.drawing_widget.canvas
        img = pixmap.toImage().convertToFormat(QImage.Format_Grayscale8)
        small = img.scaled(
            target_size, target_size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )
        ptr = small.bits().tobytes()
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((target_size, target_size)).astype(np.float32) / 255.0
        tensor = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0)
        return tensor

    def recognize_drawing(self):
        tensor = self.convert_canvas_to_mnist_tensor()
        probabilities_tensor = self.model.predict_proba(tensor)
        probabilities = list(map(lambda x: round(x * 100, 2), probabilities_tensor.cpu().numpy().flatten().tolist()))
        self.probabilities_updated.emit(probabilities)

    def update_probabilities(self, probabilities):
        for i, probability in enumerate(probabilities):
            self.progress_bars[i].setValue(probability)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApplication()
    window.show()
    sys.exit(app.exec())

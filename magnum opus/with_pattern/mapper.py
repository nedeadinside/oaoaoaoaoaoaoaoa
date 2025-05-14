from PySide6.QtCore import QObject, QTimer, Qt, Signal
from PySide6.QtGui import QImage
import numpy as np
import torch

class Mapper(QObject):
    probabilities_updated = Signal(list)

    def __init__(self, drawing_widget, model, parent=None):
        super().__init__(parent)
        self.drawing_widget = drawing_widget
        self.model = model
        
        self.timer = QTimer(self)
        self.timer.setInterval(1)
        self.timer.setSingleShot(True)
        self.drawing_widget.drawing_updated.connect(self.timer.start)
        self.timer.timeout.connect(self.map)

    def map(self):
        tensor = self.convert_canvas_to_mnist_tensor()
        probabilities_tensor = self.model.predict_proba(tensor)

        probabilities = list(map(lambda x: round(x * 100, 2), 
                                 probabilities_tensor.cpu().numpy().flatten().tolist()))
        self.probabilities_updated.emit(probabilities)

    def convert_canvas_to_mnist_tensor(self, target_size=28):
        pixmap = self.drawing_widget.canvas
        img = pixmap.toImage().convertToFormat(QImage.Format_Grayscale8)
        small = img.scaled(target_size, target_size,
                           Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        ptr = small.bits().tobytes()
        arr = np.frombuffer(ptr, dtype=np.uint8)
        arr = arr.reshape((target_size, target_size)).astype(np.float32) / 255.0
        tensor = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0)
        return tensor

    def clear_drawing_widget(self):
        self.drawing_widget.clear()
        
    def set_geometry(self, geometry):
        self.drawing_widget.setGeometry(geometry)
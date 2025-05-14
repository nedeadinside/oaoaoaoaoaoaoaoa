import sys
import os

from model import CNN
from mapper import Mapper
from form import Ui_MainWindow, DrawingWidget
from PySide6.QtWidgets import QApplication, QMainWindow

class MainApplication(QMainWindow):
    def __init__(self, mapper: Mapper):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.mapper = mapper
        
        self.mapper.set_geometry(self.ui.frame.geometry())
        self.ui.frame.setVisible(False)
        
        self.mapper.probabilities_updated.connect(self.update_probabilities)

        self.ui.clearButton.clicked.connect(self.mapper.clear_drawing_widget)
        self.ui.clearButton.clicked.connect(self.reset_probabilities)

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

    def reset_probabilities(self):
        for bar in self.progress_bars:
            bar.setValue(0)

    def update_probabilities(self, probabilities):
        for i, val in enumerate(probabilities):
            self.progress_bars[i].setValue(val)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    drawing_widget = DrawingWidget(parent=None, canvas_size=740)
    
    model = CNN()
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cnn_mnist.pth'))
    model.load_model(model_path)

    mapper = Mapper(drawing_widget, model)
    
    window = MainApplication(mapper)
    drawing_widget.setParent(window)
    
    window.show()
    sys.exit(app.exec())
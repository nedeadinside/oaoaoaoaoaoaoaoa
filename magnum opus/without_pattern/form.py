from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPixmap,
    QPen,
)
from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QLCDNumber,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QWidget,
)


class DrawingWidget(QWidget):
    drawing_updated = Signal()

    def __init__(self, parent=None, canvas_size=740):
        super().__init__(parent)
        self.setFixedSize(canvas_size, canvas_size)
        self.canvas = QPixmap(canvas_size, canvas_size)
        self.canvas.fill(Qt.black)
        self.last_point = QPoint()
        self.cell_size = canvas_size / 28

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)
        painter.drawPixmap(0, 0, self.canvas)
        grid_pen = QPen(Qt.darkGray, 1)
        grid_pen.setCosmetic(True)
        painter.setPen(grid_pen)
        step = self.width() / 28
        for i in range(1, 28):
            x = int(i * step)
            painter.drawLine(x, 0, x, self.height())
            painter.drawLine(0, x, self.width(), x)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_point = event.position().toPoint()
            self.draw_pixel(self.last_point)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            pos = event.position().toPoint()
            self.draw_pixel(pos)
            self.last_point = pos

    def clear(self):
        self.canvas.fill(Qt.black)
        self.update()

    def draw_pixel(self, point):
        gx = int(point.x() // self.cell_size)
        gy = int(point.y() // self.cell_size)
        painter = QPainter(self.canvas)
        painter.setPen(Qt.NoPen)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = gx + dx, gy + dy
                if 0 <= nx < 28 and 0 <= ny < 28:
                    x0 = int(nx * self.cell_size)
                    y0 = int(ny * self.cell_size)
                    if dx == 0 and dy == 0:
                        color = QColor(255, 255, 255)
                    elif abs(dx) + abs(dy) == 1:
                        color = QColor(255, 255, 255, 40)
                    else:
                        color = QColor(255, 255, 255, 20)
                    painter.setBrush(color)
                    painter.drawRect(x0, y0, int(self.cell_size), int(self.cell_size))
        painter.end()
        self.update()
        self.drawing_updated.emit()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("ПУПУУПУПУПУПУПУПУПУПУПУПУПУПУПУП")
        MainWindow.resize(1280, 860)
        MainWindow.setMinimumSize(QSize(1280, 860))
        MainWindow.setMaximumSize(QSize(1280, 860))
        MainWindow.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        MainWindow.setAnimated(False)
        MainWindow.setDocumentMode(False)
        MainWindow.setTabShape(QTabWidget.TabShape.Rounded)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName("frame")
        self.frame.setGeometry(QRect(520, 40, 740, 740))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.clearButton = QPushButton(self.centralwidget)
        self.clearButton.setObjectName("clearButton")
        self.clearButton.setGeometry(QRect(790, 800, 241, 41))
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName("widget")
        self.widget.setGeometry(QRect(20, 20, 461, 782))
        self.formLayout = QFormLayout(self.widget)
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout.setFormAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout.setHorizontalSpacing(10)
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.lcdNumber_0 = QLCDNumber(self.widget)
        self.lcdNumber_0.setObjectName("lcdNumber_0")
        self.lcdNumber_0.setMinimumSize(QSize(60, 60))
        self.lcdNumber_0.setMaximumSize(QSize(60, 60))
        self.lcdNumber_0.setDigitCount(1)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lcdNumber_0)
        self.progressBar_0 = QProgressBar(self.widget)
        self.progressBar_0.setObjectName("progressBar_0")
        self.progressBar_0.setMinimumSize(QSize(0, 60))
        self.progressBar_0.setValue(0)
        self.progressBar_0.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.progressBar_0.setStyleSheet(
            """
            QProgressBar {
            text-align: right;
            margin-right: 30px;
            }
            QProgressBar::chunk {
            background-color: #56a866;
            width: 5px;
            margin: 0px;
            }
            """
        )

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.progressBar_0)

        self.lcdNumber_1 = QLCDNumber(self.widget)
        self.lcdNumber_1.setObjectName("lcdNumber_1")
        self.lcdNumber_1.setMinimumSize(QSize(60, 60))
        self.lcdNumber_1.setMaximumSize(QSize(60, 60))
        self.lcdNumber_1.setDigitCount(1)
        self.lcdNumber_1.setProperty("intValue", 1)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lcdNumber_1)

        self.progressBar_1 = QProgressBar(self.widget)
        self.progressBar_1.setObjectName("progressBar_1")
        self.progressBar_1.setMinimumSize(QSize(0, 60))
        self.progressBar_1.setValue(0)
        self.progressBar_1.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.progressBar_1.setStyleSheet(
            """
            QProgressBar {
            text-align: right;
            margin-right: 30px;
            }
            QProgressBar::chunk {
            background-color: #56a866;
            width: 5px;
            margin: 0px;
            }
            """
        )

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.progressBar_1)

        self.lcdNumber_2 = QLCDNumber(self.widget)
        self.lcdNumber_2.setObjectName("lcdNumber_2")
        self.lcdNumber_2.setMinimumSize(QSize(60, 60))
        self.lcdNumber_2.setMaximumSize(QSize(60, 60))
        self.lcdNumber_2.setDigitCount(1)
        self.lcdNumber_2.setProperty("intValue", 2)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lcdNumber_2)

        self.progressBar_2 = QProgressBar(self.widget)
        self.progressBar_2.setObjectName("progressBar_2")
        self.progressBar_2.setMinimumSize(QSize(0, 60))
        self.progressBar_2.setValue(0)
        self.progressBar_2.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.progressBar_2.setStyleSheet(
            """
            QProgressBar {
            text-align: right;
            margin-right: 30px;
            }
            QProgressBar::chunk {
            background-color: #56a866;
            width: 5px;
            margin: 0px;
            }
            """
        )

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.progressBar_2)

        self.lcdNumber_3 = QLCDNumber(self.widget)
        self.lcdNumber_3.setObjectName("lcdNumber_3")
        self.lcdNumber_3.setMinimumSize(QSize(60, 60))
        self.lcdNumber_3.setMaximumSize(QSize(60, 60))
        self.lcdNumber_3.setDigitCount(1)
        self.lcdNumber_3.setProperty("intValue", 3)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lcdNumber_3)

        self.progressBar_3 = QProgressBar(self.widget)
        self.progressBar_3.setObjectName("progressBar_3")
        self.progressBar_3.setMinimumSize(QSize(0, 60))
        self.progressBar_3.setValue(0)
        self.progressBar_3.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.progressBar_3.setStyleSheet(
            """
            QProgressBar {
            text-align: right;
            margin-right: 30px;
            }
            QProgressBar::chunk {
            background-color: #56a866;
            width: 5px;
            margin: 0px;
            }
            """
        )

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.progressBar_3)

        self.lcdNumber_4 = QLCDNumber(self.widget)
        self.lcdNumber_4.setObjectName("lcdNumber_4")
        self.lcdNumber_4.setMinimumSize(QSize(60, 60))
        self.lcdNumber_4.setMaximumSize(QSize(60, 60))
        self.lcdNumber_4.setDigitCount(1)
        self.lcdNumber_4.setProperty("intValue", 4)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lcdNumber_4)

        self.progressBar_4 = QProgressBar(self.widget)
        self.progressBar_4.setObjectName("progressBar_4")
        self.progressBar_4.setMinimumSize(QSize(0, 60))
        self.progressBar_4.setValue(0)
        self.progressBar_4.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.progressBar_4.setStyleSheet(
            """
            QProgressBar {
            text-align: right;
            margin-right: 30px;
            }
            QProgressBar::chunk {
            background-color: #56a866;
            width: 5px;
            margin: 0px;
            }
            """
        )

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.progressBar_4)

        self.lcdNumber_5 = QLCDNumber(self.widget)
        self.lcdNumber_5.setObjectName("lcdNumber_5")
        self.lcdNumber_5.setMinimumSize(QSize(60, 60))
        self.lcdNumber_5.setMaximumSize(QSize(60, 60))
        self.lcdNumber_5.setDigitCount(1)
        self.lcdNumber_5.setProperty("intValue", 5)

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lcdNumber_5)

        self.progressBar_5 = QProgressBar(self.widget)
        self.progressBar_5.setObjectName("progressBar_5")
        self.progressBar_5.setMinimumSize(QSize(0, 60))
        self.progressBar_5.setValue(0)
        self.progressBar_5.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.progressBar_5.setStyleSheet(
            """
            QProgressBar {
            text-align: right;
            margin-right: 30px;
            }
            QProgressBar::chunk {
            background-color: #56a866;
            width: 5px;
            margin: 0px;
            }
            """
        )

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.progressBar_5)

        self.lcdNumber_6 = QLCDNumber(self.widget)
        self.lcdNumber_6.setObjectName("lcdNumber_6")
        self.lcdNumber_6.setMinimumSize(QSize(60, 60))
        self.lcdNumber_6.setMaximumSize(QSize(60, 60))
        self.lcdNumber_6.setDigitCount(1)
        self.lcdNumber_6.setProperty("intValue", 6)

        self.formLayout.setWidget(6, QFormLayout.ItemRole.LabelRole, self.lcdNumber_6)

        self.progressBar_6 = QProgressBar(self.widget)
        self.progressBar_6.setObjectName("progressBar_6")
        self.progressBar_6.setMinimumSize(QSize(0, 60))
        self.progressBar_6.setValue(0)
        self.progressBar_6.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.progressBar_6.setStyleSheet(
            """
            QProgressBar {
            text-align: right;
            margin-right: 30px;
            }
            QProgressBar::chunk {
            background-color: #56a866;
            width: 5px;
            margin: 0px;
            }
            """
        )

        self.formLayout.setWidget(6, QFormLayout.ItemRole.FieldRole, self.progressBar_6)

        self.lcdNumber_7 = QLCDNumber(self.widget)
        self.lcdNumber_7.setObjectName("lcdNumber_7")
        self.lcdNumber_7.setMinimumSize(QSize(60, 60))
        self.lcdNumber_7.setMaximumSize(QSize(60, 60))
        self.lcdNumber_7.setDigitCount(1)
        self.lcdNumber_7.setProperty("intValue", 7)

        self.formLayout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.lcdNumber_7)

        self.progressBar_7 = QProgressBar(self.widget)
        self.progressBar_7.setObjectName("progressBar_7")
        self.progressBar_7.setMinimumSize(QSize(0, 60))
        self.progressBar_7.setValue(0)
        self.progressBar_7.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.progressBar_7.setStyleSheet(
            """
            QProgressBar {
            text-align: right;
            margin-right: 30px;
            }
            QProgressBar::chunk {
            background-color: #56a866;
            width: 5px;
            margin: 0px;
            }
            """
        )

        self.formLayout.setWidget(7, QFormLayout.ItemRole.FieldRole, self.progressBar_7)

        self.lcdNumber_8 = QLCDNumber(self.widget)
        self.lcdNumber_8.setObjectName("lcdNumber_8")
        self.lcdNumber_8.setMinimumSize(QSize(60, 60))
        self.lcdNumber_8.setMaximumSize(QSize(60, 60))
        self.lcdNumber_8.setDigitCount(1)
        self.lcdNumber_8.setProperty("intValue", 8)

        self.formLayout.setWidget(8, QFormLayout.ItemRole.LabelRole, self.lcdNumber_8)

        self.progressBar_8 = QProgressBar(self.widget)
        self.progressBar_8.setObjectName("progressBar_8")
        self.progressBar_8.setMinimumSize(QSize(0, 60))
        self.progressBar_8.setValue(0)
        self.progressBar_8.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.progressBar_8.setStyleSheet(
            """
            QProgressBar {
            text-align: right;
            margin-right: 30px;
            }
            QProgressBar::chunk {
            background-color: #56a866;
            width: 5px;
            margin: 0px;
            }
            """
        )

        self.formLayout.setWidget(8, QFormLayout.ItemRole.FieldRole, self.progressBar_8)

        self.lcdNumber_9 = QLCDNumber(self.widget)
        self.lcdNumber_9.setObjectName("lcdNumber_9")
        self.lcdNumber_9.setMinimumSize(QSize(60, 60))
        self.lcdNumber_9.setMaximumSize(QSize(60, 60))
        self.lcdNumber_9.setDigitCount(1)
        self.lcdNumber_9.setProperty("intValue", 9)

        self.formLayout.setWidget(9, QFormLayout.ItemRole.LabelRole, self.lcdNumber_9)

        self.progressBar_9 = QProgressBar(self.widget)
        self.progressBar_9.setObjectName("progressBar_9")
        self.progressBar_9.setMinimumSize(QSize(60, 60))
        self.progressBar_9.setValue(0)
        self.progressBar_9.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.progressBar_9.setStyleSheet(
            """
            QProgressBar {
            text-align: right;
            margin-right: 30px;
            }
            QProgressBar::chunk {
            background-color: #56a866;
            width: 5px;
            margin: 0px;
            }
            """
        )

        self.formLayout.setWidget(9, QFormLayout.ItemRole.FieldRole, self.progressBar_9)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MainWindow", None)
        )
        self.clearButton.setText(
            QCoreApplication.translate(
                "MainWindow", "Очистить", None
            )
        )

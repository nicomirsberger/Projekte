import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, QScrollArea)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt


class BildBetrachter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mein PyQt Bildbetrachter")
        self.resize(800, 600)

        # Icon für das Fenster (Titelleiste)
        icon_path = '/Users/student/Downloads/icon_eye.png'
        self.setWindowIcon(QIcon(icon_path))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # --- Button Layout (Nebeneinander statt untereinander) ---
        button_layout = QHBoxLayout()

        self.btn_open = QPushButton("Bild öffnen")
        self.btn_open.clicked.connect(self.open_image)

        self.btn_zoom_in = QPushButton("Zoom (+)")
        self.btn_zoom_in.clicked.connect(lambda: self.zoom_image(1.2))

        self.btn_zoom_out = QPushButton("Zoom (-)")
        self.btn_zoom_out.clicked.connect(lambda: self.zoom_image(0.8))

        button_layout.addWidget(self.btn_open)
        button_layout.addWidget(self.btn_zoom_in)
        button_layout.addWidget(self.btn_zoom_out)

        layout.addLayout(button_layout)

        # --- Bildbereich ---
        self.image_label = QLabel("Kein Bild ausgewählt")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # WICHTIG: Transparenz für Label UND ScrollArea
        self.image_label.setStyleSheet("background-color: transparent;")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        # Macht den Rahmen der ScrollArea unsichtbar/transparent (Mac-Style)
        self.scroll_area.setStyleSheet("background-color: transparent; border: none;")

        layout.addWidget(self.scroll_area)

        self.pixmap = None
        self.zoom_factor = 1.0

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Bild öffnen", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.pixmap = QPixmap(file_path)
            self.zoom_factor = 1.0
            self.update_display()

    def zoom_image(self, factor):
        if self.pixmap:
            self.zoom_factor *= factor
            self.update_display()

    def update_display(self):
        if self.pixmap:
            new_width = int(self.pixmap.width() * self.zoom_factor)
            new_height = int(self.pixmap.height() * self.zoom_factor)
            scaled_pixmap = self.pixmap.scaled(new_width, new_height,
                                               Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.adjustSize()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Icon für das Dock setzen (macOS)
    app.setWindowIcon(QIcon('/Users/student/Downloads/icon_eye.icns'))

    window = BildBetrachter()
    window.show()
    sys.exit(app.exec())
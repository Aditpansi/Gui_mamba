from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QGridLayout, QToolButton
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("MomentuX Systems GUI")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #f5f5f5;")  # Light background color

        # Central widget setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Header layout
        header_layout = QHBoxLayout()
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_frame.setStyleSheet("border: 1px solid black;")
        header_frame.setLayout(header_layout)
        
        # Bluetooth icon button on the left
        bluetooth_button = QToolButton()
        bluetooth_button.setIcon(QIcon('icons/bluetooth-icon.png'))  # Replace with your icon path
        bluetooth_button.setIconSize(Qt.QSize(32, 32))
        header_layout.addWidget(bluetooth_button, alignment=Qt.AlignLeft)

        # MomentuX logo in the center
        title_label = QLabel("MomentuX\nSYSTEMS")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_label)

        # Menu button on the right
        menu_button = QToolButton()
        menu_button.setIcon(QIcon('icons/menu-icon.png'))  # Replace with your icon path
        menu_button.setIconSize(Qt.QSize(32, 32))
        header_layout.addWidget(menu_button, alignment=Qt.AlignRight)

        main_layout.addWidget(header_frame)

        # Content area with three panels layout
        content_layout = QHBoxLayout()
        for _ in range(3):
            panel = QFrame()
            panel.setFrameShape(QFrame.StyledPanel)
            panel.setStyleSheet("border: 1px solid black;")
            content_layout.addWidget(panel)
        
        main_layout.addLayout(content_layout)

        # Button layout at the bottom
        button_layout = QHBoxLayout()

        start_button = QPushButton("START")
        start_button.setFont(QFont("Arial", 14))
        start_button.setStyleSheet("""
            background-color: white;
            border: 1px solid black;
            border-radius: 15px;
            padding: 10px 30px;
        """)
        button_layout.addWidget(start_button)

        stop_button = QPushButton("STOP")
        stop_button.setFont(QFont("Arial", 14))
        stop_button.setStyleSheet("""
            background-color: white;
            border: 1px solid black;
            border-radius: 15px;
            padding: 10px 30px;
        """)
        button_layout.addWidget(stop_button)

        main_layout.addLayout(button_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

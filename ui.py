# import sys
# from PyQt5.QtWidgets import (
#     QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
#     QPushButton, QToolButton, QFrame , QLabel
# )
# from PyQt5.QtCore import QSize, Qt
# from PyQt5.QtGui import QIcon,QFont

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         # Set up the main window
#         self.setWindowTitle("MomentuX Systems GUI")
#         self.setGeometry(100, 100, 800, 600)
#         self.setStyleSheet("background-color: #f5f5f5;")  # Light background color

#         # Central widget setup
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#         main_layout = QVBoxLayout()
#         central_widget.setLayout(main_layout)

#         # Header layout
#         header_layout = QHBoxLayout()
#         header_frame = QFrame()
#         header_frame.setFrameShape(QFrame.StyledPanel)
#         header_frame.setStyleSheet("border: 1px solid black;")
#         header_frame.setLayout(header_layout)
        
#         # Bluetooth icon button on the left
#         bluetooth_button = QToolButton()
#         bluetooth_button.setIcon(QIcon('icons/bluetooth-icon.png'))  # Replace with your icon path
#         bluetooth_button.setIconSize(QSize(32, 32))
#         header_layout.addWidget(bluetooth_button, alignment=Qt.AlignLeft)

#         # MomentuX logo in the center
#         title_label = QLabel("MomentuX\nSYSTEMS")
#         title_label.setAlignment(Qt.AlignCenter)
#         title_label.setFont(QFont("Arial", 16, QFont.Bold))
#         header_layout.addWidget(title_label)

#         # Menu button on the right
#         menu_button = QToolButton()
#         menu_button.setIcon(QIcon('icons/menu-icon.png'))  # Replace with your icon path
#         menu_button.setIconSize(QSize(32, 32))
#         header_layout.addWidget(menu_button, alignment=Qt.AlignRight)

#         main_layout.addWidget(header_frame)

#         # Content area with three panels layout
#         content_layout = QHBoxLayout()
#         for _ in range(3):
#             panel = QFrame()
#             panel.setFrameShape(QFrame.StyledPanel)
#             panel.setStyleSheet("border: 1px solid black;")
#             content_layout.addWidget(panel)
        
#         main_layout.addLayout(content_layout)

#         # Button layout at the bottom
#         button_layout = QHBoxLayout()

#         start_button = QPushButton("START")
#         start_button.setFont(QFont("Arial", 14))
#         start_button.setStyleSheet("""
#             background-color: white;
#             border: 1px solid black;
#             border-radius: 15px;
#             padding: 10px 30px;
#         """)
#         button_layout.addWidget(start_button)

#         stop_button = QPushButton("STOP")
#         stop_button.setFont(QFont("Arial", 14))
#         stop_button.setStyleSheet("""
#             background-color: white;
#             border: 1px solid black;
#             border-radius: 15px;
#             padding: 10px 30px;
#         """)
#         button_layout.addWidget(stop_button)

#         main_layout.addLayout(button_layout)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())



from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget

class MomentuXApp(App):
    def build(self):
        # Main vertical layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Top bar layout with Bluetooth icon, logo, and menu button
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=0.2)

        # Bluetooth button on the left
        bluetooth_button = Button(size_hint=(None, None), size=(50, 50), background_normal='icons/bluetooth-icon.png')
        top_bar.add_widget(bluetooth_button)

        # MomentuX logo in the center
        logo = Label(text='[b]MomentuX\nSYSTEMS[/b]', markup=True, font_size='20sp', halign='center', valign='middle')
        top_bar.add_widget(logo)

        # Menu button on the right
        menu_button = Button(size_hint=(None, None), size=(50, 50), background_normal='icons/menu-icon.png')
        top_bar.add_widget(menu_button)

        main_layout.add_widget(top_bar)

        # Content area with three panels layout
        content_layout = BoxLayout(orientation='horizontal', spacing=20)
        for _ in range(3):
            panel = Widget(size_hint=(1, 1), size=(200, 200))
            panel.canvas.before.clear()
            content_layout.add_widget(panel)

        main_layout.add_widget(content_layout)

        # Bottom buttons (Start and Stop)
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, padding=10, spacing=20)

        start_button = Button(text='START', size_hint=(None, None), size=(150, 50), background_normal='', background_color=(0, 1, 0, 1))
        stop_button = Button(text='STOP', size_hint=(None, None), size=(150, 50), background_normal='', background_color=(1, 0, 0, 1))

        button_layout.add_widget(start_button)
        button_layout.add_widget(stop_button)

        main_layout.add_widget(button_layout)

        return main_layout

if __name__ == '__main__':
    MomentuXApp().run()

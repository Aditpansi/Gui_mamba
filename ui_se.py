import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from kivy.garden.matplotlib import FigureCanvasKivyAgg 
from matplotlib import style
import serial.tools.list_ports
import time
import re
import pandas as pd
import asyncio
import threading
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout  
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.properties import NumericProperty, ListProperty
from kivy.graphics import PushMatrix, PopMatrix, Rotate, Color, Rectangle
from kivy.lang import Builder
from kivymd.app import MDApp
from bleak import BleakScanner

# Constants for serial communication
BAUD_RATE = 115200
pattern = r'([^,]+),([^,]+),([^,]+),([^,]+)'  # Matches Timestamp, Roll, Pitch, Yaw


# Function to detect device
def detect_device():
    device_ports = [
        p.device
        for p in serial.tools.list_ports.comports()
        if 'VID:PID' in p.hwid
    ]
    if not device_ports:
        raise IOError("No device found")
    return device_ports[0]

# KivyMD layout for the MainScreen
KV = '''
########################################################################################
                                    #MainScreen
########################################################################################
<DrawerClickableItem@MDNavigationDrawerItem>
    focus_color: "#fffff0"
    text_color: "#4a4939"
    icon_color: "#4a4939"
    ripple_color: "#c5bdd2"
    selected_color: "#0c6c4d"

<DrawerLabelItem@MDNavigationDrawerItem>
    text_color: "#4a4939"
    icon_color: "#4a4939"
    focus_behavior: False
    selected_color: "#4a4939"
    _no_ripple_effect: True

MDScreen:
    MDNavigationLayout:
        MDScreenManager:
            MDScreen:
                MDTopAppBar:
                    title: "MAMBA"
                    elevation: 4
                    pos_hint: {"top": 1}
                    md_bg_color: "#fffff0"
                    specific_text_color: "#4a4939"
                    left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]

        MDNavigationDrawer:
            id: nav_drawer
            radius: (0, 16, 16, 0)

            MDNavigationDrawerMenu:
                MDNavigationDrawerHeader:
                    title: "Momentux"
                    title_color: "#4a4939"
                    text: "Systems"
                    spacing: "4dp"
                    padding: "12dp", 0, 0, "56dp"

                MDNavigationDrawerLabel:
                    text: "Settings"

                MDNavigationDrawerDivider:

                DrawerClickableItem:
                    icon: "cellphone"
                    text: "Device"
                    on_release: app.root.current = 'bluetooth_screen'

                DrawerClickableItem:
                    icon: "chart-line"
                    text: "Graph"
                    on_release: app.root.current = 'graph_screen'  # Navigate to graph screen

                DrawerClickableItem:
                    icon: "close"
                    text: "Close"
                    on_release: nav_drawer.set_state("close") 

########################################################################################
                                    #BluetoothScreen
########################################################################################

<BluetoothScreen>:
    name: 'bluetooth_screen'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size

        CustomTopAppBar:
            title: "Bluetooth Device Connection"
            md_bg_color: "#fffff0"
            specific_text_color: "#4a4939"

            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            right_action_items: [["bluetooth", lambda x: app.scan_for_devices()]]

        MDSpinner:
            id: spinner
            size_hint: None, None
            size: dp(30), dp(30)
            pos_hint: {'center_x': .5, 'center_y': .5}
            active: False  # Initially inactive

        Label:
            text: "Scan for Devices"
            font_size: '24sp'
            bold: True
            color: 1, 1, 1, 1

        Label:
            id: devices_list
            text: "No devices found."
            size_hint: (1, None)
            height: 50
            color: 1, 1, 1, 1  

<DevicesView>:
    viewclass: 'DeviceLabel'
    RecycleView:
        id: rv
        RecycleBoxLayout:
            default_size: None, dp(56)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'

<DeviceLabel>:
    size_hint_y: None
    height: dp(40)
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1  # Optional: Background color for DeviceLabel
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text: root.device_name
        color: 1, 1, 1, 1  # White text color

<CustomTopAppBar@MDTopAppBar>:
    canvas.before:
        Color:
            rgba: 0.2, 0.6, 0.8, 0.5
        Ellipse:
            pos: self.x - dp(20), self.y + self.height/2 - dp(20)
            size: dp(40), dp(40)

########################################################################################
                                    #GraphScreen
########################################################################################

<GraphScreen>:
    name: 'graph_screen'
    BoxLayout:
        orientation: 'vertical'
        
        # Placeholder for the Matplotlib figure widget
        id: plot_area

'''

class BluetoothScreen(Screen):
    def scan_for_devices(self):
        """ Start the Bluetooth device scanning in a separate thread. """
        self.ids.spinner.active = True  # Show the spinner
        threading.Thread(target=self.async_scan_for_devices_wrapper).start()  # Start scanning in a new thread

    def async_scan_for_devices_wrapper(self):
        """ Wrapper to call the async scanning function. """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.async_scan_for_devices())
        loop.close()

    async def async_scan_for_devices(self):
        """ Asynchronously scan for Bluetooth devices. """
        try:
            devices = await BleakScanner.discover()  # Run the scanner
            device_info = [(device.name if device.name else "Unnamed Device", device.address) for device in devices]
            Clock.schedule_once(lambda dt: self.update_device_list(device_info))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(f"Error: {str(e)}"))
        finally:
            Clock.schedule_once(lambda dt: setattr(self.ids.spinner, 'active', False))

    def update_device_list(self, devices):
        devices_list_label = self.ids.devices_list
        if devices:
            formatted_devices = [f"{name} - {address}" for name, address in devices]
            devices_list_label.text = "\n".join(formatted_devices)
        else:
            devices_list_label.text = "No devices found."

    def show_error(self, message):
        """ Show error message in the devices_list label. """
        self.ids.devices_list.text = message


class GraphScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(GraphScreen, self).__init__(**kwargs)

        layout = BoxLayout(orientation='vertical')  # Create a BoxLayout
        # Automatically detect the serial port
        self.serial_port = detect_device()
        self.ser = serial.Serial(self.serial_port, 115200, timeout=1)

        self.x_data = []
        self.pitch_data = []
        self.yaw_data = []

        self.df = pd.DataFrame(columns=['time', 'pitch', 'yaw'])

        # Set up the figure and axes
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(10, 8))

        # Set titles and labels for each subplot
        title_font = {'fontsize': 16}
        label_font = {'fontsize': 14}

        self.ax1.set_title('Pitch (Degrees)', fontdict=title_font)
        self.ax1.set_ylabel('Pitch', fontdict=label_font)
        self.ax1.set_xlim(0, 10)
        self.ax1.set_ylim(-60, 60)
        self.ax1.legend(['Pitch'], loc='upper right')

        self.ax2.set_title('Yaw (Degrees)', fontdict=title_font)
        self.ax2.set_ylabel('Yaw', fontdict=label_font)
        self.ax2.set_xlim(0, 10)
        self.ax2.set_ylim(-60, 60)
        self.ax2.legend(['Yaw'], loc='upper right')

        self.ax3.set_title('Pitch vs Yaw', fontdict=title_font)
        self.ax3.set_xlabel('Yaw', fontdict=label_font)
        self.ax3.set_ylabel('Pitch', fontdict=label_font)
        self.ax3.set_xlim(-60, 60)
        self.ax3.set_ylim(-60, 60)
        self.ax3.legend(['Pitch vs Yaw'], loc='upper right')

        # Create plot lines
        self.pitch_line, = self.ax1.plot([], [], color='green')
        self.yaw_line, = self.ax2.plot([], [], color='blue')
        self.pitch_vs_yaw_line, = self.ax3.plot([], [], color='purple')

        # Create text annotations
        self.pitch_text = self.ax1.text(0.02, 0.95, '', transform=self.ax1.transAxes, fontsize=14, color='green', verticalalignment='top',
                                         bbox=dict(facecolor='white', edgecolor='green', boxstyle='round,pad=0.3', alpha=0.8))
        self.yaw_text = self.ax2.text(0.02, 0.95, '', transform=self.ax2.transAxes, fontsize=14, color='blue', verticalalignment='top',
                                       bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.3', alpha=0.8))
        self.pitch_vs_yaw_text = self.ax3.text(0.02, 0.95, '', transform=self.ax3.transAxes, fontsize=14, color='purple', verticalalignment='top',
                                                bbox=dict(facecolor='white', edgecolor='purple', boxstyle='round,pad=0.3', alpha=0.8))

        # # Add the canvas widget to the BoxLayout in GraphScreen
        # self.canvas_widget = FigureCanvasKivyAgg(self.fig)
        self.add_widget(layout)  

        # Schedule the update function to be called regularly
        Clock.schedule_interval(self.update_plot, 0.05)  # Update every 50 ms

    def read_serial_data(self):
        try:
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"Raw Data: {line}")

            # Match the line with the regex for four comma-separated values
            match = re.match(r'(\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)', line)
            if match:
                timestamp = float(match.group(1)) / 1000.0  # Convert milliseconds to seconds
                roll = float(match.group(2))    # Roll value (not used)
                pitch = float(match.group(3))   # Pitch value
                yaw = float(match.group(4))     # Yaw value
                return timestamp, roll, pitch, yaw
            else:
                return None, None, None, None  # Data format mismatch
        except (ValueError, IndexError) as e:
            return None, None, None, None  # Error handling for conversion issues

    def update_plot(self, dt):
        timestamp, roll, pitch, yaw = self.read_serial_data()

        if timestamp is not None and pitch is not None and yaw is not None:
            # Append data
            self.x_data.append(timestamp)  # Append the timestamp
            self.pitch_data.append(pitch)
            self.yaw_data.append(yaw)

            # Update plot limits dynamically
            self.ax1.set_xlim(max(0, self.x_data[-1] - 10), self.x_data[-1])
            self.ax2.set_xlim(max(0, self.x_data[-1] - 10), self.x_data[-1])
            self.ax3.set_xlim(-60, 60)

            # Update data in the plot lines
            self.pitch_line.set_data(self.x_data, self.pitch_data)
            self.yaw_line.set_data(self.x_data, self.yaw_data)
            self.pitch_vs_yaw_line.set_data(self.yaw_data, self.pitch_data)

            # Update text annotations with the latest values
            self.pitch_text.set_text(f'Pitch: {pitch:.2f}')
            self.yaw_text.set_text(f'Yaw: {yaw:.2f}')
            self.pitch_vs_yaw_text.set_text(f'Pitch vs Yaw: Pitch={pitch:.2f}, Yaw={yaw:.2f}')

            # Update DataFrame with new values
            self.df = pd.concat([self.df, pd.DataFrame({'time': [self.x_data[-1]], 
                                                         'pitch': [pitch],
                                                         'yaw': [yaw]})], ignore_index=True)

        return self.pitch_line, self.yaw_line, self.pitch_vs_yaw_line, self.pitch_text, self.yaw_text, self.pitch_vs_yaw_text

class AnimatedLogo(Widget):
    dummy_angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super(AnimatedLogo, self).__init__(**kwargs)
        with self.canvas:
            self.rotation = Rotate(angle=0, origin=self.center)

        self.image = Image(
            source='/Users/aditpansi/Desktop/Momentux/Momentux_Website/images/Momentux-removebg-preview.png',
            size_hint=(None, None), size=(200, 200)
        )
        self.add_widget(self.image)
        self.bind(pos=self.update_position, size=self.update_position)

    def update_position(self, *args):
        self.image.center = self.center
        self.rotation.origin = self.center

    def on_dummy_angle(self, instance, value):
        self.rotation.angle = value


class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super(SplashScreen, self).__init__(**kwargs)
        with self.canvas:
            Color(0.2, 0.2, 0.2, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.animated_logo = AnimatedLogo()
        self.add_widget(self.animated_logo)

        # Create an animation that updates the dummy_angle property
        animation = Animation(dummy_angle=360, duration=1)
        animation.bind(on_complete=self.on_animation_complete)
        animation.start(self.animated_logo)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_animation_complete(self, *args):
        Clock.schedule_once(self.switch_to_main_screen, 1)

    def switch_to_main_screen(self, dt):
        self.manager.current = 'main_screen'


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        with self.canvas:
            Color(0, 0, 0, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Load the KivyMD layout
        self.layout = Builder.load_string(KV)
        self.add_widget(self.layout)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class MyApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SplashScreen(name='splash_screen'))
        sm.add_widget(MainScreen(name='main_screen'))
        sm.add_widget(BluetoothScreen(name='bluetooth_screen'))  # Add the Bluetooth screen
        sm.add_widget(GraphScreen())  # Add the graph screen
        sm.current = 'splash_screen'
        return sm

    def scan_for_devices(self):
        """ Method to initiate scanning from the app level. """
        self.root.get_screen('bluetooth_screen').scan_for_devices()
    
    def go_back(self):
        self.root.get_screen('main_screen').manager.current = 'main_screen'  # Example logic to go back


if __name__ == '__main__':
    MyApp().run()

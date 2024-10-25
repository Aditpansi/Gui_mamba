import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from kivy.garden.matplotlib import FigureCanvasKivyAgg as FigureCanvas
from matplotlib import style
import serial.tools.list_ports
import time
import re
import pandas as pd
import asyncio
import threading
from kivy.app import App
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.screen import MDScreen
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
                    icon: "information-outline"
                    text: "info"
                    on_release: app.root.current = 'info_screen'  # Navigate to info screen

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

        MDTopAppBar:
            title: "Graph"
            elevation: 4
            md_bg_color: "#fffff0"
            specific_text_color: "#4a4939"
            left_action_items: [["arrow-left", lambda x: app.go_back()]]

        # Placeholder for the Matplotlib figure widget
        BoxLayout:
            id: plot_area
            # Add your matplotlib canvas or other widgets here     

########################################################################################
                                    #InfoScreen
########################################################################################

<InfoScreen>:
    name: 'info_screen'
    BoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Info"
            elevation: 4
            md_bg_color: "#fffff0"
            specific_text_color: "#4a4939"
            left_action_items: [["arrow-left", lambda x: app.go_back()]]   

        Label:
            text: "Information about the application"
            font_size: '24sp'
            color: 1, 1, 1, 1
        Label:
            text: "This application allows you to connect to Bluetooth devices and visualize data."
            size_hint_y: None
            height: self.texture_size[1]  # Adjust height according to text size
            color: 1, 1, 1, 1   
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


class GraphScreen(Screen):
    def __init__(self, **kwargs):
        super(GraphScreen, self).__init__(**kwargs)
        self.graph_initialized = False
        self.ser = None

    def on_enter(self):
        """Initialize the graph when entering the screen."""
        if not self.graph_initialized:
            self.setup_plot()
            self.graph_initialized = True

        if self.ser and self.ser.is_open:
            self.thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.thread.start()
        else:
            print("Serial connection is not established.")

    def setup_plot(self):
        """Set up the Matplotlib plot in the Kivy screen."""
        try:
            self.port = detect_device()  
            self.ser = serial.Serial(self.port, BAUD_RATE)  
            print(f"Serial connection established on port {self.port}")
        except Exception as e:
            print(f"Error initializing serial connection: {e}")
            self.ser = None
            return

        style.use('fivethirtyeight')
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(10, 10))
        self.canvas = FigureCanvas(self.fig)
        self.ids.plot_area.add_widget(self.canvas)

        self.x_data, self.pitch_data, self.yaw_data = [], [], []
        self.df = pd.DataFrame()

        self.pitch_line, = self.ax1.plot([], [], label='Pitch', color='g')
        self.yaw_line, = self.ax2.plot([], [], label='Yaw', color='b')
        self.pitch_vs_yaw_line, = self.ax3.plot([], [], label='Pitch vs Yaw', color='purple')

        self.setup_plot_labels()  # Call the label setup here

        Clock.schedule_interval(self.update_plot, 0.05)  # Schedule plot updates

    def setup_plot_labels(self):
        """Set up labels, titles, and legends for the plots."""
        self.ax1.set_title('Pitch over Time', fontsize=14)
        self.ax1.set_xlabel('Time (s)', fontsize=12)
        self.ax1.set_ylabel('Pitch (degrees)', fontsize=12)
        self.ax1.legend(loc='upper right')

        self.ax2.set_title('Yaw over Time', fontsize=14)
        self.ax2.set_xlabel('Time (s)', fontsize=12)
        self.ax2.set_ylabel('Yaw (degrees)', fontsize=12)
        self.ax2.legend(loc='upper right')

        self.ax3.set_title('Pitch vs Yaw', fontsize=14)
        self.ax3.set_xlabel('Yaw (degrees)', fontsize=12)
        self.ax3.set_ylabel('Pitch (degrees)', fontsize=12)
        self.ax3.legend(loc='upper right')

        self.fig.tight_layout()

    def update_plot(self, dt):
        """Update the plot with the latest serial data."""
        if len(self.x_data) > 0:
            # Update pitch vs time plot
            self.pitch_line.set_data(self.x_data, self.pitch_data)
            self.ax1.relim()
            self.ax1.autoscale_view()

            # Update yaw vs time plot
            self.yaw_line.set_data(self.x_data, self.yaw_data)
            self.ax2.relim()
            self.ax2.autoscale_view()

            # Update pitch vs yaw plot
            self.pitch_vs_yaw_line.set_data(self.yaw_data, self.pitch_data)
            self.ax3.relim()
            self.ax3.autoscale_view()

            # Redraw the canvas with updated data
            self.canvas.draw_idle()

    def read_serial_data(self):
        """Continuously read serial data."""
        while self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    match = re.match(pattern, line)
                    if match:
                        timestamp, roll, pitch, yaw = match.groups()
                        time_value = float(timestamp)
                        self.x_data.append(time_value)
                        self.pitch_data.append(float(pitch))
                        self.yaw_data.append(float(yaw))
            except Exception as e:
                print(f"Error reading serial data: {e}")
                break

    def on_leave(self):
        """Cleanup actions when leaving the GraphScreen."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial connection closed.")
        self.ser = None


class InfoScreen(Screen):
    def __init__(self, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)
        self.add_widget(Label(text="Information Screen", font_size='24sp', color=(1, 1, 1, 1)))


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
        sm.add_widget(GraphScreen(name='graph_screen'))  # Add the graph screen
        sm.add_widget(InfoScreen(name='info_screen'))
        sm.current = 'splash_screen'
        return sm

    def scan_for_devices(self):
        """ Method to initiate scanning from the app level. """
        self.root.get_screen('bluetooth_screen').scan_for_devices()
    
    def go_back(self):
        self.root.current = 'main_screen'


if __name__ == '__main__':
    MyApp().run()

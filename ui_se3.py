from matplotlib import style
import serial.tools.list_ports
import time
import re
import pandas as pd
import asyncio
import threading
from kivy.app import App
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
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
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.properties import NumericProperty, ListProperty
from kivy.graphics import PushMatrix, PopMatrix, Rotate, Color, Rectangle
from kivy.lang import Builder
from kivymd.app import MDApp
from bleak import BleakScanner

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
                    text: "Info"
                    on_release: app.show_info_popup()

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

# <InfoScreen>:
#     name: 'info_screen'
#     BoxLayout:
#         orientation: 'vertical'
#         MDTopAppBar:
#             title: "Info"
#             elevation: 4
#             md_bg_color: "#fffff0"
#             specific_text_color: "#4a4939"
#             left_action_items: [["arrow-left", lambda x: app.go_back()]]   

#         Label:
#             text: "Information about the application"
#             font_size: '24sp'
#             color: 0, 0, 0, 1
#         Label:
#             text: "This application allows you to connect to Bluetooth devices and visualize data."
#             size_hint_y: None
#             height: self.texture_size[1]  # Adjust height according to text size
#             color: 0, 0, 0, 1   
'''
if not hasattr(FigureCanvasKivyAgg, 'resize_event'):
    def resize_event(self):
        pass
    FigureCanvasKivyAgg.resize_event = resize_event
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

port = detect_device()
ser = serial.Serial(port,115200)

# Constants for serial communication

pattern = r'([^,]+),([^,]+),([^,]+),([^,]+)'  # Matches Timestamp, Roll, Pitch, Yaw

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

class CustomFigureCanvasKivyAgg(FigureCanvasKivyAgg):
    def __init__(self, figure, **kwargs):
        super(CustomFigureCanvasKivyAgg, self).__init__(figure, **kwargs)
        
        # Connect the motion notify event to the figure's canvas
        self.mpl_disconnect(self.on_mouse_move)

    def on_mouse_move(self, event):
        """Handle mouse movement over the canvas."""
        try:
            if event.inaxes is not None:
                # Here you can handle mouse movement events
                print(f'Mouse moved to: ({event.xdata}, {event.ydata})')
        except Exception as e:
            print(f"Error in on_mouse_move: {e}")
 
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
            self.ser = serial.Serial(self.port, 115200)  
            print(f"Serial connection established on port {self.port}")
        except Exception as e:
            print(f"Error initializing serial connection: {e}")
            self.ser = None
            return

        style.use('fivethirtyeight')
        self.fig, self.ax = plt.subplots(figsize=(10, 5))  # One subplot for Roll, Pitch, Yaw
        self.canvas = CustomFigureCanvasKivyAgg(self.fig)
        self.ids.plot_area.add_widget(self.canvas)

        self.x_data ,self.roll_data, self.pitch_data, self.yaw_data = [], [], [] , []
        self.df = pd.DataFrame()

        self.line_roll, = self.ax.plot([], [], label='Roll', color='r')
        self.line_pitch, = self.ax.plot([], [], label='Elevation', color='g')
        self.line_yaw, = self.ax.plot([], [], label='Azimuth', color='b')

        # Initialize text annotations
        self.roll_text = self.ax.text(0.02, 0.95, '', transform=self.ax.transAxes, fontsize=14, color='red', verticalalignment='top',
                                       bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.3', alpha=0.8))
        self.pitch_text = self.ax.text(0.16, 0.95, '', transform=self.ax.transAxes, fontsize=14, color='green', verticalalignment='top',
                                        bbox=dict(facecolor='white', edgecolor='green', boxstyle='round,pad=0.3', alpha=0.8))
        self.yaw_text = self.ax.text(0.30, 0.95, '', transform=self.ax.transAxes, fontsize=14, color='blue', verticalalignment='top',
                                      bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.3', alpha=0.8))

        self.setup_plot_labels()

        # Schedule plot updates
        Clock.schedule_interval(self.update_plot, 0.05)

    def setup_plot_labels(self):
        """Set up labels, titles, and legends for the plots."""
        self.ax.set_title('Roll, Elevation, and Azimuth over Time', fontsize=14)
        self.ax.set_xlabel('Time (Minutes)', fontsize=12)
        self.ax.set_ylabel('Degrees', fontsize=12)
        self.ax.legend(loc='upper right')
        self.ax.grid(True)
        self.ax.set_axisbelow(True)  # Ensure grid lines are behind the plot lines


        self.fig.tight_layout()

    def update_plot(self, dt):
        """Update the plot with the latest serial data."""
        try:
            if len(self.x_data) > 0:
                # Update Roll, Pitch, and Yaw vs Time plot
                self.line_roll.set_data(self.x_data, self.roll_data)
                self.line_pitch.set_data(self.x_data, self.pitch_data)
                self.line_yaw.set_data(self.x_data, self.yaw_data)
                self.ax.relim()
                self.ax.autoscale_view()

                # # Set x-axis limit to a maximum of 15 minutes
                # if len(self.x_data) > 0:
                #     self.ax.set_xlim(left=max(0, min(max(self.x_data) - 15, 0)), right=15)

                # Update the text annotations with the latest values
                self.roll_text.set_text(f'Roll: {self.roll_data[-1]:.2f}°')
                self.pitch_text.set_text(f'Pitch: {self.pitch_data[-1]:.2f}°')
                self.yaw_text.set_text(f'Yaw: {self.yaw_data[-1]:.2f}°')

                # Redraw the canvas
                self.canvas.draw_idle()
                
        except Exception as e:
            print(f"Error in updating the plot: {e}")  # Log the error


    def read_serial_data(self):
        """Continuously read serial data."""
        while self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    match = re.match(pattern, line)
                    if match:
                        timestamp, roll, pitch, yaw = match.groups()
                        time_value = float(timestamp) / 60  # Convert to minutes
                        self.x_data.append(time_value)
                        self.roll_data.append(float(roll))
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

    # def on_leave(self):
    #     if hasattr(self, 'ser') and self.ser is not None:
    #         if self.ser.is_open:
    #             self.ser.close()


# class InfoScreen(Screen):
#     def __init__(self, **kwargs):
#         super(InfoScreen, self).__init__(**kwargs)
#         self.add_widget(Label(text="Information Screen", font_size='24sp', color=(0, 0, 0, 1)))

class RoundedPopup(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (400, 300)
        self.auto_dismiss = True
        self.background_color = (0, 0, 0, 0)  # Make background transparent

        # Adding custom rounded background
        with self.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # White background color
            self.bg = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[20]  # Adjust radius to make corners more rounded
            )
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        """Update the size and position of the rounded background."""
        self.bg.size = self.size
        self.bg.pos = self.pos


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

    def start_animation(self):
        self.animation = Animation(dummy_angle=360, duration=2)
        self.animation += Animation(dummy_angle=0, duration=0)
        self.animation.repeat = True
        self.animation.start(self)

    def update_position(self, *args):
        self.image.center = self.center
        self.rotation.origin = self.center

    def on_dummy_angle(self, instance, angle):
        self.rotation.angle = angle

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

class MainApp(MDApp):
    def build(self):
        
        self.theme_cls.primary_palette = "BlueGray"
        # Create an instance of the ScreenManager
        sm = ScreenManager()
        
        # Add the various screens to the ScreenManager
        sm.add_widget(SplashScreen(name='splash_screen'))  # Welcome screen
        sm.add_widget(MainScreen(name='main_screen'))  # Main screen
        sm.add_widget(BluetoothScreen(name='bluetooth_screen'))  # Bluetooth screen
        sm.add_widget(GraphScreen(name='graph_screen'))  # Graph screen
        # sm.add_widget(InfoScreen(name='info_screen'))  # Info screen

        # Set the initial screen
        sm.current = 'splash_screen'  # Start with the welcome screen

        return sm  # Return the ScreenManager

    def scan_for_devices(self):
        """ Method to initiate scanning from the app level. """
        self.root.get_screen('bluetooth_screen').scan_for_devices()

    def show_info_popup(self):
        """ Show a popup with information about the app with rounded corners and wrapped text. """

        # Content layout
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Information label with text wrapping
        info_label = Label(
            text="App Version: 1.0.0\nThis application allows you to connect to Bluetooth devices and visualize data.",
            font_size='16sp',
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle",
            text_size=(300, None)  # Limiting width to wrap text within 300 pixels
        )
        content.add_widget(info_label)

        # Close button
        close_button = Button(text="Close", size_hint=(None, None), size=(100, 40))
        close_button.bind(on_release=lambda *args: popup.dismiss())
        content.add_widget(close_button)

        # Create the rounded popup
        popup = RoundedPopup()
        popup.add_widget(content)

        # Open the popup
        popup.open()


    def go_back(self):
        self.root.current = 'main_screen'   

if __name__ == '__main__':
    MainApp().run()
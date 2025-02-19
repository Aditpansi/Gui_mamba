from matplotlib import style
import pandas as pd
import asyncio
import threading
import asyncio
from datetime import datetime
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
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.properties import NumericProperty, ListProperty
from kivy.graphics import PushMatrix, PopMatrix, Rotate, Color, Rectangle
from kivy.lang import Builder
from kivymd.app import MDApp
from bleak import BleakScanner,BleakClient
from kivy.metrics import dp
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior

# KV layout string
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

        MDTopAppBar:
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
            id: devices_list_label
            text: "Available Devices:"
            size_hint_y: None
            height: 50
            font_size: '18sp'
            color: 1, 1, 1, 1
            bold: True

        RecycleView:
            id: devices_list
            size_hint_y: 1  # Expand to fill available space
            viewclass: 'DeviceItem'
            RecycleBoxLayout:
                default_size: None, dp(56)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'

<DeviceItem>:
    orientation: 'horizontal'
    canvas.before:
        Color:
            rgba: 0.2, 0.2, 0.2, 1  # Background color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10]
    Label:
        text: root.device_name
        size_hint_x: 0.7
        halign: 'left'
        valign: 'middle'
        text_size: self.size
    Button:
        text: "Connect"
        size_hint_x: 0.3
        on_release: root.connect_to_device()
'''

class DeviceItem(BoxLayout):
    device_name = StringProperty("Default Device")

    def connect_to_device(self):
        app = App.get_running_app()
        app.show_message(f"Connecting to {self.device_name}...")
        Clock.schedule_once(self.simulate_connection, 2)

    def simulate_connection(self, dt):
        import random
        success = random.choice([True, False])
        app = App.get_running_app()
        if success:
            app.show_message(f"Connected to {self.device_name} successfully!")
        else:
            app.show_message(f"Connection to {self.device_name} failed!")

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
        if devices:
            device_data = [{'device_name': f"{name} - {address}"} for name, address in devices]
            self.ids.devices_list.data = device_data
        else:
            self.ids.devices_list.data = [{'device_name': 'No devices found.'}]

    def show_error(self, message):
        """ Show error message in the devices_list label. """
        self.ids.devices_list.text = message

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

        # Set the initial screen
        sm.current = 'splash_screen'  # Start with the welcome screen

        return sm  # Return the ScreenManager

    def scan_for_devices(self):
        """ Method to initiate scanning from the app level. """
        self.root.get_screen('bluetooth_screen').scan_for_devices()
    
    def show_message(self, message):
        popup = Popup(title="Connection Status",
                      content=Label(text=message),
                      size_hint=(0.8, 0.4))
        popup.open()


    def show_info_popup(self):
        """ Show a popup with information about the app with rounded corners and wrapped text. """

        # Content layout
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Information label with text wrapping
        info_label = Label(
            text="App Version: 1.0.0\nThis application allows you to connect via a Serial USB or Serial Bluetooth devices and visualize data.",
            font_size='16sp',
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle",
            text_size=(300, None)  # Limiting width to wrap text within 300 pixels
        )
        content.add_widget(info_label)

        # Close button
        close_button = Button(text="Close", size_hint=(None, None), size=(100, 40), pos_hint={'center_x': 0.5})
        close_button.bind(on_release=lambda *args: popup.dismiss())
        content.add_widget(close_button)

        # Create the rounded popup
        popup = RoundedPopup()
        popup.add_widget(content)

        # Open the popup
        popup.open()


    def go_back(self):
        """Navigate to the previous screen."""
        if self.root.current != 'main_screen':
            self.root.current = 'main_screen' 

if __name__ == '__main__':
    MainApp().run()
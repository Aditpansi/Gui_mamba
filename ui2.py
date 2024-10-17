import asyncio
import threading
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import PushMatrix, PopMatrix, Rotate, Color, Rectangle
from kivy.properties import NumericProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout  
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.properties import ListProperty
from kivy.lang import Builder
from kivymd.app import MDApp
from bleak import BleakScanner
from threading import Thread
from kivy.clock import Clock



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
                    on_release: app.root.current = 'bluetooth_screen'  # Switch to Bluetooth screen

                DrawerClickableItem:
                    icon: "information-outline"
                    text: "Info" 

                DrawerClickableItem:
                    icon: "close"
                    text: "Close"
                    on_release: nav_drawer.set_state("close")  # Close the drawer when clicked
                    

########################################################################################
                                    #BluetoothScreen
########################################################################################

<BluetoothScreen>:
    name: 'bluetooth_screen'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1  # Black background
            Rectangle:
                pos: self.pos
                size: self.size

        CustomTopAppBar:
            title: "Bluetooth Device Connection"
            md_bg_color: "#fffff0"  # Background color of the AppBar
            specific_text_color: "#4a4939"  # Text color in the AppBar

            left_action_items: [["arrow-left", lambda x: app.go_back()]]  # Action to go back
            
            right_action_items: [["bluetooth", lambda x: app.scan_for_devices()]]  # Action to scan for devices

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
            color: 1, 1, 1, 1  # White text color

        Label:
            id: devices_list
            text: "No devices found."
            size_hint: (1, None)
            height: 50
            color: 1, 1, 1, 1  # White text color

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
        # Draw the 3D depth circle behind the Bluetooth icon
        Color:
            rgba: 0.2, 0.6, 0.8, 0.5  # Circle color with some transparency
        Ellipse:
            pos: self.x - dp(20), self.y + self.height/2 - dp(20)  # Positioning the circle
            size: dp(40), dp(40)  # Size of the circle (adjust as needed)


'''


class BluetoothScreen(Screen):
    # def __init__(self, **kwargs):
    #     super(BluetoothScreen, self).__init__(**kwargs)

    # async def async_scan_for_devices(self):
    #     """ Asynchronously scan for Bluetooth devices. """
    #     devices = await BleakScanner.discover()
    #     return [device.name for device in devices if device.name]

    # def scan_for_devices(self):
    #     """ Start the Bluetooth device scanning. """
    #     loop = asyncio.get_event_loop()
    #     try:
    #         devices = loop.run_until_complete(self.async_scan_for_devices())
            
    #         # Update the devices_list label with found devices
    #         devices_list_label = self.ids.devices_list
    #         if devices:
    #             devices_list_label.text = "\n".join(devices)
    #         else:
    #             devices_list_label.text = "No devices found."
    #     except Exception as e:
    #         devices_list_label.text = f"Error: {str(e)}"  # Display the error message

    def scan_for_devices(self):
        """ Start the Bluetooth device scanning in a separate thread. """
        self.ids.spinner.active = True  # Show the spinner
        threading.Thread(target=self.async_scan_for_devices).start()  # Start scanning in a new thread

    def async_scan_for_devices(self):
        """ Asynchronously scan for Bluetooth devices. """
        try:
            devices = asyncio.run(BleakScanner.discover())  # Run the scanner
            device_names = [device.name for device in devices if device.name]
            # Schedule an update to the UI thread
            Clock.schedule_once(lambda dt: self.update_device_list(device_names))
        except Exception as e:
            # Schedule an update for error message
            Clock.schedule_once(lambda dt: self.show_error(f"Error: {str(e)}"))
        finally:
            # Stop the spinner
            Clock.schedule_once(lambda dt: setattr(self.ids.spinner, 'active', False))

    def update_device_list(self, devices):
        """ Update the devices_list label with found devices. """
        devices_list_label = self.ids.devices_list
        if devices:
            devices_list_label.text = "\n".join(devices)
        else:
            devices_list_label.text = "No devices found."

    def show_error(self, message):
        """ Show error message in the devices_list label. """
        self.ids.devices_list.text = message

class AnimatedLogo(Widget):
    dummy_angle = NumericProperty(0)  # Create a property that can be animated

    def __init__(self, **kwargs):
        super(AnimatedLogo, self).__init__(**kwargs)
        with self.canvas:
            PushMatrix()
            self.rotation = Rotate(angle=0, origin=self.center)
            PopMatrix()

        self.image = Image(
            source='/Users/aditpansi/Desktop/Momentux/Momentux_Website/images/Momentux-removebg-preview.png',
            size_hint=(None, None), size=(200, 200)
        )
        self.add_widget(self.image)
        self.bind(pos=self.update_position, size=self.update_position)

    def update_position(self, *args):
        # Center the image within the widget
        self.image.center = self.center
        self.rotation.origin = self.center

    def on_dummy_angle(self, instance, value):
        self.rotation.angle = value  # Update the rotation angle whenever the dummy_angle changes


class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super(SplashScreen, self).__init__(**kwargs)
        with self.canvas:
            Color(0.2, 0.2, 0.2, 1)  # Set background color (dark gray)
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
        # Schedule a transition to the main screen
        Clock.schedule_once(self.switch_to_main_screen, 1)

    def switch_to_main_screen(self, dt):
        self.manager.current = 'main_screen'


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        with self.canvas:
            Color(0, 0, 0, 1)  # Set background color (light gray)
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
        sm.current = 'splash_screen'
        return sm

    def scan_for_devices(self):
        """ Method to initiate scanning from the app level. """
        self.root.get_screen('bluetooth_screen').scan_for_devices()
    
    def go_back(self):
        self.root.get_screen('main_screen').manager.current = 'main_screen'  # Example logic to go back


if __name__ == '__main__':
    MyApp().run()

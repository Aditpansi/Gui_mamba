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
import asyncio

class BluetoothScreen(Screen):
    def __init__(self, **kwargs):
        super(BluetoothScreen, self).__init__(**kwargs)

    async def async_scan_for_devices(self):
        devices = await BleakScanner.discover()
        return [device.name for device in devices if device.name]

    def scan_for_devices(self):
        loop = asyncio.get_event_loop()
        devices_list_label = self.ids.devices_list  # Ensure you have this label in your KV
        try:
            devices = loop.run_until_complete(self.async_scan_for_devices())
            devices_list_label.text = "\n".join(devices) if devices else "No devices found."
        except Exception as e:
            devices_list_label.text = f"Error: {str(e)}"

class AnimatedLogo(Widget):
    dummy_angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super(AnimatedLogo, self).__init__(**kwargs)
        with self.canvas:
            PushMatrix()
            self.rotation = Rotate(angle=0, origin=self.center)
            PopMatrix()

        self.image = Image(
            source='/Users/aditpansi/Desktop/Momentux/Momentux_Website/images/Momentux-removebg-preview.png',  # Update this path
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

        animation = Animation(dummy_angle=360, duration=0.8)
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

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MyApp(MDApp):
    def build(self):
        kv = Builder.load_file("/Users/aditpansi/Desktop/Momentux/Swash Plate/Gui/my.kv")
        return kv

    def scan_for_devices(self):
        self.root.get_screen('bluetooth_screen').scan_for_devices()

if __name__ == '__main__':
    MyApp().run()

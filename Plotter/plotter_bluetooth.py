import asyncio
import re
import pandas as pd
from bleak import BleakScanner, BleakClient
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
import time  # Import time module

class BluetoothPlotterApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.device_map = {}
        self.selected_device = None
        self.is_running = False

    async def find_esp32_bluetooth(self):
        print("Searching for Bluetooth devices...")
        devices = await BleakScanner.discover()
        self.device_map = {device.name: device.address for device in devices if device.name}
        
        if not self.device_map:
            print("No Bluetooth devices found.")
            return
        
        print("Devices found:")
        for name, address in self.device_map.items():
            print(f"Device: {name} ({address})")
        return self.device_map

    async def connect_and_receive_data(self):
        if self.selected_device is None:
            print("No device selected. Please select a device.")
            return

        characteristic_uuid = await self.get_device_services_and_characteristics(self.selected_device)

        async with BleakClient(self.selected_device) as client:
            print(f"Connected to ESP32 at {self.selected_device}")

            # Initialize plot
            style.use('fivethirtyeight')
            fig, ax = plt.subplots()
            x_data, azimuth_data, elevation_data = [], [], []
            df = pd.DataFrame()

            azimuth_line, = ax.plot([], [], label='Yaw (Azimuth)', color='r')
            elevation_line, = ax.plot([], [], label='Pitch (Elevation)', color='b')
            ax.legend(loc='upper right')

            start_time = time.time()  # Start time for plotting

            async def update_plot(i):
                nonlocal x_data, azimuth_data, elevation_data, df

                data = await client.read_gatt_char(characteristic_uuid)
                decoded_data = data.decode('utf-8').strip()
                print(f"Raw Data: {decoded_data}")

                match = re.match(r'([^,]+),([^,]+)', decoded_data)
                if match:
                    elevation = float(match.group(1))
                    azimuth = float(match.group(2))

                    x_data.append(time.time() - start_time)  # Time elapsed since start
                    azimuth_data.append(azimuth)
                    elevation_data.append(elevation)

                    ax.set_xlim(max(0, x_data[-1] - 10), x_data[-1])
                    azimuth_line.set_data(x_data, azimuth_data)
                    elevation_line.set_data(x_data, elevation_data)

                    df = pd.concat([df, pd.DataFrame({'time': [x_data[-1]],
                                                      'azimuth': [azimuth],
                                                      'elevation': [elevation]})], ignore_index=True)

                return azimuth_line, elevation_line

            ani = animation.FuncAnimation(fig, update_plot, blit=True, interval=5, cache_frame_data=False)
            plt.show()

    async def get_device_services_and_characteristics(self, device_address):
        async with BleakClient(device_address) as client:
            print(f"Connected to ESP32 at {device_address}")
            services = await client.get_services()
            characteristic_uuid = None

            for service in services:
                print(f"Service: {service.uuid}")
                for characteristic in service.characteristics:
                    print(f"  Characteristic: {characteristic.uuid} | Properties: {characteristic.properties}")
                    if 'notify' in characteristic.properties or 'read' in characteristic.properties:
                        characteristic_uuid = characteristic.uuid

            if characteristic_uuid is None:
                raise ValueError("No suitable characteristic found for data reception")

            return characteristic_uuid

    def connect_to_device(self, device_name):
        self.selected_device = self.device_map[device_name]
        print(f"Selected device: {self.selected_device}")

    def start_plotting(self):
        if self.selected_device:
            self.is_running = True
            asyncio.run(self.connect_and_receive_data())
        else:
            print("No device selected. Please select a device.")

    def stop_plotting(self):
        self.is_running = False
        print("Plotting stopped.")

    def build(self):
        layout = BoxLayout(orientation='vertical')

        # Dropdown for device selection
        self.device_spinner = Spinner(text='Select Bluetooth Device', values=list(self.device_map.keys()))
        self.device_spinner.bind(text=self.connect_to_device)
        layout.add_widget(self.device_spinner)

        # Start button
        start_button = Button(text='Start')
        start_button.bind(on_press=lambda x: self.start_plotting())
        layout.add_widget(start_button)

        # Stop button
        stop_button = Button(text='Stop')
        stop_button.bind(on_press=lambda x: self.stop_plotting())
        layout.add_widget(stop_button)

        # Label for status
        self.status_label = Label(text='Status: Waiting for action...')
        layout.add_widget(self.status_label)

        asyncio.run(self.find_esp32_bluetooth())

        return layout


if __name__ == '__main__':
    BluetoothPlotterApp().run()

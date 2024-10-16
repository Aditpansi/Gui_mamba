# from kivy.lang import Builder

# from kivymd.app import MDApp

# KV = '''
# MDBoxLayout:
#     orientation: "vertical"

#     MDTopAppBar:
#         title: "MDTopAppBar"

#     MDLabel:
#         text: "Content"
#         halign: "center"
# '''


# class Test(MDApp):
#     def build(self):
#         return Builder.load_string(KV)


# Test().run()

# class BluetoothScreen(Screen):
#     def scan_for_devices(self):
#         """ Start the Bluetooth device scanning in a separate thread. """
#         self.ids.spinner.active = True  # Show the spinner
#         threading.Thread(target=self.async_scan_for_devices).start()  # Start scanning in a new thread

#     def async_scan_for_devices(self):
#         """ Asynchronously scan for Bluetooth devices. """
#         try:
#             devices = asyncio.run(BleakScanner.discover())  # Run the scanner
#             device_names = [device.name if device.name else "Unnamed Device" for device in devices]
#             # Schedule an update to the UI thread
#             Clock.schedule_once(lambda dt: self.update_device_list(device_names))
#         except Exception as e:
#             # Schedule an update for error message
#             Clock.schedule_once(lambda dt: self.show_error(f"Error: {str(e)}"))
#         finally:
#             # Stop the spinner
#             Clock.schedule_once(lambda dt: setattr(self.ids.spinner, 'active', False))

#     def update_device_list(self, devices):
#         """ Update the devices_list with found devices. """
#         devices_list = self.ids.devices_list  # Access the MDList
#         devices_list.clear_widgets()  # Clear the previous list

#         # Access the "Scan for Devices" label
#         scan_label = self.ids.scan_label  # Ensure you give an ID to this label in your KV string

#         # Hide the label initially
#         scan_label.height = 0

#         if devices:
#             # Add each device as a label in the MDList
#             for device in devices:
#                 device_label = OneLineListItem(text=device, on_release=lambda x=device: self.connect_to_device(x))
#                 devices_list.add_widget(device_label)
#         else:
#             # Show a message if no devices are found
#             no_devices_label = self.ids.no_devices_label
#             no_devices_label.text = "No devices found."
#             no_devices_label.height = no_devices_label.texture_size[1] + dp(10)  # Show the label if no devices

#     def connect_to_device(self, device_name):
#         """ Connect to the selected Bluetooth device. """
#         # Implement your device connection logic here
#         print(f"Connecting to {device_name}...")  # Example action on device selection

import lightblue

def scan_for_devices():
    try:
        print("Scanning for devices...")
        devices = lightblue.finddevices()  # No duration parameter
        if devices:
            print("Found devices:")
            for addr, name in devices:
                print(f"Address: {addr}, Name: {name}")
        else:
            print("No devices found.")
    except Exception as e:
        print("Error during scanning:", e)

scan_for_devices()




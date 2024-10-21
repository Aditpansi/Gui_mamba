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

# import lightblue

# def scan_for_devices():
#     try:
#         print("Scanning for devices...")
#         devices = lightblue.finddevices()  # No duration parameter
#         if devices:
#             print("Found devices:")
#             for addr, name in devices:
#                 print(f"Address: {addr}, Name: {name}")
#         else:
#             print("No devices found.")
#     except Exception as e:
#         print("Error during scanning:", e)

# scan_for_devices()



# Copyright 2021-2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import asyncio
import sys
import os
import logging

from bumble.device import Device
from bumble.transport import open_transport_or_link
from bumble.sdp import (
    DataElement,
    ServiceAttribute,
    SDP_PUBLIC_BROWSE_ROOT,
    SDP_BROWSE_GROUP_LIST_ATTRIBUTE_ID,
    SDP_SERVICE_RECORD_HANDLE_ATTRIBUTE_ID,
    SDP_SERVICE_CLASS_ID_LIST_ATTRIBUTE_ID,
    SDP_PROTOCOL_DESCRIPTOR_LIST_ATTRIBUTE_ID,
    SDP_BLUETOOTH_PROFILE_DESCRIPTOR_LIST_ATTRIBUTE_ID,
)
from bumble.core import (
    BT_AUDIO_SINK_SERVICE,
    BT_L2CAP_PROTOCOL_ID,
    BT_AVDTP_PROTOCOL_ID,
    BT_ADVANCED_AUDIO_DISTRIBUTION_SERVICE,
)

# -----------------------------------------------------------------------------
SDP_SERVICE_RECORDS = {
    0x00010001: [
        ServiceAttribute(
            SDP_SERVICE_RECORD_HANDLE_ATTRIBUTE_ID,
            DataElement.unsigned_integer_32(0x00010001),
        ),
        ServiceAttribute(
            SDP_BROWSE_GROUP_LIST_ATTRIBUTE_ID,
            DataElement.sequence([DataElement.uuid(SDP_PUBLIC_BROWSE_ROOT)]),
        ),
        ServiceAttribute(
            SDP_SERVICE_CLASS_ID_LIST_ATTRIBUTE_ID,
            DataElement.sequence([DataElement.uuid(BT_AUDIO_SINK_SERVICE)]),
        ),
        ServiceAttribute(
            SDP_PROTOCOL_DESCRIPTOR_LIST_ATTRIBUTE_ID,
            DataElement.sequence(
                [
                    DataElement.sequence(
                        [
                            DataElement.uuid(BT_L2CAP_PROTOCOL_ID),
                            DataElement.unsigned_integer_16(25),
                        ]
                    ),
                    DataElement.sequence(
                        [
                            DataElement.uuid(BT_AVDTP_PROTOCOL_ID),
                            DataElement.unsigned_integer_16(256),
                        ]
                    ),
                ]
            ),
        ),
        ServiceAttribute(
            SDP_BLUETOOTH_PROFILE_DESCRIPTOR_LIST_ATTRIBUTE_ID,
            DataElement.sequence(
                [
                    DataElement.sequence(
                        [
                            DataElement.uuid(BT_ADVANCED_AUDIO_DISTRIBUTION_SERVICE),
                            DataElement.unsigned_integer_16(256),
                        ]
                    )
                ]
            ),
        ),
    ]
}


# -----------------------------------------------------------------------------
async def main() -> None:
    if len(sys.argv) < 3:
        print('Usage: run_classic_discoverable.py <device-config> <transport-spec>')
        print('example: run_classic_discoverable.py classic1.json usb:04b4:f901')
        return

    print('<<< connecting to HCI...')
    async with await open_transport_or_link(sys.argv[2]) as hci_transport:
        print('<<< connected')

        # Create a device
        device = Device.from_config_file_with_hci(
            sys.argv[1], hci_transport.source, hci_transport.sink
        )
        device.classic_enabled = True
        device.sdp_service_records = SDP_SERVICE_RECORDS
        await device.power_on()

        # Start being discoverable and connectable
        await device.set_discoverable(True)
        await device.set_connectable(True)

        await hci_transport.source.wait_for_termination()


# -----------------------------------------------------------------------------
logging.basicConfig(level=os.environ.get('BUMBLE_LOGLEVEL', 'DEBUG').upper())
asyncio.run(main())



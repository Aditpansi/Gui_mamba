# import serial
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from matplotlib import style
# import serial.tools.list_ports
# import time
# import re
# import pandas as pd

# # Set up the serial port (modify with your port and baud rate) 
# def detect_device():
#     device_ports = [
#         p.device
#         for p in serial.tools.list_ports.comports()
#         if 'VID:PID' in p.hwid  # Modify if your device uses a different identifier
#     ]
#     if not device_ports:
#         raise IOError("No device found")
#     return device_ports[0]

# port = detect_device()
# ser = serial.Serial(port, 115200)  # Adjust baud rate if needed

# # Regular expression for matching two comma-separated values
# pattern = r'([^,]+),([^,]+)'  # Assuming the data is Azimuth,Elevation

# # Initialize plot
# style.use('fivethirtyeight')
# fig, ax = plt.subplots()

# # Store the plot lines and data
# x_data, azimuth_data, elevation_data = [], [], []
# df = pd.DataFrame()

# # Initialize the plot lines (for blitting)
# azimuth_line, = ax.plot([], [], label='Yaw (Azimuth)', color='r')
# elevation_line, = ax.plot([], [], label='Pitch (Elevation)', color='b')
# ax.legend(loc='upper right')

# # Start time for real-time plotting
# start_time = time.time()

# # Function to read and process data from the serial port
# def read_serial_data():
#     try:
#         line = ser.readline().decode('utf-8', errors='ignore').strip()
#         print(f"Raw Data: {line}")

#         # Match the line with the regex for two comma-separated values
#         match = re.match(pattern, line)
#         if match:
#             elevation = float(match.group(1))  # Now representing Pitch (Elevation)
#             azimuth = float(match.group(3))  # Now representing Yaw (Azimuth)
#             return azimuth, elevation
#         else:
#             return None, None  # Data format mismatch
#     except (ValueError, IndexError) as e:
#         return None, None  # Error handling for conversion issues

# # Function to initialize the plot (blitting setup)
# def init():
#     ax.set_xlim(0, 10)
#     ax.set_ylim(-180, 180)
#     azimuth_line.set_data([], [])
#     elevation_line.set_data([], [])
#     return azimuth_line, elevation_line

# # Function to update the plot
# def update_plot(i):
#     global ax , df 

#     azimuth, elevation = read_serial_data()

#     if azimuth is not None and elevation is not None:
#         # Append data
#         x_data.append(time.time() - start_time)  # Time since start
#         azimuth_data.append(azimuth)
#         elevation_data.append(elevation)

#         # Update plot limits dynamically
#         ax.set_xlim(max(0, x_data[-1] - 10), x_data[-1])

#         # Update data in the plot lines
#         azimuth_line.set_data(x_data, azimuth_data)
#         elevation_line.set_data(x_data, elevation_data)

#         # Update DataFrame with new values
#         df = pd.concat([df, pd.DataFrame({'time': [x_data[-1]], 
#                                           'azimuth': [azimuth], 
#                                           'elevation': [elevation]})], ignore_index=True)

#     return azimuth_line, elevation_line

# # Animation function with blitting
# ani = animation.FuncAnimation(fig, update_plot, init_func=init, blit=True, interval=5, cache_frame_data=False)  # 5ms interval

# plt.show()


import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import serial.tools.list_ports
import time
import re
import pandas as pd

# Set up the serial port (modify with your port and baud rate)
def detect_device():
    device_ports = [
        p.device
        for p in serial.tools.list_ports.comports()
        if 'VID:PID' in p.hwid  # Modify if your device uses a different identifier
    ]
    if not device_ports:
        raise IOError("No device found")
    return device_ports[0]

port = detect_device()
ser = serial.Serial(port, 115200)  # Adjust baud rate if needed

# Regular expression for matching four comma-separated values (Timestamp, Roll, Pitch, Yaw)
pattern = r'([^,]+),([^,]+),([^,]+),([^,]+)'  # Adjusted to capture Timestamp, Roll, Pitch, and Yaw

# Initialize plot
style.use('fivethirtyeight')
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))

# Store the plot lines and data
x_data, roll_data, pitch_data, yaw_data = [], [], [], []
df = pd.DataFrame()

# Initialize the plot lines
roll_line, = ax1.plot([], [], label='Roll', color='r')
pitch_line, = ax2.plot([], [], label='Pitch', color='g')
yaw_line, = ax3.plot([], [], label='Yaw', color='b')

# Set titles and labels for each subplot
ax1.set_title('Roll (Degrees)')
ax1.set_ylabel('Roll')
ax1.set_xlim(0, 10)
ax1.set_ylim(-280, 280)
ax1.legend(loc='upper right')

ax2.set_title('Pitch (Degrees)')
ax2.set_ylabel('Pitch')
ax2.set_xlim(0, 10)
ax2.set_ylim(-180, 180)
ax2.legend(loc='upper right')

ax3.set_title('Yaw (Degrees)')
ax3.set_ylabel('Yaw')
ax3.set_xlim(0, 10)
ax3.set_ylim(-280, 280)
ax3.legend(loc='upper right')

ax3.set_xlabel('Time (s)')  # X-axis label for the last subplot

# Start time for real-time plotting
start_time = time.time()

# Function to read and process data from the serial port
def read_serial_data():
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        print(f"Raw Data: {line}")

        # Match the line with the regex for four comma-separated values
        match = re.match(pattern, line)
        if match:
            timestamp = float(match.group(1)) / 1000.0  # Convert milliseconds to seconds
            roll = float(match.group(2))    # Roll value
            pitch = float(match.group(3))   # Pitch value
            yaw = float(match.group(4))     # Yaw value
            return timestamp, roll, pitch, yaw
        else:
            return None, None, None, None  # Data format mismatch
    except (ValueError, IndexError) as e:
        return None, None, None, None  # Error handling for conversion issues


# Function to initialize the plot (blitting setup)
def init():
    roll_line.set_data([], [])
    pitch_line.set_data([], [])
    yaw_line.set_data([], [])
    return roll_line, pitch_line, yaw_line

# Function to update the plot
def update_plot(i):
    global ax1, ax2, ax3, df 

    timestamp, roll, pitch, yaw = read_serial_data()

    if timestamp is not None and roll is not None and pitch is not None and yaw is not None:
        # Append data
        x_data.append(timestamp)  # Append the timestamp
        roll_data.append(roll)
        pitch_data.append(pitch)
        yaw_data.append(yaw)

        # Update plot limits dynamically
        ax1.set_xlim(max(0, x_data[-1] - 10), x_data[-1])
        ax2.set_xlim(max(0, x_data[-1] - 10), x_data[-1])
        ax3.set_xlim(max(0, x_data[-1] - 10), x_data[-1])

        # Update data in the plot lines
        roll_line.set_data(x_data, roll_data)
        pitch_line.set_data(x_data, pitch_data)
        yaw_line.set_data(x_data, yaw_data)

        # Update DataFrame with new values
        df = pd.concat([df, pd.DataFrame({'time': [x_data[-1]], 
                                          'roll': [roll], 
                                          'pitch': [pitch],
                                          'yaw': [yaw]})], ignore_index=True)

    return roll_line, pitch_line, yaw_line

# Animation function with blitting
ani = animation.FuncAnimation(fig, update_plot, init_func=init, blit=True, interval=5, cache_frame_data=False)  # 5ms interval

plt.tight_layout()  # Adjust layout for better spacing
plt.show()

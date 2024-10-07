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

# Regular expression for matching two comma-separated values
pattern = r'([^,]+),([^,]+)'  # Assuming the data is Azimuth,Elevation

# Initialize plot
style.use('fivethirtyeight')
fig, ax = plt.subplots()

# Store the plot lines and data
x_data, azimuth_data, elevation_data = [], [], []
df = pd.DataFrame()

# Initialize the plot lines (for blitting)
azimuth_line, = ax.plot([], [], label='Yaw (Azimuth)', color='r')
elevation_line, = ax.plot([], [], label='Pitch (Elevation)', color='b')
ax.legend(loc='upper right')

# Start time for real-time plotting
start_time = time.time()

# Function to read and process data from the serial port
def read_serial_data():
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        print(f"Raw Data: {line}")

        # Match the line with the regex for two comma-separated values
        match = re.match(pattern, line)
        if match:
            elevation = float(match.group(1))  # Now representing Pitch (Elevation)
            azimuth = float(match.group(2))  # Now representing Yaw (Azimuth)
            return azimuth, elevation
        else:
            return None, None  # Data format mismatch
    except (ValueError, IndexError) as e:
        return None, None  # Error handling for conversion issues

# Function to initialize the plot (blitting setup)
def init():
    ax.set_xlim(0, 10)
    ax.set_ylim(-180, 180)
    azimuth_line.set_data([], [])
    elevation_line.set_data([], [])
    return azimuth_line, elevation_line

# Function to update the plot
def update_plot(i):
    global ax , df 

    azimuth, elevation = read_serial_data()

    if azimuth is not None and elevation is not None:
        # Append data
        x_data.append(time.time() - start_time)  # Time since start
        azimuth_data.append(azimuth)
        elevation_data.append(elevation)

        # Update plot limits dynamically
        ax.set_xlim(max(0, x_data[-1] - 10), x_data[-1])

        # Update data in the plot lines
        azimuth_line.set_data(x_data, azimuth_data)
        elevation_line.set_data(x_data, elevation_data)

        # Update DataFrame with new values
        df = pd.concat([df, pd.DataFrame({'time': [x_data[-1]], 
                                          'azimuth': [azimuth], 
                                          'elevation': [elevation]})], ignore_index=True)

    return azimuth_line, elevation_line

# Animation function with blitting
ani = animation.FuncAnimation(fig, update_plot, init_func=init, blit=True, interval=5, cache_frame_data=False)  # 5ms interval

plt.show()

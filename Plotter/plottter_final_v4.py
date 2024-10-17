######################################################################################
                            #Two Graph(Pitch and Yaw)
######################################################################################
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

# Regular expression for matching the values (Timestamp, Roll, Pitch, Yaw)
pattern = r'([^,]+),[^,]+,([^,]+),([^,]+)'  # Modified to ignore the roll value

# Initialize plot
style.use('fivethirtyeight')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))

# Set the window title
fig.canvas.manager.set_window_title('MAMBA')

# Store the plot lines and data
x_data, pitch_data, yaw_data = [], [], []
df = pd.DataFrame()

# Initialize the plot lines
pitch_line, = ax1.plot([], [], label='Pitch', color='g')
yaw_line, = ax2.plot([], [], label='Yaw', color='b')

# Set titles and labels for each subplot
ax1.set_title('Pitch (Degrees)')
ax1.set_ylabel('Pitch')
ax1.set_xlim(0, 10)
ax1.set_ylim(-180, 180)
ax1.legend(loc='upper right')

ax2.set_title('Yaw (Degrees)')
ax2.set_ylabel('Yaw')
ax2.set_xlim(0, 10)
ax2.set_ylim(-410, 410)
ax2.legend(loc='upper right')

ax2.set_xlabel('Time (s)')  # X-axis label for the last subplot

# Start time for real-time plotting
start_time = time.time()

# Function to read and process data from the serial port
def read_serial_data():
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        print(f"Raw Data: {line}")

        # Match the line with the regex for timestamp, pitch, and yaw (ignoring roll)
        match = re.match(pattern, line)
        if match:
            timestamp = float(match.group(1)) / 1000.0  # Convert milliseconds to seconds
            pitch = float(match.group(2))   # Pitch value
            yaw = float(match.group(3))     # Yaw value
            return timestamp, pitch, yaw
        else:
            return None, None, None  # Data format mismatch
    except (ValueError, IndexError) as e:
        return None, None, None  # Error handling for conversion issues

# Create text annotations for displaying real-time values outside the functions with a background box
pitch_text = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, fontsize=14, color='green', verticalalignment='top',
                      bbox=dict(facecolor='white', edgecolor='green', boxstyle='round,pad=0.3', alpha=0.8))
yaw_text = ax2.text(0.02, 0.95, '', transform=ax2.transAxes, fontsize=14, color='blue', verticalalignment='top',
                    bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.3', alpha=0.8))

# Function to initialize the plot (blitting setup)
def init():
    pitch_line.set_data([], [])
    yaw_line.set_data([], [])

    # Initialize text annotations
    pitch_text.set_text('')
    yaw_text.set_text('')

    return pitch_line, yaw_line, pitch_text, yaw_text

# Function to update the plot
def update_plot(i):
    global ax1, ax2, df 

    timestamp, pitch, yaw = read_serial_data()

    if timestamp is not None and pitch is not None and yaw is not None:
        # Append data
        x_data.append(timestamp)  # Append the timestamp
        pitch_data.append(pitch)
        yaw_data.append(yaw)

        # Update plot limits dynamically
        ax1.set_xlim(max(0, x_data[-1] - 10), x_data[-1])
        ax2.set_xlim(max(0, x_data[-1] - 10), x_data[-1])

        # Update data in the plot lines
        pitch_line.set_data(x_data, pitch_data)
        yaw_line.set_data(x_data, yaw_data)

        # Update text annotations with the latest values
        pitch_text.set_text(f'Pitch: {pitch:.2f}')
        yaw_text.set_text(f'Yaw: {yaw:.2f}')

        # Update DataFrame with new values
        df = pd.concat([df, pd.DataFrame({'time': [x_data[-1]], 
                                          'pitch': [pitch],
                                          'yaw': [yaw]})], ignore_index=True)

    return pitch_line, yaw_line, pitch_text, yaw_text

# Animation function with blitting
ani = animation.FuncAnimation(fig, update_plot, init_func=init, blit=True, interval=5, cache_frame_data=False)  # 5ms interval

plt.tight_layout()  # Adjust layout for better spacing
plt.show()

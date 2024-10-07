import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import serial.tools.list_ports
import re
import time
import pandas as pd
from datetime import datetime
import os

# Set up the serial port (modify with your port and baud rate)
def detect_arduino():
    arduino_ports = [
        p.device
        for p in serial.tools.list_ports.comports()
        if 'Arduino' in p.description
        or 'VID:PID' in p.hwid  # for Linux and macOS
    ]
    if not arduino_ports:
        raise IOError("No Arduino found")
    return arduino_ports[0]

port = detect_arduino()
ser = serial.Serial(port, 9600)  # Change this to your serial port

# Initialize plot
style.use('fivethirtyeight')
fig, axs = plt.subplots()

# This will store the plot lines and data
plots = {}
data = {}
df = pd.DataFrame()
max_points = {}
max_markers = {}  # Store the max point markers and text annotations

def update_plot(i):
    global axs, df, max_points, max_markers
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        print(line)
        matches = re.findall(r'([^,]+):([^,]+)', line)
        
        if matches:
            new_data = {}
            for match in matches:
                label, value, unit = match
                value = float(value)
                
                if label not in data:
                    data[label] = {'x': [], 'y': [], 'unit': unit}
                    max_points[label] = (-float('inf'), None)  # Initialize max value and point
                    max_markers[label] = (None, None)  # Initialize max marker and text annotation
                    # Create a new subplot for the new label
                    num_plots = len(data)
                    fig.clear()
                    axs = [fig.add_subplot(num_plots, 1, i + 1) for i in range(num_plots)]
                    plots.clear()
                    for j, key in enumerate(data):
                        plots[key] = axs[j].plot([], [], label=f'{key} ({data[key]["unit"]})' if data[key]["unit"] else key)[0]
                        axs[j].set_ylabel(key)
                        if j == num_plots - 1:
                            axs[j].set_xlabel('Time (s)')
                
                # Update data
                data[label]['x'].append(time.time() - start_time)
                data[label]['y'].append(value)
                
                # Collect new data
                new_data[label] = value
                
                # Update plot
                plots[label].set_data(data[label]['x'], data[label]['y'])

                # Update max point if current value is higher
                if value > max_points[label][0]:
                    max_points[label] = (value, (data[label]['x'][-1], value))
                    # Clear previous max marker and text
                    if max_markers[label][0] is not None:
                        max_markers[label][0].remove()
                        max_markers[label][1].remove()
                    # Plot new max point marker
                    ax = plots[label].axes
                    max_x, max_y = max_points[label][1]
                    max_marker, = ax.plot(max_x, max_y, 'ro')  # Marker for max value
                    max_text = ax.text(max_x, max_y, f'{max_y:.2f}', color='red', fontsize=8)
                    max_markers[label] = (max_marker, max_text)

            # Update DataFrame
            new_data['time'] = time.time() - start_time
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                
            # Update the axis limits for all plots
            for key in data:
                ax = plots[key].axes
                ax.relim()
                ax.autoscale_view()
                ax.legend(loc='upper left')

        fig.tight_layout()
    
    except Exception as e:
        print(f"Error: {e}")

# def save_to_excel(df, folder_path="C:\\Users\\Momentux\\Desktop\\LCS\\Sensor_data"):
#     if not os.path.exists(folder_path):
#         os.makedirs(folder_path)
#     filename = os.path.join(folder_path, f'DATA_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
#     df.to_excel(filename, index=False)

# Set the start time
start_time = time.time()

# Animation function
ani = animation.FuncAnimation(fig, update_plot, interval=100)  # Reduced interval to 100ms

plt.show()

# Save data to Excel when the program ends
# save_to_excel(df)

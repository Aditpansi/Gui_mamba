# import serial
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from matplotlib import style
# import serial.tools.list_ports
# import re
# import time

# # Set up the serial port (modify with your port and baud rate)


# def detect_arduino():
#     arduino_ports = [
#         p.device
#         for p in serial.tools.list_ports.comports()
#         if 'Arduino' in p.description
#         or 'VID:PID' in p.hwid  # for Linux
#         or 'USB VID:PID' in p.hwid  # for macOS
#     ]
#     return arduino_ports[0]

# port = detect_arduino()
# ser = serial.Serial(port, 9600)  # Change this to your serial port

# # Initialize plot
# style.use('fivethirtyeight')
# fig, axs = plt.subplots()

# # This will store the plot lines and data
# plots = {}
# data = {}

# def update_plot(i):
#     global axs
#     try:
#         line = ser.readline().decode('utf-8', errors='ignore').strip()
#         print(line)
#         matches = re.findall(r'(\w+):(-?[\d\.]+)\s*([\w%]*)', line)
        
#         if matches:
#             for match in matches:
#                 label, value, unit = match
#                 value = float(value)
                
#                 if label not in data:
#                     data[label] = {
#                         'x': [],
#                         'y': [],
#                         'unit': unit
#                     }
#                     # Create a new subplot for the new label
#                     num_plots = len(data)
#                     fig.clear()
#                     axs = [fig.add_subplot(num_plots, 1, i+1) for i in range(num_plots)]
#                     plots.clear()
#                     for j, key in enumerate(data):
#                         plots[key] = axs[j].plot([], [], label=f'{key} ({data[key]["unit"]})' if data[key]["unit"] else key)[0]
#                         axs[j].set_ylabel(key)
#                         if j == num_plots - 1:
#                             axs[j].set_xlabel('Time (s)')
                
#                 # Update data
#                 data[label]['x'].append(time.time() - start_time)
#                 data[label]['y'].append(value)
                
#                 # Update plot
#                 plots[label].set_data(data[label]['x'], data[label]['y'])
                
#             # Update the axis limits for all plots
#             for key in data:
#                 ax = plots[key].axes
#                 ax.relim()
#                 ax.autoscale_view()
#                 ax.legend(loc='upper left')

#         fig.tight_layout()
    
#     except Exception as e:
#         print(f"Error: {e}")

# # Set the start time
# start_time = time.time()

# # Animation function
# ani = animation.FuncAnimation(fig, update_plot, interval=1000)

# plt.show()

######################################################### code 2: works well.######################################################################

# import serial
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from matplotlib import style
# import serial.tools.list_ports
# import re
# import time
# import pandas as pd

# # Set up the serial port (modify with your port and baud rate)

# def detect_arduino():
#     arduino_ports = [
#         p.device
#         for p in serial.tools.list_ports.comports()
#         if 'Arduino' in p.description
#         or 'VID:PID' in p.hwid  # for Linux
#         or 'USB VID:PID' in p.hwid  # for macOS
#     ]
#     return arduino_ports[0]

# port = detect_arduino()
# ser = serial.Serial(port, 9600)  # Change this to your serial port

# # Initialize plot
# style.use('fivethirtyeight')
# fig, axs = plt.subplots()

# # This will store the plot lines and data
# plots = {}
# data = {}
# df = pd.DataFrame()

# def update_plot(i):
#     global axs, df
#     try:
#         line = ser.readline().decode('utf-8', errors='ignore').strip()
#         print(line)
#         matches = re.findall(r'(\w+):(-?[\d\.]+)\s*([\w%]*)', line)
        
#         if matches:
#             new_data = {}
#             for match in matches:
#                 label, value, unit = match
#                 value = float(value)
                
#                 if label not in data:
#                     data[label] = {
#                         'x': [],
#                         'y': [],
#                         'unit': unit
#                     }
#                     # Create a new subplot for the new label
#                     num_plots = len(data)
#                     fig.clear()
#                     axs = [fig.add_subplot(num_plots, 1, i+1) for i in range(num_plots)]
#                     plots.clear()
#                     for j, key in enumerate(data):
#                         plots[key] = axs[j].plot([], [], label=f'{key} ({data[key]["unit"]})' if data[key]["unit"] else key)[0]
#                         axs[j].set_ylabel(key)
#                         if j == num_plots - 1:
#                             axs[j].set_xlabel('Time (s)')
                
#                 # Update data
#                 data[label]['x'].append(time.time() - start_time)
#                 data[label]['y'].append(value)
                
#                 # Collect new data
#                 new_data[label] = value
                
#                 # Update plot
#                 plots[label].set_data(data[label]['x'], data[label]['y'])
                
#             # Update DataFrame
#             new_data['time'] = time.time() - start_time
#             df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                
#             # Update the axis limits for all plots
#             for key in data:
#                 ax = plots[key].axes
#                 ax.relim()
#                 ax.autoscale_view()
#                 ax.legend(loc='upper left')

#         fig.tight_layout()
    
#     except Exception as e:
#         print(f"Error: {e}")

# def save_to_excel(df, filename='D:\Momentux\LCS\DATA\data.xlsx'):
#     df.to_excel(filename, index=False)

# # Set the start time
# start_time = time.time()

# # Animation function
# ani = animation.FuncAnimation(fig, update_plot, interval=1000)

# plt.show()

# # Save data to Excel when the program ends
# save_to_excel(df)

######################################################### code 3: .######################################################################

# import serial
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from matplotlib import style
# import serial.tools.list_ports
# import re
# import time
# import pandas as pd
# from datetime import datetime
# import os

# # Set up the serial port (modify with your port and baud rate)

# def detect_arduino():
#     arduino_ports = [
#         p.device
#         for p in serial.tools.list_ports.comports()
#         if 'Arduino' in p.description
#         or 'VID:PID' in p.hwid  # for Linux
#         or 'USB VID:PID' in p.hwid  # for macOS
#     ]
#     return arduino_ports[0]

# port = detect_arduino()
# ser = serial.Serial(port, 9600)  # Change this to your serial port

# # Initialize plot
# style.use('fivethirtyeight')
# fig, axs = plt.subplots()

# # This will store the plot lines and data
# plots = {}
# data = {}
# df = pd.DataFrame()
# max_points = {}

# def update_plot(i):
#     global axs, df, max_points
#     try:
#         line = ser.readline().decode('utf-8', errors='ignore').strip()
#         print(line)
#         matches = re.findall(r'(\w+):(-?[\d\.]+)\s*([\w%]*)', line)
        
#         if matches:
#             new_data = {}
#             for match in matches:
#                 label, value, unit = match
#                 value = float(value)
                
#                 if label not in data:
#                     data[label] = {
#                         'x': [],
#                         'y': [],
#                         'unit': unit
#                     }
#                     max_points[label] = (-float('inf'), None)  # Initialize max value and point
#                     # Create a new subplot for the new label
#                     num_plots = len(data)
#                     fig.clear()
#                     axs = [fig.add_subplot(num_plots, 1, i+1) for i in range(num_plots)]
#                     plots.clear()
#                     for j, key in enumerate(data):
#                         plots[key] = axs[j].plot([], [], label=f'{key} ({data[key]["unit"]})' if data[key]["unit"] else key)[0]
#                         axs[j].set_ylabel(key)
#                         if j == num_plots - 1:
#                             axs[j].set_xlabel('Time (s)')
                
#                 # Update data
#                 data[label]['x'].append(time.time() - start_time)
#                 data[label]['y'].append(value)
                
#                 # Collect new data
#                 new_data[label] = value
                
#                 # Update max point if current value is higher
#                 if value > max_points[label][0]:
#                     max_points[label] = (value, (data[label]['x'][-1], value))
                
#                 # Update plot
#                 plots[label].set_data(data[label]['x'], data[label]['y'])
                
#             # Update DataFrame
#             new_data['time'] = time.time() - start_time
#             df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                
#             # Update the axis limits for all plots
#             for key in data:
#                 ax = plots[key].axes
#                 ax.relim()
#                 ax.autoscale_view()
#                 ax.legend(loc='upper left')
#                 # Plot max point marker
#                 max_x, max_y = max_points[key][1]
#                 ax.plot(max_x, max_y, 'ro')  # Marker for max value
#                 ax.text(max_x, max_y, f'{max_y:.2f}', color='red', fontsize=8)

#         fig.tight_layout()
    
#     except Exception as e:
#         print(f"Error: {e}")

# def save_to_excel(df, folder_path='D:\\Momentux\\LCS\\DATA'):
#     if not os.path.exists(folder_path):
#         os.makedirs(folder_path)
#     filename = os.path.join(folder_path, f'DATA_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
#     df.to_excel(filename, index=False)

# # Set the start time
# start_time = time.time()

# # Animation function
# ani = animation.FuncAnimation(fig, update_plot, interval=1000)

# plt.show()

# # Save data to Excel when the program ends
# save_to_excel(df)

######################################################### code 3: .######################################################################

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
        or 'VID:PID' in p.hwid  # for Linux
        or 'USB VID:PID' in p.hwid  # for macOS
    ]
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
        matches = re.findall(r'(\w+):(-?[\d\.]+)\s*([\w%]*)', line)
        
        if matches:
            new_data = {}
            for match in matches:
                label, value, unit = match
                value = float(value)
                
                if label not in data:
                    data[label] = {
                        'x': [],
                        'y': [],
                        'unit': unit
                    }
                    max_points[label] = (-float('inf'), None)  # Initialize max value and point
                    max_markers[label] = (None, None)  # Initialize max marker and text annotation
                    # Create a new subplot for the new label
                    num_plots = len(data)
                    fig.clear()
                    axs = [fig.add_subplot(num_plots, 1, i+1) for i in range(num_plots)]
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

def save_to_excel(df, folder_path='D:\\Momentux\\LCS\\DATA'):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = os.path.join(folder_path, f'DATA_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
    df.to_excel(filename, index=False)

# Set the start time
start_time = time.time()

# Animation function
ani = animation.FuncAnimation(fig, update_plot, interval=1000)

plt.show()

# Save data to Excel when the program ends
save_to_excel(df)

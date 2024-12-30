import tkinter as tk
from tkinter import ttk
import threading
import math
import serial
import serial.tools.list_ports
 
 
def get_com_port():
    """Prompt the user to enter a valid COM port."""
    return "COM6"
 
def initialize_serial_port(port):
    """Initialize and return the serial port."""
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        if ser.is_open:
            print(f"Serial port {port} is open for reading.")
            return ser
    except serial.SerialException as e:
        print(f"Error: Unable to open serial port {port}. Details: {e}")
    return None
 
 
def usb_data(ser):
    """Generator to read and parse USB data."""
    while True:
        try:
            # Read a line of data from the serial port
            data_line = ser.readline().decode("utf-8").strip()
 
            # Check if data is in the expected format
            if data_line.startswith("Throttle:") and "RPM:" in data_line:
                parts = data_line.split(",")
                throttle = int(parts[0].split(":")[1].strip())
                motor_speed = int(parts[1].split(":")[1].strip())
                yield throttle, motor_speed
            else:
                print("Invalid data format:", data_line)
 
        except ValueError as e:
            print(f"Data parsing error: {e}")
 
 
class DashboardGUI:

    def draw_dial(self):
        # Draw a circular dial
        print()
 
    def update_needle(self, speed):
        # Calculate needle angle based on speed (assuming 0 to 6000 scale)
        angle = 180 - (speed / 6000) * 180
        radians = math.radians(angle)
        needle_length = 70
        x_end = 125 + needle_length * math.cos(radians)
        y_end = 125 - needle_length * math.sin(radians)
        # Update needle position
        self.dial_canvas.coords(self.needle, 125, 125, x_end, y_end)
 
    def update_values(self):
        try:
            for throttle, motor_speed in usb_data(ser):
                # Update the throttle progress bar
                self.throttle_value.set(throttle)
                # Update the throttle label dynamically
                self.throttle_label.config(text=f"Throttle: {throttle}%")
                # Update the needle based on motor speed
                self.update_needle(motor_speed)
        except Exception as e:
            print(f"Error in update thread: {e}")
 

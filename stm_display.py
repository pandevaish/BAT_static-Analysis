import tkinter as tk
from tkinter import ttk
import threading
import math
import serial
import serial.tools.list_ports


def get_com_port():
    """Prompt the user to enter a valid COM port."""
    available_ports = [port.device for port in serial.tools.list_ports.comports()]
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
                yield "Invalid data format"

        except ValueError as e:
            print(f"Data parsing error: {e}")

class DashboardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Payload Parser GUI")
        self.root.geometry("400x400")  # Set a specific size (width x height)

        # Frame for Throttle View
        self.throttle_frame = ttk.LabelFrame(root, text="Throttle View", padding=(20, 20))
        self.throttle_frame.grid(row=0, column=0, padx=20, pady=20)

        # Label for "Min"
        self.throttle_min_label = tk.Label(
            self.throttle_frame, text="Min", font=("Arial", 10), anchor="e"
        )
        self.throttle_min_label.pack(side="left", padx=(5, 0))

        self.throttle_value = tk.IntVar()
        self.throttle_bar = ttk.Progressbar(
            self.throttle_frame, orient="horizontal",
            mode="determinate", variable=self.throttle_value,
            length=300, maximum=100
        )
        self.throttle_bar.pack(padx=20, pady=10)

        self.throttle_bar.pack(side="left", padx=10, pady=10)

        # Label for "Max"
        self.throttle_max_label = tk.Label(
            self.throttle_frame, text="Max", font=("Arial", 10), anchor="w"
        )
        self.throttle_max_label.pack(side="left", padx=(0, 5))

        self.throttle_label = tk.Label(
            self.throttle_frame, text="Throttle: 0%", font=("Arial", 12)
        )
        self.throttle_label.pack(pady=10)

        # Frame for Motor View
        self.motor_frame = ttk.LabelFrame(root, text="Motor View", padding=(20, 20))
        self.motor_frame.grid(row=1, column=0, padx=20, pady=20)

        # Create a Canvas for the motor view dial
        self.dial_canvas = tk.Canvas(self.motor_frame, width=250, height=250, bg="white")
        self.dial_canvas.pack()

        # Draw the dial (circle and labels)
        self.draw_dial()

        # Start a thread to update the values
        self.update_thread = threading.Thread(target=self.update_values, daemon=True)
        self.update_thread.start()

    def draw_dial(self):
        # Draw a circular dial
        self.dial_canvas.create_oval(30, 30, 220, 220, outline="black", fill="#ccc", width=4)

        # Draw static labels for 0, 50, and 100 marks
        self.dial_canvas.create_text(190, 125, text="6000", font=("Arial", 8, "bold"))
        self.dial_canvas.create_text(195, 100, text="5400", font=("Arial", 6, "bold"))
        self.dial_canvas.create_text(180, 80, text="4800", font=("Arial", 6, "bold"))
        self.dial_canvas.create_text(165, 65, text="4200", font=("Arial", 6, "bold"))
        self.dial_canvas.create_text(147.5, 55, text="3600", font=("Arial", 6, "bold"))
        self.dial_canvas.create_text(125, 55, text="3000", font=("Arial", 8, "bold"))
        self.dial_canvas.create_text(102.5, 55, text="2400", font=("Arial", 6, "bold"))
        self.dial_canvas.create_text(85, 65, text="1800", font=("Arial", 6, "bold"))
        self.dial_canvas.create_text(70, 80, text="1200", font=("Arial", 6, "bold"))
        self.dial_canvas.create_text(55, 100, text="600", font=("Arial", 6, "bold"))
        self.dial_canvas.create_text(50, 125, text="0", font=("Arial", 8, "bold"))

        self.dial_canvas.create_text(125, 160, text="RPM", font=("Arial", 12, "bold"))

        # Add intermediate markers
        for i in range(0, 110, 10):
            angle = math.radians(180 - (i / 100) * 180)
            x1 = 125 + 80 * math.cos(angle)
            y1 = 125 - 80 * math.sin(angle)
            x2 = 125 + 90 * math.cos(angle)
            y2 = 125 - 90 * math.sin(angle)
            self.dial_canvas.create_line(x1, y1, x2, y2, width=2)

        # Draw the center circle (for aesthetic purposes)
        self.dial_canvas.create_oval(110, 110, 140, 140, outline="black", fill="gray")

        # Initial needle line for the dial
        self.needle = self.dial_canvas.create_line(125, 125, 125, 55, fill="red", width=4)

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
            throttle = 50
            motor_speed = 3000
            # Update the throttle progress bar
            self.throttle_value.set(throttle)
            # Update the throttle label dynamically
            self.throttle_label.config(text=f"Throttle: {throttle}%")
            # Update the needle based on motor speed
            self.update_needle(motor_speed)
        except Exception as e:
            print(f"Error in update thread: {e}")



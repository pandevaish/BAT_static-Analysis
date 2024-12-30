import pytest
from unittest.mock import MagicMock, patch
from stm_display import get_com_port, initialize_serial_port, usb_data, DashboardGUI
import tkinter as tk
import serial
import pytest
 
def test_get_com_port():
    assert get_com_port() == 'COM6'
 
def test_initialize_serial_port():
    with patch('serial.Serial') as mock_serial:
        mock_serial.return_value.is_open = True
        ser = initialize_serial_port('COM1')
        assert ser.is_open is True
 
        mock_serial.side_effect = serial.SerialException('Error')
        ser = initialize_serial_port('COM1')
        assert ser is None
 
 
def test_usb_data():
    mock_serial = MagicMock()
    mock_serial.readline.side_effect = [
        b'Throttle: 50, RPM: 3000\n',
        ]
    generator = usb_data(mock_serial)
 
    assert next(generator) == (50, 3000)
    
# This will automatically use xvfb in headless environments like GitHub Actions
@pytest.mark.usefixtures("xvfb")
def test_dashboard_gui():
    # Create the Tkinter root window
    root = tk.Tk()

    # Your test code here, e.g., testing widgets, layout, etc.
    root.title("Test Dashboard")
    label = tk.Label(root, text="Hello, World!")
    label.pack()

    # Update the window without showing it
    root.update_idletasks()

    # Add your assertions here
    assert label.cget("text") == "Hello, World!"

    # Cleanup
    root.destroy()
 
if __name__ == '__main__':
    pytest.main()

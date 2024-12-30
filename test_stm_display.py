import pytest
from unittest.mock import MagicMock, patch
from stm_display import get_com_port, initialize_serial_port, usb_data, DashboardGUI
import tkinter as tk
import serial
 
def test_get_com_port():
    # with patch('serial.tools.list_ports.comports') as mock_comports:
    #     mock_comports.return_value = [
    #         MagicMock(device='COM1'),
    #         MagicMock(device='COM2')
    #     ]
    #     with patch('builtins.input', return_value='1'):
    #         assert get_com_port() == 'COM1'
 
    #     with patch('builtins.input', return_value='2'):
    #         assert get_com_port() == 'COM2'
 
    #     with patch('builtins.input', return_value='3'):
    #         assert get_com_port() is None
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
        # b'Invalid Data\n',
        # b'Throttle: 20, RPM: 1500\n',
    ]
    generator = usb_data(mock_serial)
 
    assert next(generator) == (50, 3000)
    # with pytest.raises(StopIteration):
    #     assert next(generator)  # Invalid data should not be yielded
    # assert next(generator) == (20, 1500)
 
 
def test_dashboard_gui():
    root = tk.Tk()
    gui = DashboardGUI(root)
 
    # Verify initial throttle value is 0
    assert gui.throttle_value.get() == 0
    gui.throttle_value.set(50)
 
    # Verify the throttle label is updated correctly
    gui.throttle_label.config(text=f"Throttle: {gui.throttle_value.get()}%")
    assert gui.throttle_label.cget("text") == "Throttle: 50%"
 
    # Verify needle position updates without exceptions
    gui.update_needle(3000)
   
    root.destroy()
 
if __name__ == '__main__':
    pytest.main()

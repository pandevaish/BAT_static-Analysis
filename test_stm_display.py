import pytest
from unittest.mock import MagicMock, patch
from stm_display import get_com_port, initialize_serial_port, usb_data, DashboardGUI
import tkinter as tk
import serial

def test_get_com_port_no_ports_available(capfd):
    # Mock list_ports.comports() to return an empty list, simulating no COM ports available
    with patch('serial.tools.list_ports.comports', return_value=[]):
        result = get_com_port()

    # Capture the printed output
    captured = capfd.readouterr()

    # Check the output and the result
    assert result is None
    assert "No COM ports available. Please connect a device and try again." in captured.out


def test_get_com_port_with_available_ports_valid_choice(capfd):
    # Mock list_ports.comports() to return a list with 2 COM ports
    mock_ports = [MagicMock(device='COM1'), MagicMock(device='COM2')]
    with patch('serial.tools.list_ports.comports', return_value=mock_ports):
        # Mock input() to simulate the user selecting the first COM port (1)
        with patch('builtins.input', return_value='1'):
            result = get_com_port()

    # Capture the printed output
    captured = capfd.readouterr()

    # Check the result and the printed output
    assert result == 'COM1'
    assert "Available COM ports:" in captured.out
    assert "1: COM1" in captured.out
    assert "2: COM2" in captured.out


def test_get_com_port_with_available_ports_invalid_choice(capfd):
    # Mock list_ports.comports() to return a list with 2 COM ports
    mock_ports = [MagicMock(device='COM1'), MagicMock(device='COM2')]
    with patch('serial.tools.list_ports.comports', return_value=mock_ports):
        # Mock input() to simulate the user selecting an invalid choice (e.g., 3, which is out of range)
        with patch('builtins.input', return_value='3'):
            result = get_com_port()

    # Capture the printed output
    captured = capfd.readouterr()

    # Check the result and the printed output
    assert result is None
    assert "Invalid selection. Exiting." in captured.out


def test_get_com_port_with_invalid_input(capfd):
    # Mock list_ports.comports() to return a list with 2 COM ports
    mock_ports = [MagicMock(device='COM1'), MagicMock(device='COM2')]
    with patch('serial.tools.list_ports.comports', return_value=mock_ports):
        # Mock input() to simulate the user entering an invalid non-integer value (e.g., 'abc')
        with patch('builtins.input', return_value='abc'):
            result = get_com_port()

    # Capture the printed output
    captured = capfd.readouterr()

    # Check the result and the printed output
    assert result is None
    assert "Invalid selection. Exiting." in captured.out


def test_initialize_serial_port():
    with patch('serial.Serial') as mock_serial:
        mock_serial.return_value.is_open = True
        ser = initialize_serial_port('COM1')
        assert ser.is_open is True

        mock_serial.side_effect = serial.SerialException('Error')
        ser = initialize_serial_port('COM1')
        assert ser is None


def test_usb_data_with_value_error_handling():
    # Create a mock serial object
    mock_serial = MagicMock()

    # Define the side effects for mock_serial.readline()
    # The first one is valid, the second is invalid (will cause ValueError), and the third is valid
    mock_serial.readline.side_effect = [
        b'Throttle: 50, RPM: 3000\n',  # Valid line
        b'Throttle: abc, RPM: def\n',  # Invalid line (will trigger ValueError)
        b'Throttle: 20, RPM: 1500\n',  # Valid line
        b'Throttle: 20\n',             # Invalid line (will return Invalid data format)
    ]

    # Create the generator instance
    generator = usb_data(mock_serial)

    # Test for the first valid data line
    assert next(generator) == (50, 3000)

    # The second line will raise a ValueError when parsing "Throttle: abc" and "RPM: def"
    # The generator should skip this line and proceed to the next one
    assert next(generator) == (20, 1500)

    assert next(generator) == "Invalid data format"

    # Ensure the readline method was called for each of the data lines
    assert mock_serial.readline.call_count == 4

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

def test_update_values_with_exception():
    # Create a mock DashboardGUI instance
    root = tk.Tk()
    gui = DashboardGUI(root)

    # Mock the throttle_value, throttle_label, and update_needle
    gui.throttle_value = MagicMock()
    gui.throttle_label = MagicMock()
    gui.update_needle = MagicMock()

    # Simulate an exception in the update_needle method
    gui.update_needle.side_effect = Exception("Simulated Exception")

    # Call the update_values method
    gui.update_values()

    # Verify that set and config were called as expected
    gui.throttle_value.set.assert_called_once_with(50)
    gui.throttle_label.config.assert_called_once_with(text="Throttle: 50%")

    # Verify that update_needle was called even though it raised an exception
    gui.update_needle.assert_called_once_with(3000)

    # Since we are handling the exception in the method, no crash should occur and nothing else needs to be asserted about the exception handling.
    root.destroy()

if __name__ == '__main__':
    pytest.main()

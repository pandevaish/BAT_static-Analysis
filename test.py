import unittest
from unittest.mock import patch, MagicMock
import main

class TestMain(unittest.TestCase):
    @patch("serial.tools.list_ports.comports")
    def test_get_com_port(self, mock_comports):
        # Mock available COM ports
        mock_comports.return_value = [MagicMock(device="COM1"), MagicMock(device="COM2")]

        with patch("builtins.input", return_value="1"):
            result = main.get_com_port()
            self.assertEqual(result, "COM1")

    @patch("serial.Serial")
    def test_initialize_serial_port_success(self, mock_serial):
        # Mock successful serial port opening
        mock_serial.return_value.is_open = True
        result = main.initialize_serial_port("COM1")
        self.assertIsNotNone(result)

    @patch("serial.Serial")
    def test_initialize_serial_port_failure(self, mock_serial):
        # Mock serial port failure
        mock_serial.side_effect = Exception("Failed to open serial port")
        result = main.initialize_serial_port("COM1")
        self.assertIsNone(result)

    @patch("serial.Serial")
    def test_usb_data_valid_format(self, mock_serial):
        # Mock serial data input
        mock_serial.readline.side_effect = [
            b"Throttle: 50, RPM: 3000\n",
            b"Throttle: 75, RPM: 4500\n",
            b"",
        ]
        data_gen = main.usb_data(mock_serial)
        self.assertEqual(next(data_gen), (50, 3000))
        self.assertEqual(next(data_gen), (75, 4500))

    @patch("serial.Serial")
    def test_usb_data_invalid_format(self, mock_serial):
        # Mock serial data input with invalid format
        mock_serial.readline.side_effect = [
            b"Invalid data\n",
            b"Throttle: Fifty, RPM: Three Thousand\n",
            b"",
        ]
        data_gen = main.usb_data(mock_serial)
        with self.assertRaises(StopIteration):
            next(data_gen)

    @patch("tkinter.IntVar")
    @patch("tkinter.ttk.Progressbar")
    @patch("tkinter.Canvas")
    def test_dashboard_gui(self, mock_canvas, mock_progressbar, mock_intvar):
        # Mock Tkinter widgets
        root_mock = MagicMock()
        gui = main.DashboardGUI(root_mock)

        # Test throttle bar updates
        gui.throttle_value.set(50)
        mock_progressbar.assert_called_once_with(
            gui.throttle_frame, orient="horizontal", mode="determinate",
            variable=mock_intvar.return_value, length=300, maximum=100
        )

        # Test needle update
        gui.update_needle(3000)
        mock_canvas.return_value.coords.assert_called_once()

---

### **Run the Tests**

Run the tests using the `pytest` or `unittest` command:
```bash
pytest test_main.py

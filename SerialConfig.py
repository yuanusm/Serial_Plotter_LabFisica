import serial
import serial.tools.list_ports
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox

from Data_Manager import DataManager


class SerialManager:
    """Lee líneas completas del puerto sin bloquear la interfaz gráfica."""

    MAX_LINES_PER_TICK = 200

    def __init__(self, ui):
        self.ui = ui
        self.serial = None
        self.is_connected = False
        self.port = None
        self.baudrate = None
        self.data_manager = DataManager(ui)
        self.on_disconnected = None
        self._line_buffer = bytearray()
        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_data)
        self.read_timer.start(20)

    def read_data(self):
        if not self.serial or not self.is_connected:
            return
        try:
            available = self.serial.in_waiting
            if available <= 0:
                return
            self._line_buffer.extend(self.serial.read(available))
            lines = self._line_buffer.split(b"\n")
            tail = lines.pop()
            ready, deferred = lines[:self.MAX_LINES_PER_TICK], lines[self.MAX_LINES_PER_TICK:]
            self._line_buffer = bytearray(b"\n".join(deferred + [tail]))
            for raw_data in ready:
                decoded = raw_data.decode("utf-8", errors="replace").strip()
                if decoded:
                    self.data_manager.process_data(decoded)
        except (serial.SerialException, OSError):
            self.handle_disconnection()

    def connect(self, port, baudrate):
        try:
            self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=0.1)
            self.is_connected = True
            self.port = port
            self.baudrate = baudrate
            self.ui.pushButton_Conectar.setText("Desconectar")
            self.ui.pushButton_Detener.setEnabled(False)
            self.ui.ConfirmacionConectado.setText(f"Conectado a {port} a {baudrate} baudios")
            self.ui.ConfirmacionConectado.setStyleSheet("color: green;")
        except serial.SerialException as error:
            QMessageBox.warning(None, "Error de conexión", f"El puerto no se pudo conectar.\n\n{error}")

    def write_data(self, data):
        if not self.serial or not self.is_connected:
            return False
        try:
            self.serial.write(data.encode())
            return True
        except (serial.SerialException, OSError):
            self.handle_disconnection()
            return False

    def handle_disconnection(self):
        if self.is_connected:
            self.disconnect(message="Dispositivo desconectado físicamente", color="red")
            QMessageBox.warning(None, "Desconexión", "El dispositivo USB se ha desconectado físicamente.")

    def disconnect(self, message="Desconectado manualmente", color="gray"):
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.is_connected = False
        self.serial = None
        self.ui.pushButton_Conectar.setText("Conectar")
        self.ui.pushButton_Detener.setEnabled(False)
        self.ui.ConfirmacionConectado.setText(message)
        self.ui.ConfirmacionConectado.setStyleSheet(f"color: {color};")
        if self.on_disconnected is not None:
            self.on_disconnected(message)

    def list_ports(self):
        return [(port.device, f"{port.device} - {port.description}") for port in serial.tools.list_ports.comports()]

    def check_connection(self):
        if not self.is_connected:
            return False
        if self.port not in [port.device for port in serial.tools.list_ports.comports()]:
            self.handle_disconnection()
            return False
        return True

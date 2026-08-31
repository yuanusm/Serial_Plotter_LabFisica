import serial
import serial.tools.list_ports
from PySide6.QtWidgets import QMessageBox
from ui.main_window_ui import Ui_MainWindow
from PySide6.QtWidgets import QMainWindow
from Data_Manager import DataManager
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QTableWidgetItem, QHeaderView, QMessageBox
import serial
import serial.tools.list_ports

class SerialManager:
    def __init__(self, ui):
        self.ui = ui
        self.serial = None
        self.is_connected = False
        self.port = None
        self.baudrate = None
        self.data_manager = DataManager(ui)
        
        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_data)
        self.read_timer.start(20)  # Leer cada 20ms
    
    def read_data(self):
        """Lee datos del puerto serial"""
        if not self.serial or not self.is_connected:
            return
        
        try:
            if self.serial.in_waiting > 0:
                data = self.serial.readline().decode('utf-8').strip()
                if data:
                    # Procesar datos con DataManager
                    self.data_manager.process_data(data)
                    
        except (serial.SerialException, OSError) as e:
            # Puerto desconectado
            self.handle_disconnection()

    def connect(self, port, baudrate):
        try:
            self.serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=0.1
            )
            self.is_connected = True
            self.port = port
            self.baudrate = baudrate
            
            QMessageBox.information(None, "Éxito", f"Conexión establecida en {port}")
            self.ui.pushButton_Conectar.setEnabled(False)
            self.ui.pushButton_Detener.setEnabled(True)
            self.ui.ConfirmacionConectado.setText(f"Conectado a {port} a {baudrate} baudios")
            self.ui.ConfirmacionConectado.setStyleSheet("color: green;")
            
        except serial.SerialException:
            QMessageBox.warning(
                None,
                "Error de conexión",
                f"Puerto: {port}\nBaudrate: {baudrate}\n\nEl puerto no se pudo conectar."
            )

    # def read_data(self):
        # """Lee datos del puerto serial y maneja desconexiones físicas"""
        # if not self.serial or not self.is_connected:
            # return None
            
        # try:
            # if self.serial.in_waiting > 0:
                # data = self.serial.readline().decode('utf-8').strip()
                # return data
            # return None
            
        # except (serial.SerialException, OSError) as e:
            #Puerto desconectado físicamente
            # self.handle_disconnection()
            # return None

    def write_data(self, data):
        """Escribe datos al puerto serial"""
        if not self.serial or not self.is_connected:
            return False
            
        try:
            self.serial.write(data.encode())
            return True
            
        except (serial.SerialException, OSError) as e:
            # Puerto desconectado físicamente
            self.handle_disconnection()
            return False

    def handle_disconnection(self):
        """Maneja la desconexión física del dispositivo"""
        if self.is_connected:
            self.is_connected = False
            self.serial = None
            
            # Actualizar UI
            self.ui.pushButton_Conectar.setEnabled(True)
            self.ui.pushButton_Detener.setEnabled(False)
            self.ui.ConfirmacionConectado.setText("Dispositivo desconectado físicamente")
            self.ui.ConfirmacionConectado.setStyleSheet("color: red;")
            
            # Mostrar mensaje
            QMessageBox.warning(
                None,
                "Desconexión",
                "El dispositivo USB se ha desconectado físicamente.\n\nVerifique la conexión e intente reconectar."
            )

    def disconnect(self):
        """Desconexión manual"""
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.is_connected = False
        self.serial = None
        
        self.ui.pushButton_Conectar.setEnabled(True)
        self.ui.pushButton_Detener.setEnabled(False)
        self.ui.ConfirmacionConectado.setText("Desconectado manualmente")
        self.ui.ConfirmacionConectado.setStyleSheet("color: gray;")


    def list_ports(self):
        """Devuelve lista de tuplas (port, description)"""
        ports = []
        for port in serial.tools.list_ports.comports():
            # Formato: "COM9 - Driver CH340 (COM9)" o similar
            description = f"{port.device} - {port.description}"
            ports.append((port.device, description))
        return ports
        
    def check_connection(self):
        """Verifica periódicamente si el puerto sigue conectado"""
        if not self.is_connected:
            return False
            
        try:
            # Verificar si el puerto todavía existe en el sistema
            available_ports = [port.device for port in serial.tools.list_ports.comports()]
            if self.port not in available_ports:
                self.handle_disconnection()
                return False
            return True
            
        except Exception:
            self.handle_disconnection()
            return False
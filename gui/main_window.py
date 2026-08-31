from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import QTimer
from ui.main_window_ui import Ui_MainWindow
from Data_Manager import DataManager
from SerialConfig import SerialManager

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_connections()
        self.serial_manager = SerialManager(self.ui)
        
        self.ui.comboBox_Baud.clear()
        self.ui.comboBox_Baud.addItems([
        "9600",
        "19200",
        "38400",
        "57600",
        "115200"
        ])
        self.ui.comboBox_Baud.setCurrentText("9600")
        
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.check_serial_connection)
        self.connection_timer.start(2000)  # Cada 2 segundos

    def setup_connections(self):

        self.ui.pushButton_Iniciar.clicked.connect(
            self.start_acquisition
        )

        self.ui.pushButton_Detener.clicked.connect(
            self.stop_acquisition
        )
        
        self.ui.pushButton_Actualizar.clicked.connect(
            self.Actualizar_Lista_Puertos
        )
        
        self.ui.pushButton_Conectar.clicked.connect(
            self.Conectar_COM
        )

    def start_acquisition(self):

        print("Adquisición iniciada")

    def stop_acquisition(self):

        print("Adquisición detenida")
        self.serial_manager.disconnect()
        self.ui.pushButton_Conectar.setEnabled(True)
        self.ui.pushButton_Detener.setEnabled(False)
        self.ui.ConfirmacionConectado.setText(f"Desconectado")
        self.ui.ConfirmacionConectado.setStyleSheet("color: gray;")
        
        
        
        
    def Actualizar_Lista_Puertos(self):
        ports_info = self.serial_manager.list_ports()
        
        self.ui.comboBox_COM.clear()
        
        # Guardar los datos completos en el comboBox
        for port, description in ports_info:
            self.ui.comboBox_COM.addItem(description, port)  # Guardamos el puerto como data
        
    def Conectar_COM(self):
        baudrate = int(self.ui.comboBox_Baud.currentText())
        
        # Obtener el puerto real desde el data almacenado
        port = self.ui.comboBox_COM.currentData()  # Esto devuelve "COM9" o "COM10"
        
        if port:  # Verificar que hay un puerto seleccionado
            self.serial_manager.connect(port, baudrate)
        
    def check_serial_connection(self):
        """Verifica si el puerto serial sigue conectado"""
        if self.serial_manager.is_connected:
            self.serial_manager.check_connection()
    
        
        # En tu main_window.py o donde configures la UI
    def setup_table(self):
        """Configura la tabla con columnas dinámicas"""
        # Configurar columnas base
        self.ui.tableWidget.setColumnCount(2)  # N° y Timestamp
        self.ui.tableWidget.setHorizontalHeaderLabels(['N°', 'Timestamp'])
        
        # Conectar checkboxes a actualización de columnas
        self.ui.checkBox_1.stateChanged.connect(self.update_table_columns)
        self.ui.checkBox_2.stateChanged.connect(self.update_table_columns)
        self.ui.checkBox_3.stateChanged.connect(self.update_table_columns)
        self.ui.checkBox_4.stateChanged.connect(self.update_table_columns)

    def update_table_columns(self):
        """Actualiza las columnas de la tabla según checkboxes seleccionados"""
        selected = self.get_selected_channels()
        
        # Contar columnas: N° (1) + Timestamp (1) + canales seleccionados
        num_columns = 2 + len(selected)
        self.ui.tableWidget.setColumnCount(num_columns)
        
        # Establecer headers
        headers = ['N°', 'Timestamp']
        for ch in selected:
            headers.append(f'T_{ch+1}')
        self.ui.tableWidget.setHorizontalHeaderLabels(headers)
        
        # Ajustar tamaño de columnas
        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        
        
    def on_start_recording(self):
        """Inicia grabación"""
        if not self.serial_manager.is_connected:
            QMessageBox.warning(None, "Error", "Conéctese al puerto primero")
            return
        
        self.data_manager.start_recording()
        self.ui.pushButton_Iniciar.setEnabled(False)
        self.ui.pushButton_Detener.setEnabled(True)

    def on_stop_recording(self):
        """Detiene grabación"""
        self.data_manager.stop_recording()
        self.ui.pushButton_Iniciar.setEnabled(True)
        self.ui.pushButton_Detener.setEnabled(False)

    def on_export_data(self):
        """Exporta datos del buffer"""
        self.data_manager.export_all_data()
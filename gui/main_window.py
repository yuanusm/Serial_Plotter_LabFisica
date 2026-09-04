from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QMainWindow, QMessageBox

from gui.plot_widget import PlotWidget
from SerialConfig import SerialManager
from ui.main_window_ui import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.serial_manager = SerialManager(self.ui)
        self.serial_manager.on_disconnected = self._serial_disconnected
        self.setup_table()
        self.setup_plot()
        # Mostrar los cuatro datos por defecto; se siguen registrando todos aunque
        # el usuario oculte uno de ellos.
        for checkbox in (self.ui.checkBox_1, self.ui.checkBox_2, self.ui.checkBox_3, self.ui.checkBox_4):
            checkbox.setChecked(True)

        self.ui.comboBox_Baud.clear()
        self.ui.comboBox_Baud.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.ui.comboBox_Baud.setCurrentText("9600")
        self.setup_connections()
        self.ui.pushButton_Detener.setEnabled(False)
        self.ui.spinBox.setValue(0)
        self.ui.spinBox_2.setValue(360)
        self.ui.spinBox_3.setValue(-10)
        self.ui.spinBox_4.setValue(100)
        self.ui.spinBox_5.setRange(1, 9999)
        self.ui.spinBox_5.setValue(1)
        self.ui.label_7.setText("Temperatura: --.--")
        temperature_font = QFont(self.ui.label_7.font())
        temperature_font.setPointSize(max(18, temperature_font.pointSize() * 2))
        temperature_font.setBold(True)
        self.ui.label_7.setFont(temperature_font)
        self.Actualizar_Lista_Puertos()

        self.connection_timer = QTimer(self)
        self.connection_timer.timeout.connect(self.check_serial_connection)
        self.connection_timer.start(2000)
        self.acquisition_remaining = 0
        self.acquisition_timer = QTimer(self)
        self.acquisition_timer.timeout.connect(self._on_acquisition_tick)

    @property
    def data_manager(self):
        return self.serial_manager.data_manager

    def setup_connections(self):
        self.ui.pushButton_Iniciar.clicked.connect(self.start_acquisition)
        self.ui.pushButton_Detener.clicked.connect(self.stop_acquisition)
        self.ui.pushButton_Actualizar.clicked.connect(self.Actualizar_Lista_Puertos)
        self.ui.pushButton_Conectar.clicked.connect(self.Conectar_COM)
        self.ui.pushButton.clicked.connect(self.on_export_data)
        self.ui.pushButton_2.clicked.connect(self.start_timed_acquisition)
        for spinbox in (self.ui.spinBox, self.ui.spinBox_2, self.ui.spinBox_3, self.ui.spinBox_4):
            spinbox.valueChanged.connect(self.update_plot_limits)

    def start_acquisition(self):
        if not self.serial_manager.is_connected:
            QMessageBox.warning(self, "Error", "Conéctese al puerto primero")
            return False
        if self.data_manager.start_recording():
            self.plot_widget.clear_data()
            self.ui.pushButton_Iniciar.setEnabled(False)
            self.ui.pushButton_Detener.setEnabled(True)
            self.ui.ConfirmacionConectado.setText("Conectado y grabando")
            return True
        return False

    def start_timed_acquisition(self):
        """Inicia una sesión y la detiene automáticamente al vencer los minutos."""
        if not self.start_acquisition():
            return
        minutes = self.ui.spinBox_5.value()
        self.acquisition_remaining = minutes * 60
        self.ui.pushButton_2.setEnabled(False)
        self._update_countdown()
        self.acquisition_timer.start(1000)

    def stop_acquisition(self):
        if hasattr(self, "acquisition_timer"):
            self.acquisition_timer.stop()
        self.ui.pushButton_2.setEnabled(True)
        self.data_manager.stop_recording()
        self.ui.pushButton_Iniciar.setEnabled(True)
        self.ui.pushButton_Detener.setEnabled(False)

    def Actualizar_Lista_Puertos(self):
        self.ui.comboBox_COM.clear()
        for port, description in self.serial_manager.list_ports():
            self.ui.comboBox_COM.addItem(description, port)

    def Conectar_COM(self):
        if self.serial_manager.is_connected:
            self.data_manager.stop_recording()
            self.serial_manager.disconnect()
            self.ui.pushButton_Iniciar.setEnabled(True)
            self.ui.pushButton_Detener.setEnabled(False)
            return
        port = self.ui.comboBox_COM.currentData()
        if not port:
            QMessageBox.warning(self, "Sin puerto", "Actualice la lista y seleccione un puerto COM.")
            return
        self.serial_manager.connect(port, int(self.ui.comboBox_Baud.currentText()))

    def check_serial_connection(self):
        if self.serial_manager.is_connected:
            self.serial_manager.check_connection()

    def _serial_disconnected(self):
        """Detiene el contador y devuelve los controles a un estado seguro."""
        if hasattr(self, "acquisition_timer"):
            self.acquisition_timer.stop()
        self.ui.pushButton_Iniciar.setEnabled(True)
        self.ui.pushButton_Detener.setEnabled(False)
        self.ui.pushButton_2.setEnabled(True)

    def setup_table(self):
        for checkbox in (
            self.ui.checkBox_1,
            self.ui.checkBox_2,
            self.ui.checkBox_3,
            self.ui.checkBox_4):
            checkbox.stateChanged.connect(self.update_table_columns)

        table = self.ui.tableWidget
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        header = table.horizontalHeader()
        header.setStretchLastSection(False)

        self.update_table_columns()

        # Forzar actualización de la tabla
        table.resizeColumnsToContents()

        for column in range(table.columnCount()):
            header.setSectionResizeMode(column, QHeaderView.Stretch)

        table.viewport().update()
        table.update()

    def update_table_columns(self):
        selected = self.data_manager.get_selected_channels()
        self.ui.tableWidget.setColumnCount(6)
        headers = ["N°", "Tiempo", "T_1", "T_2", "T_3", "T_4"]
        self.ui.tableWidget.setHorizontalHeaderLabels(headers)
        for channel in range(4):
            self.ui.tableWidget.setColumnHidden(channel + 2, channel not in selected)
        # Las columnas visibles se reparten siempre el ancho disponible, por lo
        # que ninguna queda oculta detrás de una barra horizontal.
        self.ui.tableWidget.resizeColumnsToContents()
        if hasattr(self, "plot_widget"):
            self.update_plot_data()

    def setup_plot(self):
        layout = self.ui.widget.layout()
        if layout is None:
            from PySide6.QtWidgets import QVBoxLayout

            layout = QVBoxLayout(self.ui.widget)
            layout.setContentsMargins(0, 0, 0, 0)
        self.plot_widget = PlotWidget(self.ui.widget)
        layout.addWidget(self.plot_widget)
        self.data_manager.on_data_added = self.plot_widget.append_sample
        self.data_manager.on_temperature_changed = self.update_temperature
        self.update_plot_limits()

    def update_temperature(self, value):
        self.ui.label_7.setText(f"Temp Sensor 1: {value:.2f}")

    def _update_countdown(self):
        minutes, seconds = divmod(self.acquisition_remaining, 60)
        self.ui.ConfirmacionConectado.setText(f"Grabando — restante: {minutes:02d}:{seconds:02d}")

    def _on_acquisition_tick(self):
        self.acquisition_remaining -= 1
        if self.acquisition_remaining <= 0:
            self.stop_acquisition()
            self.ui.ConfirmacionConectado.setText("Adquisición temporizada finalizada")
            return
        self._update_countdown()

    def update_plot_data(self):
        """Actualiza sólo la configuración; las muestras llegan incrementalmente."""
        self.plot_widget.set_channels(self.data_manager.get_selected_channels())

    def update_plot_limits(self):
        self.plot_widget.set_limits(
            self.ui.spinBox.value(),
            self.ui.spinBox_2.value(),
            self.ui.spinBox_3.value(),
            self.ui.spinBox_4.value(),
        )

    def on_export_data(self):
        self.data_manager.export_all_data()

    def closeEvent(self, event):
        """Garantiza que las últimas muestras pendientes lleguen al CSV al cerrar."""
        self.data_manager.shutdown()
        self.serial_manager.disconnect()
        event.accept()

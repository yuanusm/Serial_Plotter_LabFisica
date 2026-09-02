import time

from PySide6.QtCore import QSettings, QSignalBlocker, QTimer
from PySide6.QtWidgets import QHeaderView, QMainWindow, QMessageBox, QPushButton

from gui.plot_widget import PlotWidget
from gui.settings_dialog import SettingsDialog
from SerialConfig import SerialManager
from ui.main_window_ui import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow(); self.ui.setupUi(self)
        self.serial_manager = SerialManager(self.ui)
        self.serial_manager.on_disconnected = self._serial_disconnected
        self._timed_deadline = None
        self._settings = QSettings("LabFisica", "SerialPlotter")
        self.setup_table(); self.setup_plot()
        for checkbox in (self.ui.checkBox_1, self.ui.checkBox_2, self.ui.checkBox_3, self.ui.checkBox_4): checkbox.setChecked(True)
        self.ui.comboBox_Baud.clear(); self.ui.comboBox_Baud.addItems(["9600", "19200", "38400", "57600", "115200"]); self.ui.comboBox_Baud.setCurrentText("115200")
        self.ui.spinBox.setValue(0); self.ui.spinBox_2.setValue(300); self.ui.spinBox_3.setValue(-127); self.ui.spinBox_4.setValue(100)
        self.ui.spinBox_5.setRange(1, 9999); self.ui.spinBox_5.setValue(1)
        self._add_settings_button(); self.setup_connections(); self._apply_plot_settings(self._load_plot_settings())
        self.ui.pushButton_Detener.setEnabled(False); self.Actualizar_Lista_Puertos()
        self.connection_timer = QTimer(self); self.connection_timer.timeout.connect(self.check_serial_connection); self.connection_timer.start(2000)
        self.countdown_timer = QTimer(self); self.countdown_timer.setInterval(250); self.countdown_timer.timeout.connect(self._update_countdown)

    @property
    def data_manager(self): return self.serial_manager.data_manager

    def _add_settings_button(self):
        self.settings_button = QPushButton("Settings", self.ui.groupBox)
        self.ui.gridLayout_3.addWidget(self.settings_button, 0, 7, 1, 1)

    def setup_connections(self):
        self.ui.pushButton_Iniciar.clicked.connect(self.start_acquisition)
        self.ui.pushButton_Detener.clicked.connect(self.stop_acquisition)
        self.ui.pushButton_Actualizar.clicked.connect(self.Actualizar_Lista_Puertos)
        self.ui.pushButton_Conectar.clicked.connect(self.Conectar_COM)
        self.ui.pushButton.clicked.connect(self.on_export_data)
        self.ui.pushButton_2.clicked.connect(self.start_timed_acquisition)
        self.settings_button.clicked.connect(self.open_settings)
        for spinbox in (self.ui.spinBox, self.ui.spinBox_2, self.ui.spinBox_3, self.ui.spinBox_4): spinbox.valueChanged.connect(self.update_plot_limits)

    def start_acquisition(self):
        if not self.serial_manager.is_connected:
            QMessageBox.warning(self, "Error", "Conéctese al puerto primero"); return False
        if self.data_manager.start_recording():
            self.ui.pushButton_Iniciar.setEnabled(False); self.ui.pushButton_Detener.setEnabled(True)
            self.ui.ConfirmacionConectado.setText("Conectado y grabando")
            return True
        return False

    def stop_acquisition(self):
        self.countdown_timer.stop(); self._timed_deadline = None
        self.data_manager.stop_recording()
        self.ui.pushButton_Iniciar.setEnabled(True); self.ui.pushButton_Detener.setEnabled(False)
        self.ui.pushButton_2.setText("Tomar Datos Durante X Minutos")

    def start_timed_acquisition(self):
        if self.data_manager.is_recording:
            return
        if self.start_acquisition():
            self._timed_deadline = time.monotonic() + self.ui.spinBox_5.value() * 60
            self.countdown_timer.start(); self._update_countdown()

    def _update_countdown(self):
        remaining = max(0, int(self._timed_deadline - time.monotonic() + .999))
        if remaining <= 0:
            self.stop_acquisition(); return
        self.ui.pushButton_2.setText(f"Deteniendo en {remaining // 60}:{remaining % 60:02d}")

    def _serial_disconnected(self, message):
        if self.data_manager.is_recording: self.stop_acquisition()

    def Actualizar_Lista_Puertos(self):
        self.ui.comboBox_COM.clear()
        for port, description in self.serial_manager.list_ports(): self.ui.comboBox_COM.addItem(description, port)

    def Conectar_COM(self):
        if self.serial_manager.is_connected:
            self.stop_acquisition(); self.serial_manager.disconnect(); return
        port = self.ui.comboBox_COM.currentData()
        if not port:
            QMessageBox.warning(self, "Sin puerto", "Actualice la lista y seleccione un puerto COM."); return
        self.serial_manager.connect(port, int(self.ui.comboBox_Baud.currentText()))

    def check_serial_connection(self):
        if self.serial_manager.is_connected: self.serial_manager.check_connection()

    def setup_table(self):
        for checkbox in (self.ui.checkBox_1, self.ui.checkBox_2, self.ui.checkBox_3, self.ui.checkBox_4): checkbox.stateChanged.connect(self.update_table_columns)
        self.update_table_columns(); self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def update_table_columns(self):
        selected = self.data_manager.get_selected_channels(); self.ui.tableWidget.setColumnCount(6)
        self.ui.tableWidget.setHorizontalHeaderLabels(["N°", "Timestamp", "T_1", "T_2", "T_3", "T_4"])
        for channel in range(4): self.ui.tableWidget.setColumnHidden(channel + 2, channel not in selected)
        if hasattr(self, "plot_widget"): self.update_plot_data()

    def setup_plot(self):
        layout = self.ui.widget.layout()
        if layout is None:
            from PySide6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self.ui.widget); layout.setContentsMargins(0, 0, 0, 0)
        self.plot_widget = PlotWidget(self.ui.widget); layout.addWidget(self.plot_widget)
        self.data_manager.on_data_added = self.update_plot_data
        self.plot_widget.viewLimitsChanged.connect(self._sync_limits_from_plot)
        self.update_plot_limits()

    def update_plot_data(self): self.plot_widget.set_data(self.data_manager.data_buffer, self.data_manager.get_selected_channels(), self.data_manager.total_samples)
    def update_plot_limits(self): self.plot_widget.set_limits(self.ui.spinBox.value(), self.ui.spinBox_2.value(), self.ui.spinBox_3.value(), self.ui.spinBox_4.value())

    def _sync_limits_from_plot(self, x_min, x_max, y_min, y_max):
        for box, value in zip((self.ui.spinBox, self.ui.spinBox_2, self.ui.spinBox_3, self.ui.spinBox_4), (round(x_min), round(x_max), round(y_min), round(y_max))):
            with QSignalBlocker(box): box.setValue(value)

    def _load_plot_settings(self):
        return {"colors": [self._settings.value(f"plot/color{i}", color) for i, color in enumerate(PlotWidget.DEFAULT_COLORS)], "cursor_colors": [self._settings.value("plot/cursor1", "#00bcd4"), self._settings.value("plot/cursor2", "#e91e63")], "background": self._settings.value("plot/background", "#ffffff"), "line_width": int(self._settings.value("plot/width", 2)), "decimation": self._settings.value("plot/decimation", "medium")}

    def _apply_plot_settings(self, values):
        self.plot_widget.set_style(**values)
        for i, color in enumerate(values["colors"]): self._settings.setValue(f"plot/color{i}", color)
        self._settings.setValue("plot/cursor1", values["cursor_colors"][0]); self._settings.setValue("plot/cursor2", values["cursor_colors"][1]); self._settings.setValue("plot/background", values["background"]); self._settings.setValue("plot/width", values["line_width"]); self._settings.setValue("plot/decimation", values["decimation"])

    def open_settings(self):
        dialog = SettingsDialog({**self._load_plot_settings(), "colors": self._load_plot_settings()["colors"] + self._load_plot_settings()["cursor_colors"] + [self._load_plot_settings()["background"]]}, self)
        dialog.apply_settings = self._apply_plot_settings
        dialog.exec()

    def on_export_data(self): self.data_manager.export_all_data()

    def closeEvent(self, event):
        self.connection_timer.stop(); self.countdown_timer.stop(); self.data_manager.shutdown(); self.serial_manager.disconnect(); event.accept()

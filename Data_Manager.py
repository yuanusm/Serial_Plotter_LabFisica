"""Almacenamiento y presentación de las muestras recibidas por el puerto serie."""

import csv
import os
from collections import deque
from datetime import datetime

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem


class DataManager:
    """Conserva una ventana acotada en RAM y guarda la adquisición completa en CSV.

    ``data_buffer`` es deliberadamente circular: sirve para la vista y una
    exportación rápida, no para conservar una adquisición indefinida. Durante
    una grabación cada muestra válida se añade también a ``file_buffer`` y se
    vacía al CSV como máximo cada segundo o al reunir 250 muestras.
    """

    MEMORY_BUFFER_SIZE = 10_000
    FILE_BUFFER_SIZE = 250
    MAX_DISPLAY_ROWS = 1_000

    def __init__(self, ui):
        self.ui = ui
        self.data_buffer = deque(maxlen=self.MEMORY_BUFFER_SIZE)
        self.file_buffer = []
        self.is_recording = False
        self.current_file = None
        self.csv_writer = None
        self.total_samples = 0
        self.on_data_added = None

        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.flush_to_file)
        self.save_timer.start(1000)

    @staticmethod
    def parse_data(data_string):
        """Devuelve exactamente las cuatro lecturas enviadas en una línea COM."""
        try:
            values = [float(value.strip()) for value in data_string.strip().split(",")]
        except (AttributeError, ValueError):
            return None
        return values if len(values) == 4 else None

    def process_data(self, raw_data):
        """Procesa una línea válida sin descartar sensores no visibles en la tabla."""
        values = self.parse_data(raw_data)
        if values is None:
            return False

        self.add_to_buffer([datetime.now(), *values])
        return True

    def get_selected_channels(self):
        return [
            index
            for index, checkbox in enumerate(
                (self.ui.checkBox_1, self.ui.checkBox_2, self.ui.checkBox_3, self.ui.checkBox_4)
            )
            if checkbox.isChecked()
        ]

    def add_to_buffer(self, row_data):
        self.data_buffer.append(row_data)
        self.total_samples += 1

        if self.is_recording:
            self.file_buffer.append(row_data)
            if len(self.file_buffer) >= self.FILE_BUFFER_SIZE:
                self.flush_to_file()

        self.update_table(row_data)
        if self.on_data_added is not None:
            self.on_data_added()

    def update_table(self, row_data):
        """Muestra la muestra nueva usando únicamente los sensores seleccionados."""
        table = self.ui.tableWidget
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(str(self.total_samples)))
        table.setItem(row, 1, QTableWidgetItem(row_data[0].strftime("%H:%M:%S.%f")[:-3]))

        # Las cuatro columnas se mantienen aunque el usuario las oculte. Así un
        # cambio de checkbox no reconstruye ni reinicia las filas existentes.
        for column, value in enumerate(row_data[1:], start=2):
            table.setItem(row, column, QTableWidgetItem(f"{value:.2f}"))

        if table.rowCount() > self.MAX_DISPLAY_ROWS:
            table.removeRow(0)
        table.scrollToBottom()

    @staticmethod
    def _csv_row(row):
        return [row[0].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], *(f"{value:.2f}" for value in row[1:])]

    def flush_to_file(self):
        """Pasa las muestras pendientes a disco; no hace nada fuera de grabación."""
        if not self.file_buffer or not self.is_recording or self.csv_writer is None:
            return
        try:
            self.csv_writer.writerows(self._csv_row(row) for row in self.file_buffer)
            self.current_file.flush()
            self.file_buffer.clear()
        except OSError as error:
            print(f"Error escribiendo archivo: {error}")

    def start_recording(self, filename=None):
        if self.is_recording:
            return False
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename or f"data_{timestamp}.csv"
        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", filename)
        try:
            self.current_file = open(filepath, "w", newline="", encoding="utf-8")
            self.csv_writer = csv.writer(self.current_file)
            # Siempre se guardan los cuatro canales, incluso si no se muestran.
            self.csv_writer.writerow(["Timestamp", "T_1", "T_2", "T_3", "T_4"])
            self.is_recording = True
            print(f"Grabación iniciada: {filepath}")
            return True
        except OSError as error:
            self.current_file = None
            self.csv_writer = None
            QMessageBox.critical(None, "Error", f"No se pudo crear el archivo: {error}")
            return False

    def stop_recording(self):
        if not self.is_recording:
            return
        self.flush_to_file()
        self.current_file.close()
        self.current_file = None
        self.csv_writer = None
        self.is_recording = False
        print(f"Grabación detenida. Total de muestras: {self.total_samples}")

    def clear_buffer(self):
        self.data_buffer.clear()
        self.ui.tableWidget.setRowCount(0)

    def export_all_data(self, filename=None):
        if not self.data_buffer:
            QMessageBox.warning(None, "Sin datos", "No hay datos en el buffer para exportar")
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename or f"export_{timestamp}.csv"
        os.makedirs("exports", exist_ok=True)
        filepath = os.path.join("exports", filename)
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as output_file:
                writer = csv.writer(output_file)
                writer.writerow(["Timestamp", "T_1", "T_2", "T_3", "T_4"])
                writer.writerows(self._csv_row(row) for row in self.data_buffer)
            QMessageBox.information(None, "Exportación exitosa", f"Datos exportados a: {filepath}")
        except OSError as error:
            QMessageBox.critical(None, "Error", f"Error exportando datos: {error}")

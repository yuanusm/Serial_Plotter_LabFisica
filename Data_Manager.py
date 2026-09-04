"""Almacenamiento acotado en memoria y persistencia asíncrona de adquisiciones."""

import csv
import os
from collections import deque
from datetime import datetime

from PySide6.QtCore import QObject, QThread, QTimer, Qt, Signal, Slot
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem


class SessionCsvWriter(QObject):
    """Escritor de una sesión que vive exclusivamente fuera del hilo de la GUI."""

    error = Signal(str)
    closed = Signal()

    def __init__(self):
        super().__init__()
        self._file = None
        self._writer = None

    @Slot(str)
    def open_session(self, filepath):
        try:
            self._file = open(filepath, "w", newline="", encoding="utf-8")
            self._writer = csv.writer(self._file)
            self._writer.writerow(["N°", "Timestamp", "T1", "T2", "T3", "T4"])
            self._file.flush()
        except OSError as error:
            self._file = self._writer = None
            self.error.emit(f"No se pudo crear el archivo: {error}")

    @Slot(object)
    def write_batch(self, rows):
        if self._writer is None:
            return
        try:
            self._writer.writerows(rows)
            self._file.flush()
        except OSError as error:
            self.error.emit(f"Error escribiendo archivo: {error}")

    @Slot()
    def close_session(self):
        try:
            if self._file is not None:
                self._file.flush()
                self._file.close()
        except OSError as error:
            self.error.emit(f"Error cerrando archivo: {error}")
        finally:
            self._file = self._writer = None
            self.closed.emit()


class DataManager(QObject):
    """Mantiene 100.000 muestras en RAM y el histórico completo en el CSV maestro."""

    MEMORY_BUFFER_SIZE = 100_000
    FILE_BUFFER_SIZE = 100
    MAX_DISPLAY_ROWS = 500

    open_requested = Signal(str)
    write_requested = Signal(object)
    close_requested = Signal()

    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.data_buffer = deque(maxlen=self.MEMORY_BUFFER_SIZE)
        self.file_buffer = []
        self.table_buffer = []
        self.is_recording = False
        self.total_samples = 0
        self.on_data_added = None
        self.acquisition_started_at = None
        self.session_filepath = None

        self._writer_thread = QThread(self)
        self._writer = SessionCsvWriter()
        self._writer.moveToThread(self._writer_thread)
        self.open_requested.connect(self._writer.open_session)
        self.write_requested.connect(self._writer.write_batch)
        self.close_requested.connect(self._writer.close_session)
        self._writer.error.connect(self._show_writer_error)
        self._writer.closed.connect(self._writer_thread.quit, Qt.DirectConnection)
        self._writer_thread.start()

        # La tabla es una vista; agruparla evita modificar widgets 100 veces/s.
        self.table_timer = QTimer(self)
        self.table_timer.timeout.connect(self.flush_table)
        self.table_timer.start(100)
        # Entrega lotes al escritor sin E/S en el hilo principal.
        self.save_timer = QTimer(self)
        self.save_timer.timeout.connect(self.flush_to_file)
        self.save_timer.start(500)

    @staticmethod
    def parse_data(data_string):
        try:
            values = [float(value.strip()) for value in data_string.strip().split(",")]
        except (AttributeError, ValueError):
            return None
        return values if len(values) == 4 else None

    def process_data(self, raw_data):
        """Procesa una línea con trabajo constante y sin E/S de disco."""
        if not self.is_recording:
            return False
        values = self.parse_data(raw_data)
        if values is None:
            return False
        elapsed_seconds = (datetime.now() - self.acquisition_started_at).total_seconds()
        self.total_samples += 1
        row = [self.total_samples, elapsed_seconds, *values]
        self.data_buffer.append(row)
        self.file_buffer.append(self._csv_row(row))
        self.table_buffer.append(row)
        if len(self.file_buffer) >= self.FILE_BUFFER_SIZE:
            self.flush_to_file()
        if self.on_data_added is not None:
            self.on_data_added(row)
        return True

    def get_selected_channels(self):
        return [
            index for index, checkbox in enumerate(
                (self.ui.checkBox_1, self.ui.checkBox_2, self.ui.checkBox_3, self.ui.checkBox_4)
            ) if checkbox.isChecked()
        ]

    @staticmethod
    def _csv_row(row):
        return [row[0], f"{row[1]:.3f}", *(f"{value:.2f}" for value in row[2:])]

    def flush_to_file(self):
        """Encola un lote al escritor; nunca escribe en el hilo de la interfaz."""
        if not self.file_buffer:
            return
        batch, self.file_buffer = self.file_buffer, []
        self.write_requested.emit(batch)

    def flush_table(self):
        if not self.table_buffer:
            return
        rows, self.table_buffer = self.table_buffer, []
        table = self.ui.tableWidget
        table.setUpdatesEnabled(False)
        try:
            for row_data in rows:
                row = table.rowCount()
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(str(row_data[0])))
                table.setItem(row, 1, QTableWidgetItem(f"{row_data[1]:.3f}"))
                for column, value in enumerate(row_data[2:], start=2):
                    table.setItem(row, column, QTableWidgetItem(f"{value:.2f}"))
            excess = table.rowCount() - self.MAX_DISPLAY_ROWS
            for _ in range(max(0, excess)):
                table.removeRow(0)
        finally:
            table.setUpdatesEnabled(True)
        table.scrollToBottom()

    def start_recording(self, filename=None):
        if self.is_recording:
            return False
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename or f"data_{timestamp}.csv"
        os.makedirs("data", exist_ok=True)
        self.session_filepath = os.path.join("data", filename)
        if not self._writer_thread.isRunning():
            self._writer_thread.start()
        self.clear_buffer()
        self.total_samples = 0
        self.acquisition_started_at = datetime.now()
        self.is_recording = True
        self.open_requested.emit(self.session_filepath)
        print(f"Grabación iniciada: {self.session_filepath}")
        return True

    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False
        self.flush_to_file()
        self.flush_table()
        self.close_requested.emit()
        # Al detener se espera el cierre del lote final, no durante la adquisición.
        self._writer_thread.wait(2000)
        print(f"Grabación detenida. Total de muestras: {self.total_samples}")

    def shutdown(self):
        self.stop_recording()
        if self._writer_thread.isRunning():
            self.close_requested.emit()
            self._writer_thread.wait(2000)

    def clear_buffer(self):
        self.data_buffer.clear()
        self.file_buffer.clear()
        self.table_buffer.clear()
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
                writer.writerow(["N°", "Timestamp", "T1", "T2", "T3", "T4"])
                writer.writerows(self._csv_row(row) for row in self.data_buffer)
            QMessageBox.information(None, "Exportación exitosa", f"Datos exportados a: {filepath}")
        except OSError as error:
            QMessageBox.critical(None, "Error", f"Error exportando datos: {error}")

    @Slot(str)
    def _show_writer_error(self, message):
        print(message)

"""Bounded sample storage, asynchronous session persistence and CSV export."""

import csv
import os
import queue
import shutil
import threading
import time
from collections import deque
from datetime import datetime

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem


class _CsvWriter:
    """Owns the CSV file in one worker thread so disk latency never holds Qt."""

    HEADER = ["N°", "Timestamp", "T1", "T2", "T3", "T4"]

    def __init__(self):
        self._queue = queue.Queue()
        self.last_error = None
        self._thread = threading.Thread(target=self._run, name="csv-writer", daemon=True)
        self._thread.start()

    def command(self, name, *args, wait=False):
        if name == "start":
            self.last_error = None
        done = threading.Event() if wait else None
        self._queue.put((name, args, done))
        if done:
            done.wait(10)
        return done

    def _run(self):
        handle = writer = None
        while True:
            name, args, done = self._queue.get()
            try:
                if name == "start":
                    if handle:
                        handle.close()
                    handle = open(args[0], "w", newline="", encoding="utf-8")
                    writer = csv.writer(handle)
                    writer.writerow(self.HEADER)
                    handle.flush()
                elif name == "rows" and writer:
                    writer.writerows(args[0])
                elif name in ("flush", "close") and handle:
                    handle.flush()
                    os.fsync(handle.fileno())
                    if name == "close":
                        handle.close()
                        handle = writer = None
                elif name == "quit":
                    if handle:
                        handle.flush()
                        handle.close()
                    return
            except OSError as error:
                self.last_error = error
            finally:
                if done:
                    done.set()

    def shutdown(self):
        self.command("quit", wait=True)
        self._thread.join(timeout=2)


class DataManager:
    """Keeps only the latest 100k samples in memory; the session CSV is canonical."""

    MEMORY_BUFFER_SIZE = 100_000
    FILE_BUFFER_SIZE = 1_000
    FILE_FLUSH_SECONDS = 5.0
    MAX_DISPLAY_ROWS = 1_000

    def __init__(self, ui):
        self.ui = ui
        self.data_buffer = deque(maxlen=self.MEMORY_BUFFER_SIZE)
        self.file_buffer = []
        self.is_recording = False
        self.master_file = None
        self.total_samples = 0
        self.on_data_added = None
        self.acquisition_started_at = None
        self._last_file_submit = time.monotonic()
        self._writer = _CsvWriter()
        self._ui_batch = []
        self._table_timer = QTimer()
        self._table_timer.setInterval(50)
        self._table_timer.timeout.connect(self._flush_ui_batch)
        self._table_timer.start()
        self._save_timer = QTimer()
        self._save_timer.setInterval(500)
        self._save_timer.timeout.connect(self.flush_to_file)
        self._save_timer.start()

    @staticmethod
    def parse_data(data_string):
        try:
            values = [float(value.strip()) for value in data_string.strip().split(",")]
        except (AttributeError, ValueError):
            return None
        return values if len(values) == 4 else None

    def process_data(self, raw_data):
        if not self.is_recording:
            return False
        values = self.parse_data(raw_data)
        if values is None:
            return False
        elapsed = time.monotonic() - self.acquisition_started_at
        self.add_to_buffer([datetime.now(), elapsed, *values])
        return True

    def get_selected_channels(self):
        return [i for i, box in enumerate((self.ui.checkBox_1, self.ui.checkBox_2, self.ui.checkBox_3, self.ui.checkBox_4)) if box.isChecked()]

    def add_to_buffer(self, row_data):
        self.data_buffer.append(row_data)
        self.total_samples += 1
        self.file_buffer.append(self._csv_row(self.total_samples, row_data))
        self._ui_batch.append((self.total_samples, row_data))
        if len(self.file_buffer) >= self.FILE_BUFFER_SIZE:
            self.flush_to_file(force=True)

    @staticmethod
    def _csv_row(number, row):
        return [number, f"{row[1]:.3f}", *(f"{value:.2f}" for value in row[2:])]

    def flush_to_file(self, force=False):
        if not self.file_buffer:
            return
        if force or time.monotonic() - self._last_file_submit >= self.FILE_FLUSH_SECONDS:
            batch, self.file_buffer = self.file_buffer, []
            self._writer.command("rows", batch)
            self._last_file_submit = time.monotonic()

    def _flush_ui_batch(self):
        if not self._ui_batch:
            return
        batch, self._ui_batch = self._ui_batch, []
        table = self.ui.tableWidget
        scrollbar = table.verticalScrollBar()
        at_bottom = scrollbar.value() >= scrollbar.maximum() - 2
        table.setUpdatesEnabled(False)
        for number, row in batch:
            index = table.rowCount()
            table.insertRow(index)
            for column, value in enumerate((number, f"{row[1]:.3f}", *(f"{v:.2f}" for v in row[2:]))):
                table.setItem(index, column, QTableWidgetItem(str(value)))
        while table.rowCount() > self.MAX_DISPLAY_ROWS:
            table.removeRow(0)
        table.setUpdatesEnabled(True)
        if at_bottom:
            table.scrollToBottom()
        if self.on_data_added:
            self.on_data_added()

    def start_recording(self, filename=None):
        if self.is_recording:
            return False
        os.makedirs("data", exist_ok=True)
        filename = filename or f"data_{datetime.now():%Y%m%d_%H%M%S}.csv"
        self.master_file = os.path.join("data", filename)
        try:
            self._writer.command("start", self.master_file, wait=True)
            if self._writer.last_error:
                raise self._writer.last_error
        except OSError as error:
            QMessageBox.critical(None, "Error", f"No se pudo crear el archivo: {error}")
            return False
        self.clear_buffer()
        self.total_samples = 0
        self.acquisition_started_at = time.monotonic()
        self._last_file_submit = time.monotonic()
        self.is_recording = True
        return True

    def stop_recording(self):
        if not self.is_recording:
            return
        self.flush_to_file(force=True)
        self._writer.command("close", wait=True)
        self.is_recording = False
        self._flush_ui_batch()

    def clear_buffer(self):
        self.data_buffer.clear()
        self.file_buffer.clear()
        self._ui_batch.clear()
        self.ui.tableWidget.setRowCount(0)

    def export_all_data(self, filename=None):
        if not self.master_file and not self.data_buffer:
            QMessageBox.warning(None, "Sin datos", "No hay datos para exportar")
            return
        self.flush_to_file(force=True)
        self._writer.command("flush", wait=True)
        os.makedirs("exports", exist_ok=True)
        filepath = os.path.join("exports", filename or f"export_{datetime.now():%Y%m%d_%H%M%S}.csv")
        try:
            if self.master_file and os.path.exists(self.master_file):
                shutil.copyfile(self.master_file, filepath)
            else:
                with open(filepath, "w", newline="", encoding="utf-8") as output:
                    csv.writer(output).writerows([_CsvWriter.HEADER] + [self._csv_row(i + 1, row) for i, row in enumerate(self.data_buffer)])
            QMessageBox.information(None, "Exportación exitosa", f"Datos exportados a: {filepath}")
        except OSError as error:
            QMessageBox.critical(None, "Error", f"Error exportando datos: {error}")

    def shutdown(self):
        self.stop_recording()
        self._table_timer.stop()
        self._save_timer.stop()
        self._writer.shutdown()

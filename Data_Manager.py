import csv
import os
from datetime import datetime
from collections import deque
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QTableWidgetItem, QHeaderView, QMessageBox

class DataManager:
    def __init__(self, ui):
        self.ui = ui
        self.buffer_size = 10000  # Tamaño del buffer en memoria
        self.data_buffer = deque(maxlen=self.buffer_size)  # Buffer circular automático
        self.file_buffer = []  # Buffer para escritura en archivo
        self.file_buffer_size = 1000  # Escribir al archivo cada 1000 datos
        self.is_recording = False
        self.current_file = None
        self.csv_writer = None
        self.header_written = False
        self.max_buffer_warning = 50000  # Alerta si buffer supera esto
        
        # Timer para escritura periódica al archivo
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.flush_to_file)
        self.save_timer.start(5000)  # Cada 5 segundos
    
    def parse_data(self, data_string):
        """Parsea los datos del puerto COM"""
        try:
            # Eliminar espacios y separar por comas
            values = data_string.strip().split(',')
            values = [float(v.strip()) for v in values if v.strip()]
            
            # Verificar que sean exactamente 4 valores
            if len(values) != 4:
                return None
            
            return values
        except (ValueError, IndexError):
            return None
    
    def process_data(self, raw_data):
        """Procesa los datos recibidos del puerto COM"""
        values = self.parse_data(raw_data)
        if values is None:
            return
        
        # Verificar checkboxes seleccionados
        selected_channels = self.get_selected_channels()
        if not selected_channels:
            return  # No hay canales seleccionados
        
        # Obtener timestamp
        timestamp = datetime.now()
        
        # Construir fila de datos según canales seleccionados
        row_data = [timestamp]
        for channel in selected_channels:
            row_data.append(values[channel])
        
        # Agregar al buffer
        self.add_to_buffer(row_data)
    
    def get_selected_channels(self):
        """Retorna lista de índices de canales seleccionados (0-3)"""
        channels = []
        if self.ui.checkBox_1.isChecked():
            channels.append(0)
        if self.ui.checkBox_2.isChecked():
            channels.append(1)
        if self.ui.checkBox_3.isChecked():
            channels.append(2)
        if self.ui.checkBox_4.isChecked():
            channels.append(3)
        return channels
    
    def add_to_buffer(self, row_data):
        """Agrega datos al buffer y actualiza la tabla"""
        # Agregar al buffer principal
        self.data_buffer.append(row_data)
        
        # Agregar al buffer de archivo
        self.file_buffer.append(row_data)
        
        # Si el buffer de archivo está lleno, escribir al disco
        if len(self.file_buffer) >= self.file_buffer_size:
            self.flush_to_file()
        
        # Actualizar tabla UI (solo mostrar últimos 1000)
        self.update_table(row_data)
        
        # Verificar tamaño del buffer
        if len(self.data_buffer) > self.max_buffer_warning:
            print(f"⚠️ Buffer grande: {len(self.data_buffer)} datos")
    
    def update_table(self, row_data):
        """Actualiza la tabla con el nuevo dato"""
        # Obtener columnas seleccionadas
        selected = self.get_selected_channels()
        if not selected:
            return
        
        row = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row)
        
        # Columna 0: Número de fila
        self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        
        # Columna 1: Timestamp
        timestamp_str = row_data[0].strftime("%H:%M:%S.%f")[:-3]
        self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(timestamp_str))
        
        # Columnas siguientes: datos de cada canal seleccionado
        col_idx = 2
        for i, value in enumerate(row_data[1:]):  # row_data[1:] son los valores
            self.ui.tableWidget.setItem(row, col_idx, QTableWidgetItem(f"{value:.2f}"))
            col_idx += 1
        
        # Limitar filas mostradas en tabla (para rendimiento)
        max_display_rows = 1000
        if self.ui.tableWidget.rowCount() > max_display_rows:
            self.ui.tableWidget.removeRow(0)
            # Actualizar números de fila
            for i in range(self.ui.tableWidget.rowCount()):
                self.ui.tableWidget.setItem(i, 0, QTableWidgetItem(str(i + 1)))
        
        # Scroll automático al final
        self.ui.tableWidget.scrollToBottom()
    
    def flush_to_file(self):
        """Escribe el buffer de archivo al disco"""
        if not self.file_buffer or not self.is_recording:
            return
        
        try:
            for row in self.file_buffer:
                # Formato: timestamp, valor1, valor2, ...
                row_str = [row[0].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]]
                row_str.extend([f"{v:.2f}" for v in row[1:]])
                self.csv_writer.writerow(row_str)
            
            self.current_file.flush()  # Forzar escritura física
            self.file_buffer.clear()
            
        except Exception as e:
            print(f"Error escribiendo archivo: {e}")
    
    def start_recording(self, filename=None):
        """Inicia la grabación de datos"""
        if self.is_recording:
            return
        
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data_{timestamp}.csv"
            
            # Crear directorio si no existe
            os.makedirs("data", exist_ok=True)
            filepath = os.path.join("data", filename)
            
            self.current_file = open(filepath, 'w', newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.current_file)
            
            # Escribir header
            selected = self.get_selected_channels()
            if selected:
                header = ['Timestamp']
                for ch in selected:
                    header.append(f'T_{ch+1}')
                self.csv_writer.writerow(header)
            
            self.is_recording = True
            print(f"✅ Grabación iniciada: {filepath}")
            
        except Exception as e:
            print(f"❌ Error iniciando grabación: {e}")
    
    def stop_recording(self):
        """Detiene la grabación y guarda los datos pendientes"""
        if not self.is_recording:
            return
        
        # Guardar datos pendientes
        self.flush_to_file()
        
        if self.current_file:
            self.current_file.close()
            self.current_file = None
        
        self.is_recording = False
        print(f"✅ Grabación detenida. Total datos: {len(self.data_buffer)}")
    
    def clear_buffer(self):
        """Limpia el buffer de datos"""
        self.data_buffer.clear()
        self.file_buffer.clear()
        self.ui.tableWidget.setRowCount(0)
        print("✅ Buffer limpiado")
    
    def export_all_data(self, filename=None):
        """Exporta todos los datos del buffer a un archivo"""
        if len(self.data_buffer) == 0:
            QMessageBox.warning(None, "Sin datos", "No hay datos para exportar")
            return
        
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"export_{timestamp}.csv"
            
            os.makedirs("exports", exist_ok=True)
            filepath = os.path.join("exports", filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Escribir header
                selected = self.get_selected_channels()
                if selected:
                    header = ['Timestamp']
                    for ch in selected:
                        header.append(f'T_{ch+1}')
                    writer.writerow(header)
                
                # Escribir datos
                for row in self.data_buffer:
                    row_str = [row[0].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]]
                    row_str.extend([f"{v:.2f}" for v in row[1:]])
                    writer.writerow(row_str)
            
            QMessageBox.information(None, "Exportación exitosa", 
                                   f"Datos exportados a: {filepath}\nTotal registros: {len(self.data_buffer)}")
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error exportando datos: {e}")
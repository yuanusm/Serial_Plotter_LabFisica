"""Gráfica cartesiana ligera, sin dependencias externas, para las muestras COM."""

from PySide6.QtCore import QPointF, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class PlotWidget(QWidget):
    """Dibuja los sensores seleccionados contra el número de muestra (eje X)."""

    COLORS = (QColor("#d32f2f"), QColor("#1976d2"), QColor("#388e3c"), QColor("#7b1fa2"))
    MAX_POINTS = 1_000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = []
        self.channels = []
        self.total_samples = 0
        self.x_min = self.x_max = self.y_min = self.y_max = 0
        self._refresh_pending = False
        self.setMinimumSize(200, 0)

    def set_limits(self, x_min, x_max, y_min, y_max):
        self.x_min, self.x_max = x_min, x_max
        self.y_min, self.y_max = y_min, y_max
        self.request_refresh()

    def set_data(self, rows, channels, total_samples):
        self.rows = list(rows)[-self.MAX_POINTS :]
        self.channels = list(channels)
        self.total_samples = total_samples
        self.request_refresh()

    def request_refresh(self):
        """Agrupa actualizaciones de muestras rápidas para no bloquear la GUI."""
        if not self._refresh_pending:
            self._refresh_pending = True
            QTimer.singleShot(80, self._refresh)

    def _refresh(self):
        self._refresh_pending = False
        self.update()

    def paintEvent(self, event):
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("white"))
        plot = self.rect().adjusted(42, 12, -12, -28)
        painter.setPen(QPen(QColor("#444444")))
        painter.drawRect(plot)

        if self.x_min >= self.x_max or self.y_min >= self.y_max:
            painter.drawText(self.rect(), 0x84, "Defina límites mínimo y máximo para X e Y")
            painter.end()
            return
        if not self.rows or not self.channels:
            painter.drawText(self.rect(), 0x84, "Esperando datos del puerto COM")
            painter.end()
            return

        painter.drawText(4, plot.top() + 10, str(self.y_max))
        painter.drawText(4, plot.bottom(), str(self.y_min))
        painter.drawText(plot.left(), self.height() - 8, str(self.x_min))
        painter.drawText(plot.right() - 24, self.height() - 8, str(self.x_max))

        first_sample = self.total_samples - len(self.rows) + 1
        for channel in self.channels:
            painter.setPen(QPen(self.COLORS[channel], 1.5))
            previous = None
            for offset, row in enumerate(self.rows):
                sample_number = first_sample + offset
                value = row[channel + 1]
                if not (self.x_min <= sample_number <= self.x_max and self.y_min <= value <= self.y_max):
                    previous = None
                    continue
                x = plot.left() + (sample_number - self.x_min) * plot.width() / (self.x_max - self.x_min)
                y = plot.bottom() - (value - self.y_min) * plot.height() / (self.y_max - self.y_min)
                if previous is not None:
                    painter.drawLine(previous, QPointF(x, y))
                previous = QPointF(x, y)
        painter.end()

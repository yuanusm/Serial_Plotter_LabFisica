"""Gráfica interactiva y acotada para las muestras recibidas por el puerto COM."""

from collections import deque

from PySide6.QtCore import QPointF, QTimer, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QMenu, QWidget


class PlotWidget(QWidget):
    """Representa T1--T4 con zoom, pan y dos cursores ajustados a muestras."""

    COLORS = (QColor("#d32f2f"), QColor("#1976d2"), QColor("#388e3c"), QColor("#7b1fa2"))
    MAX_STORED_POINTS = 100_000
    MAX_RENDERED_POINTS = 6_000
    MAX_POINTS_PER_TRACE = 1_500
    GRID_DIVISIONS = 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = deque(maxlen=self.MAX_STORED_POINTS)
        self.channels = []
        self.x_min = self.x_max = self.y_min = self.y_max = 0
        self.view_x_min = self.view_x_max = self.view_y_min = self.view_y_max = 0
        self.cursor_times = [None, None]
        self._drag_cursor = None
        self._pan_origin = None
        self._refresh_pending = False
        self.setMinimumSize(200, 0)
        self.setMouseTracking(True)

    def set_limits(self, x_min, x_max, y_min, y_max):
        self.x_min, self.x_max, self.y_min, self.y_max = x_min, x_max, y_min, y_max
        self.reset_view()

    def set_channels(self, channels):
        self.channels = list(channels)
        self.request_refresh()

    def clear_data(self):
        self.rows.clear()
        self.cursor_times = [None, None]
        self.request_refresh()

    def append_sample(self, row):
        self.rows.append(row)
        self.request_refresh()

    def reset_view(self):
        self.view_x_min, self.view_x_max = self.x_min, self.x_max
        self.view_y_min, self.view_y_max = self.y_min, self.y_max
        self.request_refresh()

    def request_refresh(self):
        if not self._refresh_pending:
            self._refresh_pending = True
            QTimer.singleShot(80, self._refresh)

    def _refresh(self):
        self._refresh_pending = False
        self.update()

    def _plot_rect(self):
        return self.rect().adjusted(55, 20, -18, -42)

    @staticmethod
    def _decimate(rows, maximum):
        """Conserva extremos de cubetas; limita coste de pintura sin copiar histórico."""
        if len(rows) <= maximum:
            return rows
        step = len(rows) / maximum
        return [rows[min(int(index * step), len(rows) - 1)] for index in range(maximum)]

    def _visible_rows(self):
        visible = [row for row in self.rows if self.view_x_min <= row[1] <= self.view_x_max]
        return self._decimate(visible, min(self.MAX_RENDERED_POINTS, self.MAX_POINTS_PER_TRACE))

    def _to_x(self, time, plot):
        return plot.left() + (time - self.view_x_min) * plot.width() / (self.view_x_max - self.view_x_min)

    def _to_y(self, value, plot):
        return plot.bottom() - (value - self.view_y_min) * plot.height() / (self.view_y_max - self.view_y_min)

    def _from_x(self, x, plot):
        return self.view_x_min + (x - plot.left()) * (self.view_x_max - self.view_x_min) / plot.width()

    def _snap_time(self, time):
        if not self.rows:
            return time
        return min(self.rows, key=lambda row: abs(row[1] - time))[1]

    def _cursor_values(self, time):
        if time is None or not self.rows:
            return None
        row = min(self.rows, key=lambda candidate: abs(candidate[1] - time))
        channel = self.channels[0] if self.channels else 0
        return row[1], row[channel + 2]

    def paintEvent(self, event):
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("white"))
        plot = self._plot_rect()
        if plot.width() <= 0 or plot.height() <= 0:
            painter.end()
            return
        painter.setPen(QPen(QColor("#444")))
        painter.drawRect(plot)
        if self.view_x_min >= self.view_x_max or self.view_y_min >= self.view_y_max:
            painter.drawText(self.rect(), Qt.AlignCenter, "Defina límites mínimo y máximo para X e Y")
            painter.end()
            return

        self._draw_grid(painter, plot)
        if not self.rows or not self.channels:
            painter.drawText(plot, Qt.AlignCenter, "Esperando datos del puerto COM")
            painter.end()
            return
        self._draw_legend(painter, plot)
        rows = self._visible_rows()
        for channel in self.channels:
            painter.setPen(QPen(self.COLORS[channel], 1.5))
            previous = None
            for row in rows:
                value = row[channel + 2]
                if not self.view_y_min <= value <= self.view_y_max:
                    previous = None
                    continue
                point = QPointF(self._to_x(row[1], plot), self._to_y(value, plot))
                if previous is not None:
                    painter.drawLine(previous, point)
                previous = point
        self._draw_cursors(painter, plot)
        painter.end()

    def _draw_grid(self, painter, plot):
        painter.setPen(QPen(QColor("#dddddd"), 1))
        for index in range(self.GRID_DIVISIONS + 1):
            ratio = index / self.GRID_DIVISIONS
            x = plot.left() + ratio * plot.width()
            y = plot.bottom() - ratio * plot.height()
            painter.drawLine(QPointF(x, plot.top()), QPointF(x, plot.bottom()))
            painter.drawLine(QPointF(plot.left(), y), QPointF(plot.right(), y))
            painter.setPen(QPen(QColor("#333")))
            painter.drawText(int(x) - 17, plot.bottom() + 17, f"{self.view_x_min + ratio * (self.view_x_max - self.view_x_min):.1f}")
            painter.drawText(4, int(y) + 4, f"{self.view_y_min + ratio * (self.view_y_max - self.view_y_min):.1f}")
            painter.setPen(QPen(QColor("#dddddd"), 1))

    def _draw_legend(self, painter, plot):
        legend_x = plot.left() + 5
        for channel in self.channels:
            painter.setPen(QPen(self.COLORS[channel], 2))
            painter.drawLine(legend_x, plot.top() + 12, legend_x + 15, plot.top() + 12)
            painter.drawText(legend_x + 18, plot.top() + 16, f"T{channel + 1}")
            legend_x += 43

    def _draw_cursors(self, painter, plot):
        values = []
        for index, time in enumerate(self.cursor_times):
            if time is None or not self.view_x_min <= time <= self.view_x_max:
                values.append(None)
                continue
            color = QColor("#ff9800") if index == 0 else QColor("#009688")
            x = self._to_x(time, plot)
            painter.setPen(QPen(color, 2, Qt.DashLine))
            painter.drawLine(QPointF(x, plot.top()), QPointF(x, plot.bottom()))
            sample = self._cursor_values(time)
            values.append(sample)
            if sample:
                painter.setPen(QPen(color))
                painter.drawText(int(x) + 3, plot.top() + 32 + index * 16, f"C{index + 1}: {sample[0]:.3f}s, {sample[1]:.2f}")
        if values[0] and values[1]:
            dx = abs(values[1][0] - values[0][0])
            dy = values[1][1] - values[0][1]
            painter.setPen(QPen(QColor("#111")))
            painter.drawText(plot.left() + 5, plot.bottom() - 6, f"ΔX: {dx:.3f}s   ΔY: {dy:.2f}")

    def wheelEvent(self, event):
        plot = self._plot_rect()
        if not plot.contains(event.position().toPoint()):
            event.ignore()
            return
        factor = 0.8 if event.angleDelta().y() > 0 else 1.25
        mouse_x = self._from_x(event.position().x(), plot)
        mouse_y = self.view_y_max - (event.position().y() - plot.top()) * (self.view_y_max - self.view_y_min) / plot.height()
        self.view_x_min = mouse_x - (mouse_x - self.view_x_min) * factor
        self.view_x_max = mouse_x + (self.view_x_max - mouse_x) * factor
        self.view_y_min = mouse_y - (mouse_y - self.view_y_min) * factor
        self.view_y_max = mouse_y + (self.view_y_max - mouse_y) * factor
        self.request_refresh()
        event.accept()

    def mousePressEvent(self, event):
        plot = self._plot_rect()
        if event.button() == Qt.RightButton:
            self._context_menu(event.globalPosition().toPoint())
            return
        if not plot.contains(event.position().toPoint()):
            return
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier):
            self._pan_origin = event.position()
        elif event.button() == Qt.LeftButton:
            for index, time in enumerate(self.cursor_times):
                if time is not None and abs(self._to_x(time, plot) - event.position().x()) < 8:
                    self._drag_cursor = index
                    return
            available = 0 if self.cursor_times[0] is None else 1
            self.cursor_times[available] = self._snap_time(self._from_x(event.position().x(), plot))
            self._drag_cursor = available
            self.request_refresh()

    def mouseMoveEvent(self, event):
        plot = self._plot_rect()
        if self._drag_cursor is not None:
            self.cursor_times[self._drag_cursor] = self._snap_time(self._from_x(event.position().x(), plot))
            self.request_refresh()
        elif self._pan_origin is not None:
            dx = (event.position().x() - self._pan_origin.x()) * (self.view_x_max - self.view_x_min) / plot.width()
            dy = (event.position().y() - self._pan_origin.y()) * (self.view_y_max - self.view_y_min) / plot.height()
            self.view_x_min -= dx; self.view_x_max -= dx
            self.view_y_min += dy; self.view_y_max += dy
            self._pan_origin = event.position()
            self.request_refresh()

    def mouseReleaseEvent(self, event):
        self._drag_cursor = self._pan_origin = None
        event.accept()

    def _context_menu(self, position):
        menu = QMenu(self)
        reset = menu.addAction("Restablecer zoom")
        clear = menu.addAction("Ocultar cursores")
        action = menu.exec(position)
        if action is reset:
            self.reset_view()
        elif action is clear:
            self.cursor_times = [None, None]
            self.request_refresh()

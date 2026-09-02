"""Fast QPainter plot with cursor measurement, pan and mouse-centred zoom."""

import bisect
import math

from PySide6.QtCore import QPoint, QPointF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QMenu, QToolTip, QWidget


class PlotWidget(QWidget):
    viewLimitsChanged = Signal(float, float, float, float)

    DEFAULT_COLORS = ("#d32f2f", "#1976d2", "#388e3c", "#7b1fa2")
    DECIMATION_LIMITS = {"high": 100_000, "medium": 6_000, "low": 1_500}
    CURSOR_HIT_TOLERANCE = 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self._source_rows = ()
        self.rows, self._timestamps = [], []
        self.render_rows, self.channels = [], []
        self.x_min, self.x_max, self.y_min, self.y_max = 0., 300., -127., 100.
        self.colors = [QColor(color) for color in self.DEFAULT_COLORS]
        self.cursor_colors = [QColor("#00bcd4"), QColor("#e91e63")]
        self.background = QColor("white")
        self.line_width, self.decimation = 2, "medium"
        self.cursors = [None, None]  # indices into original, non-decimated rows
        self._refresh_pending = False
        self._drag_cursor = None
        self._pan_start = None
        self._pan_limits = None
        self.setMinimumSize(200, 0)
        self.setMouseTracking(True)

    def set_style(self, colors=None, cursor_colors=None, background=None, line_width=None, decimation=None):
        if colors: self.colors = [QColor(color) for color in colors]
        if cursor_colors: self.cursor_colors = [QColor(color) for color in cursor_colors]
        if background: self.background = QColor(background)
        if line_width: self.line_width = int(line_width)
        if decimation: self.decimation = decimation
        self.request_refresh()

    def set_limits(self, x_min, x_max, y_min, y_max):
        self.x_min, self.x_max = float(x_min), float(x_max)
        self.y_min, self.y_max = float(y_min), float(y_max)
        self.request_refresh()

    def set_data(self, rows, channels, total_samples=None):
        del total_samples
        self._source_rows = rows
        self.channels = list(channels)
        self.request_refresh()

    def request_refresh(self):
        if not self._refresh_pending:
            self._refresh_pending = True
            QTimer.singleShot(50, self._refresh)

    def _refresh(self):
        self._refresh_pending = False
        self.rows = list(self._source_rows)
        self._timestamps = [row[1] for row in self.rows]
        self._prepare_render_rows()
        self.update()

    def _prepare_render_rows(self):
        rows = self.rows
        limit = self.DECIMATION_LIMITS[self.decimation]
        if len(rows) <= limit:
            self.render_rows = rows
            return
        # Keep extrema of every bucket rather than arbitrary periodic points.
        # Each channel can contribute a min and max.  Size the buckets so the
        # union stays within the selected sample budget even with four traces.
        bucket_count = max(1, limit // max(2, 2 * len(self.channels or range(4))))
        width = len(rows) / bucket_count
        picked = {0, len(rows) - 1}
        for bucket in range(bucket_count):
            start, end = int(bucket * width), min(len(rows), int((bucket + 1) * width))
            if start >= end: continue
            for channel in (self.channels or range(4)):
                values = range(start, end)
                picked.add(min(values, key=lambda i: rows[i][channel + 2]))
                picked.add(max(range(start, end), key=lambda i: rows[i][channel + 2]))
        self.render_rows = [rows[i] for i in sorted(picked)]

    def _plot_rect(self):
        return self.rect().adjusted(52, 14, -14, -34)

    def _to_pixel(self, x, y, plot=None):
        plot = plot or self._plot_rect()
        return QPointF(plot.left() + (x - self.x_min) * plot.width() / (self.x_max - self.x_min), plot.bottom() - (y - self.y_min) * plot.height() / (self.y_max - self.y_min))

    def _from_pixel(self, point, plot=None):
        plot = plot or self._plot_rect()
        return (self.x_min + (point.x() - plot.left()) * (self.x_max - self.x_min) / plot.width(), self.y_max - (point.y() - plot.top()) * (self.y_max - self.y_min) / plot.height())

    @staticmethod
    def _tick_step(span):
        raw = max(span / 6, 1e-9)
        power = 10 ** math.floor(math.log10(raw))
        return min((1, 2, 5, 10), key=lambda factor: abs(raw - factor * power)) * power

    def _nearest_index(self, x):
        if not self._timestamps: return None
        index = bisect.bisect_left(self._timestamps, x)
        if index == 0: return 0
        if index == len(self._timestamps): return index - 1
        return index if self._timestamps[index] - x < x - self._timestamps[index - 1] else index - 1

    def _set_cursor_at(self, cursor, x):
        index = self._nearest_index(x)
        if index is not None:
            self.cursors[cursor] = index
            self.update()

    def _cursor_lines(self):
        return [(number, index, self.rows[index]) for number, index in enumerate(self.cursors) if index is not None and index < len(self.rows)]

    def paintEvent(self, event):
        del event
        painter, plot = QPainter(self), self._plot_rect()
        painter.fillRect(self.rect(), self.background)
        if plot.width() <= 0 or plot.height() <= 0 or self.x_min >= self.x_max or self.y_min >= self.y_max:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Defina límites mínimo y máximo para X e Y")
            painter.end(); return
        painter.setPen(QPen(QColor("#444")))
        painter.drawRect(plot)
        self._draw_grid(painter, plot)
        if not self.rows:
            painter.drawText(plot, Qt.AlignmentFlag.AlignCenter, "Esperando datos del puerto COM")
            painter.end(); return
        self._draw_legend(painter, plot)
        for channel in self.channels:
            painter.setPen(QPen(self.colors[channel], self.line_width))
            previous = None
            for row in self.render_rows:
                x, y = row[1], row[channel + 2]
                if not (self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max):
                    previous = None; continue
                point = self._to_pixel(x, y, plot)
                if previous: painter.drawLine(previous, point)
                previous = point
        self._draw_cursors(painter, plot)
        painter.end()

    def _draw_grid(self, painter, plot):
        painter.setPen(QPen(QColor("#888888"), 1, Qt.PenStyle.DashLine))
        for axis, lower, upper in (("x", self.x_min, self.x_max), ("y", self.y_min, self.y_max)):
            step = self._tick_step(upper - lower)
            value = math.ceil(lower / step) * step
            while value <= upper + step * .01:
                if axis == "x":
                    x = self._to_pixel(value, self.y_min, plot).x(); painter.drawLine(QPointF(x, plot.top()), QPointF(x, plot.bottom())); painter.drawText(int(x) - 18, plot.bottom() + 17, f"{value:g}")
                else:
                    y = self._to_pixel(self.x_min, value, plot).y(); painter.drawLine(QPointF(plot.left(), y), QPointF(plot.right(), y)); painter.drawText(3, int(y) + 4, f"{value:g}")
                value += step

    def _draw_legend(self, painter, plot):
        x = plot.left() + 5
        for channel in self.channels:
            painter.setPen(QPen(self.colors[channel], self.line_width)); painter.drawLine(x, plot.top() + 10, x + 16, plot.top() + 10)
            painter.setPen(QPen(QColor("#222"))); painter.drawText(x + 20, plot.top() + 14, f"T{channel + 1}")
            x += 43

    def _draw_cursors(self, painter, plot):
        lines = self._cursor_lines()
        for number, _, row in lines:
            x = self._to_pixel(row[1], self.y_min, plot).x()
            painter.setPen(QPen(self.cursor_colors[number], 1.5, Qt.PenStyle.DashLine)); painter.drawLine(QPointF(x, plot.top()), QPointF(x, plot.bottom()))
            painter.drawText(int(x) + 3, plot.top() + 28, f"C{number + 1}")
        if lines:
            text = []
            for number, _, row in lines:
                text += [f"CURSOR {number + 1}  X = {row[1]:.3f} s", *(f"T{i + 1} = {row[i + 2]:.2f} °C" for i in range(4))]
            if len(lines) == 2:
                a, b = lines[0][2], lines[1][2]; dx, dy = b[1] - a[1], b[2] - a[2]
                text += [f"ΔX = {dx:.3f} s", f"ΔY (T1) = {dy:.2f} °C", f"Pendiente (T1) = {dy / dx:.3f} °C/s" if dx else "Pendiente (T1) = N/A"]
            painter.setPen(QPen(QColor("#222"))); painter.drawText(plot.adjusted(6, 35, -6, -6), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, "\n".join(text))

    def wheelEvent(self, event):
        plot = self._plot_rect()
        if not plot.contains(event.position().toPoint()): return
        x, y = self._from_pixel(event.position(), plot)
        scale = 0.9 if event.angleDelta().y() > 0 else 1 / .9
        mods = event.modifiers()
        zoom_x, zoom_y = mods != Qt.KeyboardModifier.ShiftModifier, mods != Qt.KeyboardModifier.ControlModifier
        if zoom_x: self.x_min, self.x_max = x + (self.x_min - x) * scale, x + (self.x_max - x) * scale
        if zoom_y: self.y_min, self.y_max = y + (self.y_min - y) * scale, y + (self.y_max - y) * scale
        self.viewLimitsChanged.emit(self.x_min, self.x_max, self.y_min, self.y_max)
        self.update(); event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self._pan_start, self._pan_limits = event.position(), (self.x_min, self.x_max); self.setCursor(Qt.CursorShape.ClosedHandCursor); return
            for number, _, row in self._cursor_lines():
                if abs(self._to_pixel(row[1], self.y_min).x() - event.position().x()) <= self.CURSOR_HIT_TOLERANCE:
                    self._drag_cursor = number; return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_cursor is not None:
            self._set_cursor_at(self._drag_cursor, self._from_pixel(event.position())[0]); return
        if self._pan_start is not None:
            shift = (event.position().x() - self._pan_start.x()) * (self._pan_limits[1] - self._pan_limits[0]) / self._plot_rect().width()
            self.x_min, self.x_max = self._pan_limits[0] - shift, self._pan_limits[1] - shift
            self.viewLimitsChanged.emit(self.x_min, self.x_max, self.y_min, self.y_max); self.update(); return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_cursor = self._pan_start = self._pan_limits = None
        self.unsetCursor(); super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        menu, x = QMenu(self), self._from_pixel(event.pos())[0]
        add1 = menu.addAction("Agregar cursor 1 aquí"); add2 = menu.addAction("Agregar cursor 2 aquí")
        remove1 = menu.addAction("Eliminar cursor 1"); remove1.setEnabled(self.cursors[0] is not None)
        remove2 = menu.addAction("Eliminar cursor 2"); remove2.setEnabled(self.cursors[1] is not None)
        remove_all = menu.addAction("Eliminar todos los cursores"); remove_all.setEnabled(any(c is not None for c in self.cursors))
        measure = menu.addAction("Medir en este punto")
        chosen = menu.exec(event.globalPos())
        if chosen is add1: self._set_cursor_at(0, x)
        elif chosen is add2: self._set_cursor_at(1, x)
        elif chosen is remove1: self.cursors[0] = None; self.update()
        elif chosen is remove2: self.cursors[1] = None; self.update()
        elif chosen is remove_all: self.cursors = [None, None]; self.update()
        elif chosen is measure:
            self._set_cursor_at(0, x)
            if self.cursors[0] is not None:
                row = self.rows[self.cursors[0]]
                QToolTip.showText(event.globalPos(), "X = %.3f s\n%s" % (row[1], "\n".join(f"T{i + 1} = {row[i + 2]:.2f} °C" for i in range(4))), self, self.rect(), 2000)

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QPushButton, QSpinBox


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de gráfica")
        self._colors = list(settings["colors"])
        form = QFormLayout(self)
        self.buttons = []
        for label, color in zip(("Color T1", "Color T2", "Color T3", "Color T4", "Cursor 1", "Cursor 2", "Fondo"), self._colors):
            button = QPushButton()
            button.clicked.connect(lambda _, b=button: self._pick(b))
            self.buttons.append(button); form.addRow(label, button); self._paint_button(button)
        self.width_box = QSpinBox(); self.width_box.setRange(1, 5); self.width_box.setValue(settings["line_width"])
        self.decimation = QComboBox(); self.decimation.addItem("Máxima calidad (100k pts)", "high"); self.decimation.addItem("Medio (6k pts)", "medium"); self.decimation.addItem("Bajo (1.5k pts)", "low")
        self.decimation.setCurrentIndex(self.decimation.findData(settings["decimation"]))
        form.addRow("Grosor de línea", self.width_box); form.addRow("Decimación", self.decimation)
        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        box.clicked.connect(self._button_clicked); form.addRow(box)

    def _paint_button(self, button):
        color = self._colors[self.buttons.index(button)]
        button.setText(color); button.setStyleSheet(f"background:{color};")

    def _pick(self, button):
        index = self.buttons.index(button); color = QColorDialog.getColor(QColor(self._colors[index]), self)
        if color.isValid(): self._colors[index] = color.name(); self._paint_button(button)

    def values(self):
        return {"colors": self._colors[:4], "cursor_colors": self._colors[4:6], "background": self._colors[6], "line_width": self.width_box.value(), "decimation": self.decimation.currentData()}

    def _button_clicked(self, button):
        role = button.parent().buttonRole(button)
        if role in (QDialogButtonBox.ButtonRole.ApplyRole, QDialogButtonBox.ButtonRole.AcceptRole):
            self.apply_settings(self.values())
        if role == QDialogButtonBox.ButtonRole.AcceptRole: self.accept()
        elif role == QDialogButtonBox.ButtonRole.RejectRole: self.reject()

    def apply_settings(self, values):
        pass

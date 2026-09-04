# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QCheckBox, QComboBox,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QLayout, QMainWindow, QPushButton,
    QSizePolicy, QSpinBox, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(663, 442)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
        MainWindow.setWindowIcon(icon)
        MainWindow.setAnimated(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QSize(600, 75))
        self.groupBox.setMaximumSize(QSize(16777215, 75))
        self.gridLayout_3 = QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(-1, 5, -1, -1)
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(45, 20))
        self.label.setMaximumSize(QSize(45, 16777215))
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)

        self.pushButton_Conectar = QPushButton(self.groupBox)
        self.pushButton_Conectar.setObjectName(u"pushButton_Conectar")
        self.pushButton_Conectar.setMinimumSize(QSize(65, 20))

        self.gridLayout_3.addWidget(self.pushButton_Conectar, 0, 5, 1, 1)

        self.pushButton_Iniciar = QPushButton(self.groupBox)
        self.pushButton_Iniciar.setObjectName(u"pushButton_Iniciar")
        self.pushButton_Iniciar.setMinimumSize(QSize(50, 20))

        self.gridLayout_3.addWidget(self.pushButton_Iniciar, 0, 6, 1, 1)

        self.ConfirmacionConectado = QLabel(self.groupBox)
        self.ConfirmacionConectado.setObjectName(u"ConfirmacionConectado")
        self.ConfirmacionConectado.setMinimumSize(QSize(80, 0))
        self.ConfirmacionConectado.setMaximumSize(QSize(200, 16777215))

        self.gridLayout_3.addWidget(self.ConfirmacionConectado, 3, 0, 1, 1)

        self.pushButton_Detener = QPushButton(self.groupBox)
        self.pushButton_Detener.setObjectName(u"pushButton_Detener")
        self.pushButton_Detener.setMinimumSize(QSize(60, 20))

        self.gridLayout_3.addWidget(self.pushButton_Detener, 0, 8, 1, 1)

        self.comboBox_Baud = QComboBox(self.groupBox)
        self.comboBox_Baud.setObjectName(u"comboBox_Baud")
        self.comboBox_Baud.setMinimumSize(QSize(80, 20))

        self.gridLayout_3.addWidget(self.comboBox_Baud, 0, 4, 1, 1)

        self.comboBox_COM = QComboBox(self.groupBox)
        self.comboBox_COM.setObjectName(u"comboBox_COM")
        self.comboBox_COM.setMinimumSize(QSize(75, 20))
        font = QFont()
        font.setPointSize(9)
        self.comboBox_COM.setFont(font)
        self.comboBox_COM.setMaxCount(100)
        self.comboBox_COM.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self.comboBox_COM.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.comboBox_COM.setModelColumn(0)
        self.comboBox_COM.setLabelDrawingMode(QComboBox.LabelDrawingMode.UseStyle)

        self.gridLayout_3.addWidget(self.comboBox_COM, 0, 1, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(40, 20))
        self.label_2.setMaximumSize(QSize(40, 16777215))
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_3.addWidget(self.label_2, 0, 3, 1, 1)

        self.pushButton_Actualizar = QPushButton(self.groupBox)
        self.pushButton_Actualizar.setObjectName(u"pushButton_Actualizar")
        self.pushButton_Actualizar.setMinimumSize(QSize(70, 20))

        self.gridLayout_3.addWidget(self.pushButton_Actualizar, 0, 2, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy1)
        self.groupBox_2.setMinimumSize(QSize(600, 200))
        self.groupBox_2.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.groupBox_2.setAutoFillBackground(False)
        self.groupBox_2.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.groupBox_2.setFlat(False)
        self.groupBox_2.setCheckable(False)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 1, 5, 1)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, 0)
        self.checkBox_1 = QCheckBox(self.groupBox_2)
        self.checkBox_1.setObjectName(u"checkBox_1")
        self.checkBox_1.setMinimumSize(QSize(110, 0))
        font1 = QFont()
        font1.setPointSize(8)
        self.checkBox_1.setFont(font1)

        self.horizontalLayout_3.addWidget(self.checkBox_1)

        self.checkBox_2 = QCheckBox(self.groupBox_2)
        self.checkBox_2.setObjectName(u"checkBox_2")
        self.checkBox_2.setMinimumSize(QSize(110, 0))
        self.checkBox_2.setFont(font1)

        self.horizontalLayout_3.addWidget(self.checkBox_2)

        self.checkBox_3 = QCheckBox(self.groupBox_2)
        self.checkBox_3.setObjectName(u"checkBox_3")
        self.checkBox_3.setMinimumSize(QSize(110, 0))
        self.checkBox_3.setFont(font1)

        self.horizontalLayout_3.addWidget(self.checkBox_3)

        self.checkBox_4 = QCheckBox(self.groupBox_2)
        self.checkBox_4.setObjectName(u"checkBox_4")
        self.checkBox_4.setMinimumSize(QSize(110, 0))
        self.checkBox_4.setFont(font1)

        self.horizontalLayout_3.addWidget(self.checkBox_4)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(-1, -1, 0, 5)
        self.tableWidget = QTableWidget(self.groupBox_2)
        self.tableWidget.setObjectName(u"tableWidget")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy2)
        self.tableWidget.setMinimumSize(QSize(240, 0))
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.verticalLayout_4.addWidget(self.tableWidget)

        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName(u"label_7")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy3)
        font2 = QFont()
        font2.setPointSize(12)
        self.label_7.setFont(font2)
        self.label_7.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_7.setTextFormat(Qt.TextFormat.PlainText)
        self.label_7.setScaledContents(False)
        self.label_7.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_4.addWidget(self.label_7)


        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.widget = QWidget(self.groupBox_2)
        self.widget.setObjectName(u"widget")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy4)
        self.widget.setMinimumSize(QSize(200, 0))

        self.horizontalLayout_2.addWidget(self.widget)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBox_4 = QGroupBox(self.centralwidget)
        self.groupBox_4.setObjectName(u"groupBox_4")
        sizePolicy.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.groupBox_4.setMinimumSize(QSize(275, 125))
        self.gridLayout_2 = QGridLayout(self.groupBox_4)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_5 = QLabel(self.groupBox_4)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_5, 1, 0, 1, 1)

        self.spinBox = QSpinBox(self.groupBox_4)
        self.spinBox.setObjectName(u"spinBox")
        self.spinBox.setMinimum(-1000)
        self.spinBox.setMaximum(1000)

        self.gridLayout_2.addWidget(self.spinBox, 1, 1, 1, 1)

        self.spinBox_2 = QSpinBox(self.groupBox_4)
        self.spinBox_2.setObjectName(u"spinBox_2")
        self.spinBox_2.setMinimum(-1000)
        self.spinBox_2.setMaximum(1000)
        self.spinBox_2.setValue(0)

        self.gridLayout_2.addWidget(self.spinBox_2, 1, 2, 1, 1)

        self.label_6 = QLabel(self.groupBox_4)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_6, 2, 0, 1, 1)

        self.spinBox_3 = QSpinBox(self.groupBox_4)
        self.spinBox_3.setObjectName(u"spinBox_3")
        self.spinBox_3.setMinimum(-1000)
        self.spinBox_3.setMaximum(1000)
        self.spinBox_3.setValue(0)

        self.gridLayout_2.addWidget(self.spinBox_3, 2, 1, 1, 1)

        self.spinBox_4 = QSpinBox(self.groupBox_4)
        self.spinBox_4.setObjectName(u"spinBox_4")
        self.spinBox_4.setMinimum(-1000)
        self.spinBox_4.setMaximum(1000)
        self.spinBox_4.setValue(0)

        self.gridLayout_2.addWidget(self.spinBox_4, 2, 2, 1, 1)

        self.label_3 = QLabel(self.groupBox_4)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_3, 0, 2, 1, 1)

        self.label_4 = QLabel(self.groupBox_4)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_4, 0, 1, 1, 1)


        self.horizontalLayout.addWidget(self.groupBox_4)

        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setMinimumSize(QSize(315, 125))
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.pushButton = QPushButton(self.groupBox_3)
        self.pushButton.setObjectName(u"pushButton")

        self.verticalLayout_3.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.groupBox_3)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.verticalLayout_3.addWidget(self.pushButton_2)

        self.spinBox_5 = QSpinBox(self.groupBox_3)
        self.spinBox_5.setObjectName(u"spinBox_5")
        self.spinBox_5.setMinimum(1)
        self.spinBox_5.setMaximum(9999)

        self.verticalLayout_3.addWidget(self.spinBox_5)


        self.horizontalLayout.addWidget(self.groupBox_3)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)

        self.verticalLayout.addLayout(self.horizontalLayout)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Adquisici\u00f3n de Datos", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Conectar con Sensor", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Puerto:", None))
        self.pushButton_Conectar.setText(QCoreApplication.translate("MainWindow", u"Conectar", None))
        self.pushButton_Iniciar.setText(QCoreApplication.translate("MainWindow", u"Iniciar", None))
        self.ConfirmacionConectado.setText(QCoreApplication.translate("MainWindow", u"Desconectado", None))
        self.pushButton_Detener.setText(QCoreApplication.translate("MainWindow", u"Detener", None))
        self.comboBox_COM.setCurrentText("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Baud:", None))
        self.pushButton_Actualizar.setText(QCoreApplication.translate("MainWindow", u"Actualizar", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Datos", None))
        self.checkBox_1.setText(QCoreApplication.translate("MainWindow", u"Sensor Temp 1", None))
        self.checkBox_2.setText(QCoreApplication.translate("MainWindow", u"Sensor Temp 2", None))
        self.checkBox_3.setText(QCoreApplication.translate("MainWindow", u"Sensor Temp 3", None))
        self.checkBox_4.setText(QCoreApplication.translate("MainWindow", u"Sensor Temp 4", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Temperatura", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"L\u00edmites de Gr\u00e1fica", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"X", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Y", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"M\u00e1ximo", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"M\u00ednimo", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Exportar Datos", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Exportar Tabla", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Tomar Datos Durante X Minutos", None))
    # retranslateUi

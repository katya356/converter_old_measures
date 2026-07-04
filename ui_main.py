rom PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFormLayout,
    QComboBox, QDoubleSpinBox, QPushButton, QLabel,
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PIL import Image
import io
import database
import logging
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конвертер старых мер")
        self.setMinimumSize(800, 600)
        self.resize(900, 650)

        self.db = database.DatabaseManager()
        self.db.init_db()

        self.coeffs = {
            "аршин": 0.7112,
            "сажень": 2.1336,
            "верста": 1066.8,
            "пуд": 16.38,
            "фунт": 0.4095,
            "золотник": 0.004266,
            "метры": 1.0,
            "килограммы": 1.0
        }

        self._setup_ui()
        self._bind_signals()
        self._load_units()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        form = QWidget()
        form_layout = QFormLayout(form)

        self.cb_from = QComboBox()
        self.cb_to = QComboBox()
        self.spin_value = QDoubleSpinBox()
        self.spin_value.setRange(0.01, 1e9)
        self.spin_value.setDecimals(2)
        self.spin_value.setValue(1.0)

        self.lbl_result = QLabel("Результат: ")
        self.lbl_result.setAlignment(Qt.AlignCenter)
        self.lbl_result.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.btn_convert = QPushButton("Перевести")
        self.btn_load_img = QPushButton("Загрузить иконку")
        self.lbl_image = QLabel("Нет изображения")
        self.lbl_image.setAlignment(Qt.AlignCenter)
        self.lbl_image.setMinimumHeight(100)
        self.lbl_image.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")

        form_layout.addRow("Из:", self.cb_from)
        form_layout.addRow("В:", self.cb_to)
        form_layout.addRow("Значение:", self.spin_value)
        form_layout.addRow(self.btn_convert)
        form_layout.addRow(self.lbl_result)
        form_layout.addRow(self.btn_load_img)
        form_layout.addRow(self.lbl_image)

        layout.addWidget(form)

    def _bind_signals(self):
        self.btn_convert.clicked.connect(self._convert)
        self.btn_load_img.clicked.connect(self._load_image)

    def _load_units(self):
        units = sorted(self.coeffs.keys())
        self.cb_from.addItems(units)
        self.cb_to.addItems(units)
        if len(units) > 1:
            self.cb_to.setCurrentIndex(1)

    def _convert(self):
        try:
            from_unit = self.cb_from.currentText()
            to_unit = self.cb_to.currentText()
            value = self.spin_value.value()
            if value <= 0:
                QMessageBox.warning(self, "Ошибка", "Значение должно быть > 0")
                return
            base_value = value * self.coeffs[from_unit]
            result = base_value / self.coeffs[to_unit]
            self.lbl_result.setText(f"Результат: {result:.4f}")
            self.db.insert_record(from_unit, value, to_unit, result)
            logger.info(f"Конвертация: {value} {from_unit} → {result:.4f} {to_unit}")
        except Exception as e:
            logger.error(f"Ошибка конвертации: {e}")
            QMessageBox.critical(self, "Ошибка", f"Что-то пошло не так: {e}")

    def _load_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            try:
                img = Image.open(path).convert("RGBA")
                img.thumbnail((150, 150), Image.LANCZOS)
                byte_arr = io.BytesIO()
                img.save(byte_arr, format='PNG')
                byte_arr.seek(0)
                pixmap = QPixmap()
                pixmap.loadFromData(byte_arr.read(), 'PNG')
                self.lbl_image.setPixmap(pixmap)
                self.lbl_image.setStyleSheet("background-color: #fff; border: 2px solid #999; border-radius: 8px;")
                logger.info(f"Загружено изображение: {path}")
            except Exception as e:
                logger.error(f"Ошибка загрузки изображения: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить: {e}")

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Выход",
            "Вы уверены, что хотите закрыть?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.close()
            logger.info("Приложение закрыто")
            event.accept()
        else:
            event.ignore()

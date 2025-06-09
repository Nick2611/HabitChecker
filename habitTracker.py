from PyQt6.QtGui import QColor, QTextCharFormat
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QCalendarWidget, QListWidget, QListWidgetItem,
    QCheckBox, QFrame, QInputDialog
)
from PyQt6.QtCore import Qt, QDate
import sys
import os
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Habit Tracker")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: rgba(255,250,234,255);")
        self.init_ui()

    # === Interfaz principal ===
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        content_layout = QHBoxLayout()

        calendar_section = self._build_calendar_section()
        activities_section = self._build_activities_section()

        content_layout.addLayout(calendar_section, 2)
        content_layout.addLayout(activities_section, 1)

        main_layout.addLayout(content_layout)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    # === Sección del calendario ===
    def _build_calendar_section(self):
        layout = QVBoxLayout()
        layout.addWidget(self._horizontal_line())

        self.calendar = QCalendarWidget()
        self._setup_calendar_widget()
        self.calendar.currentPageChanged.connect(self._format_outside_days)
        self.calendar.selectionChanged.connect(self._cargar_checkboxes_de_dia)
        self._format_outside_days(self.calendar.yearShown(), self.calendar.monthShown())

        layout.addWidget(self.calendar)

        self.streak_label = QLabel(f"Racha: 0 días")
        self.streak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.streak_label.setStyleSheet("color: black; background-color: rgba(211,225,195,255); border-radius: 8px; padding: 5px;")
        layout.addWidget(self.streak_label)

        self.daily_activity_box = QVBoxLayout()
        self.daily_activity_box.addWidget(self._horizontal_line())

        label = QLabel("Actividades del día")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: black; font-family: 'Helvetica'; font-size: 20px;")
        self.daily_activity_box.addWidget(label)

        self._actualizar_checkboxes()

        frame = QFrame()
        frame.setLayout(self.daily_activity_box)
        layout.addWidget(frame)

        save_button = QPushButton("Actualizar Actividades")
        save_button.setFixedSize(150, 30)
        save_button.setStyleSheet('color: black; background-color: rgba(211,225,195,255); border-radius: 8px;')
        save_button.clicked.connect(self._guardar_estado_dia)
        layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self._actualizar_racha()

        return layout

    def _setup_calendar_widget(self):
        black_format = QTextCharFormat()
        black_format.setForeground(QColor(0, 0, 0))

        for day in range(1, 8):
            self.calendar.setWeekdayTextFormat(Qt.DayOfWeek(day), black_format)
            self.calendar.setHeaderTextFormat(black_format)

        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        self.calendar.setMaximumDate(QDate.currentDate())
        self.calendar.setStyleSheet("""
            QCalendarWidget QToolButton { color: black; }
            QCalendarWidget QMenu { color: black; }
            QCalendarWidget QAbstractItemView { color: black; }
        """)

    def _format_outside_days(self, year, month):
        gray_format = QTextCharFormat()
        gray_format.setForeground(QColor('rgba(255,250,234,255)'))
        gray_format.setBackground(QColor(230, 230, 230))

        first_day = QDate(year, month, 1)
        start_display = first_day.addDays(-first_day.dayOfWeek() + 1)

        for i in range(42):
            date = start_display.addDays(i)
            if date.month() != month:
                self.calendar.setDateTextFormat(date, gray_format)

    def _horizontal_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedSize(600, 2)
        line.setStyleSheet("background-color: rgba(120,148,134,255);")
        return line

    # === Sección de actividades ===
    def _build_activities_section(self):
        layout = QVBoxLayout()

        label = QLabel("Actividades actuales")
        label.setStyleSheet("color: black; font-family: 'Helvetica'; font-size: 23px;")
        layout.addWidget(label)

        self.activity_list = QListWidget()
        self._actualizar_lista_actividades()
        layout.addWidget(self.activity_list)

        buttons = QHBoxLayout()

        add_btn = QPushButton("Agregar")
        add_btn.setFixedSize(100, 30)
        add_btn.setStyleSheet('color: black; background-color: rgba(211,225,195,255); border-radius: 8px;')
        add_btn.clicked.connect(self._ventana_input)

        delete_btn = QPushButton("Eliminar")
        delete_btn.setFixedSize(100, 30)
        delete_btn.setStyleSheet('color: black; background-color: rgba(211,225,195,255); border-radius: 8px;')
        delete_btn.clicked.connect(lambda: self._eliminar_actividad(self.activity_list.currentItem().text()))

        buttons.addWidget(add_btn)
        buttons.addWidget(delete_btn)

        layout.addLayout(buttons)
        return layout

    def _ventana_input(self):
        input_dialog = QInputDialog(self)
        input_dialog.setWindowTitle("Agregar Actividad")
        input_dialog.setLabelText("Ingrese el nombre de la actividad:")
        input_dialog.setStyleSheet("""
            QDialog { background-color: #2e2e2e; }
            QLabel, QLineEdit, QPushButton { color: white; }
            QLineEdit { background-color: #3c3c3c; border: 1px solid #555; padding: 4px; }
            QPushButton { background-color: #444; border: 1px solid #666; padding: 4px 10px; }
            QPushButton:hover { background-color: #555; }
        """)

        if input_dialog.exec():
            texto = input_dialog.textValue().strip()
            if texto:
                self._agregar_actividad(texto)
                self._actualizar_lista_actividades()
                self._actualizar_checkboxes()

    # === Manejo de archivo actividades.txt ===
    def _leer_actividades(self):
        if not os.path.exists('actividades.txt'):
            return []
        with open('actividades.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]

    def _agregar_actividad(self, actividad):
        with open('actividades.txt', 'a') as file:
            file.write(actividad + '\n')

    def _eliminar_actividad(self, actividad):
        actividades = self._leer_actividades()
        actividades = [a for a in actividades if a != actividad]
        with open('actividades.txt', 'w') as file:
            for act in actividades:
                file.write(act + '\n')
        self._actualizar_lista_actividades()
        self._actualizar_checkboxes()

    def _actualizar_lista_actividades(self):
        self.activity_list.clear()
        for actividad in self._leer_actividades():
            QListWidgetItem(actividad, self.activity_list)
        self.activity_list.setStyleSheet('font-size: 18px; color: black;')

    def _actualizar_checkboxes(self):
        while self.daily_activity_box.count() > 2:
            item = self.daily_activity_box.takeAt(2)
            if item.widget():
                item.widget().deleteLater()
        for act in self._leer_actividades():
            cb = QCheckBox(act)
            cb.setStyleSheet("color: black; font-size : 15px;")
            self.daily_activity_box.addWidget(cb)

    # === Guardar y cargar estado diario ===
    def _guardar_estado_dia(self):
        fecha = self.calendar.selectedDate()
        archivo = f"{fecha.year()}_{fecha.month()}.json"
        estado = {}
        for i in range(2, self.daily_activity_box.count()):
            widget = self.daily_activity_box.itemAt(i).widget()
            if isinstance(widget, QCheckBox):
                estado[widget.text()] = widget.isChecked()

        if not os.path.exists(archivo):
            with open(archivo, 'w') as f:
                json.dump({}, f)

        with open(archivo, 'r+') as f:
            try:
                datos = json.load(f)
            except json.JSONDecodeError:
                datos = {}
            datos[str(fecha.day())] = estado
            f.seek(0)
            json.dump(datos, f, indent=2)
            f.truncate()

        self._actualizar_racha()

    def _cargar_checkboxes_de_dia(self):
        fecha = self.calendar.selectedDate()
        archivo = f"{fecha.year()}_{fecha.month()}.json"
        if not os.path.exists(archivo):
            return

        try:
            with open(archivo, 'r') as f:
                datos = json.load(f)
        except json.JSONDecodeError:
            return

        estado_dia = datos.get(str(fecha.day()))
        if estado_dia:
            for i in range(2, self.daily_activity_box.count()):
                widget = self.daily_activity_box.itemAt(i).widget()
                if isinstance(widget, QCheckBox):
                    widget.setChecked(estado_dia.get(widget.text(), False))
        else:
            self._actualizar_checkboxes()

    # === Racha ===
    def _actualizar_racha(self):
        fecha = self.calendar.selectedDate()
        archivo = f"{fecha.year()}_{fecha.month()}.json"
        self.dias_streak = []

        if not os.path.exists(archivo):
            self.streak_label.setText("Racha: 0 días")
            return

        try:
            with open(archivo, 'r') as f:
                datos = json.load(f)
        except json.JSONDecodeError:
            self.streak_label.setText("Racha: 0 días")
            return

        streak = 0
        ultimo_dia = None

        for dia in sorted(map(int, datos.keys())):
            actividades = datos[str(dia)].values()
            if all(actividades):
                if ultimo_dia is None or dia - ultimo_dia == 1:
                    streak += 1
                    self.dias_streak.append(dia)
                else:
                    streak = 1
                    self.dias_streak = [dia]
                ultimo_dia = dia

                formato = QTextCharFormat()
                formato.setBackground(QColor(211, 225, 195))
                formato.setForeground(QColor("darkgreen"))
                self.calendar.setDateTextFormat(QDate(fecha.year(), fecha.month(), dia), formato)
            else:
                formato = QTextCharFormat()
                formato.setBackground(QColor(255, 250, 234))
                formato.setForeground(QColor(0, 0, 0))
                self.calendar.setDateTextFormat(QDate(fecha.year(), fecha.month(), dia), formato)
                streak = 0
                self.dias_streak = []
                ultimo_dia = None

        self.streak_label.setText(f"Racha: {streak} día{'s' if streak != 1 else ''}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
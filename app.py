import sys
from typing import NoReturn, Optional, Union

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from backend import Solver, CustomSolver


class App(QWidget):
    def __init__(self) -> NoReturn:
        super().__init__()
        self.function_type: str = "default"
        self.plot_situation: Optional[QLineEdit] = None
        self.plot_factor: Optional[QLineEdit] = None
        self.eta_max: Optional[QLineEdit] = None
        self.input_folder: Optional[QLineEdit] = None
        self.solver: Optional[Union[Solver, CustomSolver]] = None
        self.table_widget: Optional[QTableWidget] = None
        self.init_ui()

    def init_ui(self) -> NoReturn:
        font_bold = QFont()
        font_bold.setBold(True)

        left = QFrame(self)
        left.setFrameShape(QFrame.StyledPanel)
        left.resize(300, 300)

        label_open = QLabel("Папка вхідних даних", left)
        label_open.move(2, 10)
        self.input_folder = QLineEdit(left)
        self.input_folder.setText("./data/variant_5")
        self.input_folder.setFixedWidth(40)
        self.input_folder.move(200, 10)

        open_file = QPushButton("...", left)
        open_file.setCheckable(True)
        open_file.move(250, 10)
        open_file.clicked[bool].connect(self.open_file_name_dialog)

        functions_type = QComboBox(left)
        functions_type.addItems(
            [
                "Запропонований варіант функціональних залежностей",
                "Власний варіант функціональних залежностей",
            ]
        )
        functions_type.move(2, 50)
        functions_type.activated[str].connect(self.function_type_handler)

        label_eta = QLabel("Рівень допуску", left)
        label_eta.move(2, 90)
        self.eta_max = QLineEdit(left)
        self.eta_max.setText("0.9")
        self.eta_max.setFixedWidth(40)
        self.eta_max.move(150, 88)

        execute_button = QPushButton("Виконати", left)
        execute_button.move(200, 130)
        execute_button.clicked.connect(self.execute)

        right = QFrame(self)
        right.setFrameShape(QFrame.StyledPanel)
        right.resize(300, 500)

        situation_label = QLabel("Номер ситуації", right)
        situation_label.move(2, 10)
        self.plot_situation = QLineEdit(right)
        self.plot_situation.setText("1")
        self.plot_situation.setFixedWidth(40)
        self.plot_situation.move(150, 8)

        factor_label = QLabel("Номер фактору", right)
        factor_label.move(2, 45)
        self.plot_factor = QLineEdit(right)
        self.plot_factor.setText("1")
        self.plot_factor.setFixedWidth(40)
        self.plot_factor.move(150, 43)

        graphic_button = QPushButton("Графік", right)
        graphic_button.move(200, 130)
        graphic_button.clicked.connect(self.graphic)

        table_frame = QFrame(self)
        table_frame.setFrameShape(QFrame.StyledPanel)
        table_frame.resize(500, 500)

        self.table_widget = QTableWidget(table_frame)
        self.table_widget.resize(1050, 160)
        self.table_widget.setRowCount(4)
        self.table_widget.setColumnCount(8)
        self.table_widget.move(0, 0)
        header = self.table_widget.horizontalHeader()
        for index in range(8):
            header.setSectionResizeMode(index, QHeaderView.ResizeToContents)
        for index in range(4):
            self.table_widget.setVerticalHeaderItem(
                index, QTableWidgetItem(f"S{index + 1}")
            )
        for index in range(7):
            self.table_widget.setHorizontalHeaderItem(
                index, QTableWidgetItem(f"Ф{index + 1}")
            )
        self.table_widget.setHorizontalHeaderItem(
            7, QTableWidgetItem(f"Класифікація ситуації")
        )

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(left)
        horizontal_layout.addWidget(right)
        vertical_layout = QVBoxLayout()
        vertical_layout.addLayout(horizontal_layout)
        vertical_layout.addWidget(table_frame)
        self.setLayout(vertical_layout)

        self.setGeometry(150, 150, 1050, 600)
        self.setWindowTitle("Інформаційний аналіз")
        self.show()

    def open_file_name_dialog(self) -> NoReturn:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        target_path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if target_path:
            self.input_folder.setText(target_path)

    def function_type_handler(self, value: str) -> NoReturn:
        if value == "Власний варіант функціональних залежностей":
            self.function_type = "custom"
        else:
            self.function_type = "default"

    def execute(self) -> NoReturn:
        if self.function_type == "default":
            self.solver = Solver(input_folder=self.input_folder.text())
        else:
            self.solver = CustomSolver(input_folder=self.input_folder.text())
        try:
            t_0, classification = self.solver.solve(eta_max=float(self.eta_max.text()))
            for s_index in range(len(t_0)):
                for f_index in range(len(t_0[0])):
                    result = t_0[s_index][f_index]
                    if result == "Not available":
                        result = ""
                    elif result == "Not exist":
                        result = "Порож. мн-на"
                    else:
                        result = [round(result[0], 2), round(result[1], 2)]
                    self.table_widget.setItem(
                        s_index, f_index, QTableWidgetItem(str(result))
                    )
                self.table_widget.setItem(
                    s_index, 7, QTableWidgetItem(str(classification[s_index]))
                )
        except ValueError:
            print("У якості рівня допуску можливе лише число")

    def graphic(self) -> NoReturn:
        if self.solver is not None:
            try:
                self.solver.plot_i(
                    s=int(self.plot_situation.text()) - 1,
                    f=int(self.plot_factor.text()) - 1,
                )
            except IndexError:
                print("Такої ситуації або фактору у заданій вибірці немає")
        else:
            print("Спершу виконайте обчислення")


if __name__ == "__main__":
    pyqt_application = QApplication(sys.argv)
    my_app = App()
    sys.exit(pyqt_application.exec_())

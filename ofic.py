import sys
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
                             QPushButton, QLineEdit, QLabel, QMessageBox, QDialog, QFormLayout, QComboBox, QTabWidget,
                             QCalendarWidget, QDialogButtonBox, QTimeEdit, QHeaderView, QDateEdit, QInputDialog)
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QColor

class WaiterWindow(QMainWindow):
    def __init__(self, connection, cursor, login_window):
        super().__init__()

        self.setWindowTitle("Окно официанта")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.connection = connection
        self.cursor = cursor
        self.login_window = login_window

        self.init_ui()

    def init_ui(self):
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.create_orders_tab()
        self.create_tables_tab()
        self.create_menu_tab()
        self.create_history_tab()

        self.logout_button = QPushButton("Выход")
        self.logout_button.clicked.connect(self.logout)
        self.layout.addWidget(self.logout_button)

    def logout(self):
        self.close()
        self.login_window.show()

    def create_orders_tab(self):
        orders_tab = QWidget()
        orders_layout = QVBoxLayout(orders_tab)

        orders_layout.addWidget(QLabel("Прием заказов"))
        self.orders_table = QTableWidget(0, 8)
        self.orders_table.setHorizontalHeaderLabels(["ID", "Столик", "Дата", "Время", "Сумма", "Статус", "Блюдо", "Количество"])
        self.orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.orders_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        orders_layout.addWidget(self.orders_table)
        self.load_orders_data()

        self.add_order_button = QPushButton("Добавить заказ")
        self.add_order_button.clicked.connect(self.add_order)
        orders_layout.addWidget(self.add_order_button)

        self.edit_order_button = QPushButton("Изменить заказ")
        self.edit_order_button.clicked.connect(self.edit_order)
        orders_layout.addWidget(self.edit_order_button)

        self.complete_order_button = QPushButton("Завершить заказ")
        self.complete_order_button.clicked.connect(self.complete_order)
        orders_layout.addWidget(self.complete_order_button)

        self.delete_order_button = QPushButton("Удалить заказ")
        self.delete_order_button.clicked.connect(self.delete_order)
        orders_layout.addWidget(self.delete_order_button)

        self.tab_widget.addTab(orders_tab, "Заказы")

    def create_tables_tab(self):
        tables_tab = QWidget()
        tables_layout = QVBoxLayout(tables_tab)

        tables_layout.addWidget(QLabel("Столики"))
        self.tables_table = QTableWidget(0, 4)
        self.tables_table.setHorizontalHeaderLabels(["ID", "Номер столика", "Вместимость", "Статус"])
        self.tables_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tables_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tables_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tables_layout.addWidget(self.tables_table)
        self.load_tables_data()

        self.manage_table_button = QPushButton("Управление столиками")
        self.manage_table_button.clicked.connect(self.manage_table)
        tables_layout.addWidget(self.manage_table_button)

        self.tab_widget.addTab(tables_tab, "Столики")

    def create_menu_tab(self):
        menu_tab = QWidget()
        menu_layout = QVBoxLayout(menu_tab)

        menu_layout.addWidget(QLabel("Меню"))
        self.menu_table = QTableWidget(0, 4)
        self.menu_table.setHorizontalHeaderLabels(["ID", "Название блюда", "Цена", "Категория"])
        self.menu_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.menu_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.menu_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        menu_layout.addWidget(self.menu_table)
        self.load_menu_data()

        self.tab_widget.addTab(menu_tab, "Меню")

    def create_history_tab(self):
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)

        history_layout.addWidget(QLabel("История заказов"))
        self.history_table = QTableWidget(0, 8)
        self.history_table.setHorizontalHeaderLabels(["ID", "Столик", "Дата", "Время", "Сумма", "Статус", "Блюдо", "Количество"])
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        history_layout.addWidget(self.history_table)
        self.load_history_data()

        self.start_date_input = QDateEdit(self)
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        self.end_date_input = QDateEdit(self)
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())

        history_layout.addWidget(QLabel("Начальная дата:"))
        history_layout.addWidget(self.start_date_input)
        history_layout.addWidget(QLabel("Конечная дата:"))
        history_layout.addWidget(self.end_date_input)

        self.filter_history_button = QPushButton("Фильтровать")
        self.filter_history_button.clicked.connect(self.filter_history_data)
        history_layout.addWidget(self.filter_history_button)

        self.clear_filter_button = QPushButton("Отменить фильтрацию")
        self.clear_filter_button.clicked.connect(self.load_history_data)
        history_layout.addWidget(self.clear_filter_button)

        self.tab_widget.addTab(history_tab, "История заказов")

    def load_orders_data(self):
        self.cursor.execute("SELECT Orders.order_id, Tables.table_number, Orders.order_date, Orders.order_time, Orders.total_amount, Orders.status, Menu.dish_name, Orders.quantity FROM Orders JOIN Tables ON Orders.table_id = Tables.table_id JOIN Menu ON Orders.dish_id = Menu.dish_id WHERE Orders.status IN ('ожидает', 'в процессе', 'готов')")
        orders = self.cursor.fetchall()
        self.orders_table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            for col, data in enumerate(order):
                item = QTableWidgetItem(str(data))
                if order[5] == 'ожидает':
                    item.setBackground(QColor('#FC9063'))
                elif order[5] == 'в процессе':
                    item.setBackground(QColor('#F8F380'))
                elif order[5] == 'готов':
                    item.setBackground(QColor('#57F40E'))
                self.orders_table.setItem(row, col, item)

    def load_tables_data(self):
        self.cursor.execute("SELECT * FROM Tables")
        tables = self.cursor.fetchall()
        self.tables_table.setRowCount(len(tables))
        for row, table in enumerate(tables):
            for col, data in enumerate(table):
                self.tables_table.setItem(row, col, QTableWidgetItem(str(data)))

    def load_menu_data(self):
        self.cursor.execute("SELECT Menu.dish_id, Menu.dish_name, Menu.price, Categories.category_name FROM Menu JOIN Categories ON Menu.category_id = Categories.category_id")
        menu = self.cursor.fetchall()
        self.menu_table.setRowCount(len(menu))
        for row, dish in enumerate(menu):
            for col, data in enumerate(dish):
                self.menu_table.setItem(row, col, QTableWidgetItem(str(data)))

    def load_history_data(self):
        self.cursor.execute("SELECT Orders.order_id, Tables.table_number, Orders.order_date, Orders.order_time, Orders.total_amount, Orders.status, Menu.dish_name, Orders.quantity FROM Orders JOIN Tables ON Orders.table_id = Tables.table_id JOIN Menu ON Orders.dish_id = Menu.dish_id WHERE Orders.status IN ('отменен', 'оплачен')")
        history = self.cursor.fetchall()
        self.history_table.setRowCount(len(history))
        for row, order in enumerate(history):
            for col, data in enumerate(order):
                item = QTableWidgetItem(str(data))
                if order[5] == 'оплачен':
                    item.setBackground(QColor('lightgreen'))
                elif order[5] == 'отменен':
                    item.setBackground(QColor('#D8D7D7'))
                self.history_table.setItem(row, col, item)

    def filter_history_data(self):
        start_date = self.start_date_input.date().toString(Qt.DateFormat.ISODate)
        end_date = self.end_date_input.date().toString(Qt.DateFormat.ISODate)
        self.cursor.execute("""
        SELECT Orders.order_id, Tables.table_number, Orders.order_date, Orders.order_time, Orders.total_amount, Orders.status, Menu.dish_name, Orders.quantity
        FROM Orders
        JOIN Tables ON Orders.table_id = Tables.table_id
        JOIN Menu ON Orders.dish_id = Menu.dish_id
        WHERE Orders.status IN ('отменен', 'оплачен') AND Orders.order_date BETWEEN ? AND ?
        """, (start_date, end_date))
        history = self.cursor.fetchall()
        self.history_table.setRowCount(len(history))
        for row, order in enumerate(history):
            for col, data in enumerate(order):
                item = QTableWidgetItem(str(data))
                if order[5] == 'оплачен':
                    item.setBackground(QColor('lightgreen'))
                elif order[5] == 'отменен':
                    item.setBackground(QColor('#D8D7D7'))
                self.history_table.setItem(row, col, item)

    def add_order(self):
        dialog = AddOrderDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            table_id, order_date, order_time, dish_id, quantity = dialog.get_order_data()
            total_amount = dialog.get_total_amount()
            try:
                self.cursor.execute(
                    "INSERT INTO Orders (table_id, order_date, order_time, total_amount, status, dish_id, quantity) VALUES (?, ?, ?, ?, 'ожидает', ?, ?)",
                    (table_id, order_date, order_time, total_amount, dish_id, quantity))
                self.connection.commit()
                self.load_orders_data()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить заказ: {e}")

    def edit_order(self):
        selected_row = self.orders_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите заказ для изменения.")
            return

        order_id = self.orders_table.item(selected_row, 0).text()
        dialog = AddOrderDialog(self, order_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            table_id, order_date, order_time, dish_id, quantity = dialog.get_order_data()
            total_amount = dialog.get_total_amount()
            try:
                self.cursor.execute(
                    "UPDATE Orders SET table_id = ?, order_date = ?, order_time = ?, total_amount = ?, dish_id = ?, quantity = ? WHERE order_id = ?",
                    (table_id, order_date, order_time, total_amount, dish_id, quantity, order_id))
                self.connection.commit()
                self.load_orders_data()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось изменить заказ: {e}")

    def complete_order(self):
        selected_row = self.orders_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите заказ для завершения.")
            return

        order_id = self.orders_table.item(selected_row, 0).text()
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Завершение заказа")
        msg_box.setText("Выберите статус заказа:")

        msg_box.addButton("Отменен", QMessageBox.ButtonRole.AcceptRole)
        msg_box.addButton("Оплачен", QMessageBox.ButtonRole.RejectRole)
        msg_box.exec()

        if msg_box.clickedButton().text() == "Отменен":
            status = "отменен"
        else:
            status = "оплачен"

        try:
            self.cursor.execute("UPDATE Orders SET status = ? WHERE order_id = ?", (status, order_id))
            self.connection.commit()
            self.load_orders_data()
            self.load_history_data()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось завершить заказ: {e}")

    def delete_order(self):
        selected_row = self.orders_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите заказ для удаления.")
            return

        order_id = self.orders_table.item(selected_row, 0).text()
        reply = QMessageBox.question(self, "Подтверждение", "Вы точно хотите удалить заказ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.cursor.execute("DELETE FROM Orders WHERE order_id = ?", (int(order_id),))
                self.connection.commit()
                self.load_orders_data()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить заказ: {e}")

    def manage_table(self):
        selected_row = self.tables_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите столик для управления.")
            return

        table_id = self.tables_table.item(selected_row, 0).text()
        dialog = ManageTableDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            status = dialog.get_table_data()
            try:
                self.cursor.execute("UPDATE Tables SET status = ? WHERE table_id = ?", (status, table_id))
                self.connection.commit()
                self.load_tables_data()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить статус столика: {e}")

class AddOrderDialog(QDialog):
    def __init__(self, parent=None, order_id=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить заказ")
        self.layout = QFormLayout(self)

        self.order_id = order_id
        self.table_id_input = QComboBox(self)
        self.order_date_input = QCalendarWidget(self)
        self.order_date_input.setGridVisible(True)
        self.order_time_input = QTimeEdit(self)
        self.dish_id_input = QComboBox(self)
        self.quantity_input = QLineEdit(self)

        self.layout.addRow("Столик", self.table_id_input)
        self.layout.addRow("Дата", self.order_date_input)
        self.layout.addRow("Время", self.order_time_input)
        self.layout.addRow("Блюдо", self.dish_id_input)
        self.layout.addRow("Количество", self.quantity_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

        self.load_table_ids()
        self.load_dish_ids()

        self.dish_id_input.currentIndexChanged.connect(self.update_total_amount)
        self.quantity_input.textChanged.connect(self.update_total_amount)

        if order_id:
            self.load_order_data()

    def load_table_ids(self):
        connection = sqlite3.connect('restaurant.db')
        cursor = connection.cursor()
        cursor.execute("SELECT table_id, table_number FROM Tables")
        tables = cursor.fetchall()
        for table in tables:
            self.table_id_input.addItem(f"{table[1]} (ID: {table[0]})", table[0])
        connection.close()

    def load_dish_ids(self):
        connection = sqlite3.connect('restaurant.db')
        cursor = connection.cursor()
        cursor.execute("SELECT dish_id, dish_name FROM Menu")
        dishes = cursor.fetchall()
        for dish in dishes:
            self.dish_id_input.addItem(f"{dish[1]} (ID: {dish[0]})", dish[0])
        connection.close()

    def update_total_amount(self):
        dish_id = self.dish_id_input.currentData()
        quantity_text = self.quantity_input.text().strip()

        if not dish_id or not quantity_text:
            self.total_amount = 0.0
            return

        try:
            quantity = int(quantity_text)
        except ValueError:
            self.total_amount = 0.0
            return

        connection = sqlite3.connect('restaurant.db')
        cursor = connection.cursor()
        cursor.execute("SELECT price FROM Menu WHERE dish_id = ?", (dish_id,))
        price = cursor.fetchone()
        connection.close()

        if price:
            self.total_amount = price[0] * quantity
        else:
            self.total_amount = 0.0

    def get_order_data(self):
        table_id = self.table_id_input.currentData()
        order_date = self.order_date_input.selectedDate().toString(Qt.DateFormat.ISODate)
        order_time = self.order_time_input.time().toString(Qt.DateFormat.ISODate)
        dish_id = self.dish_id_input.currentData()
        quantity = self.quantity_input.text().strip()

        if not table_id:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите столик.")
            return None, None, None, None, None

        if not order_date:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите дату.")
            return None, None, None, None, None

        if not order_time:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите время.")
            return None, None, None, None, None

        if not dish_id:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите блюдо.")
            return None, None, None, None, None

        if not quantity:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, введите количество.")
            return None, None, None, None, None

        try:
            quantity = int(quantity)
        except ValueError:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, введите корректное количество.")
            return None, None, None, None, None

        return table_id, order_date, order_time, dish_id, quantity

    def get_total_amount(self):
        return self.total_amount

    def load_order_data(self):
        connection = sqlite3.connect('restaurant.db')
        cursor = connection.cursor()
        cursor.execute("SELECT table_id, order_date, order_time, dish_id, quantity FROM Orders WHERE order_id = ?", (self.order_id,))
        order = cursor.fetchone()
        if order:
            self.table_id_input.setCurrentText(str(order[0]))
            self.order_date_input.setSelectedDate(QDate.fromString(order[1], Qt.DateFormat.ISODate))
            self.order_time_input.setTime(QTime.fromString(order[2], Qt.DateFormat.ISODate))
            self.dish_id_input.setCurrentText(str(order[3]))
            self.quantity_input.setText(str(order[4]))
        connection.close()

class ManageTableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление столиками")
        self.layout = QFormLayout(self)

        self.status_input = QComboBox(self)
        self.status_input.addItems(["свободен", "занят", "забронирован"])

        self.layout.addRow("Статус", self.status_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_table_data(self):
        return self.status_input.currentText()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    connection = sqlite3.connect('restaurant.db')
    cursor = connection.cursor()
    window = WaiterWindow(connection, cursor)
    window.show()
    sys.exit(app.exec())

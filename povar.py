import sys
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
                             QPushButton, QLabel, QMessageBox, QTabWidget, QDialog, QFormLayout, QLineEdit,
                             QDialogButtonBox, QTimeEdit, QHeaderView, QDateEdit)
from PyQt6.QtCore import Qt, QTime, QDate
from PyQt6.QtGui import QColor

class ChefWindow(QMainWindow):
    def __init__(self, connection, cursor, login_window):
        super().__init__()

        self.setWindowTitle("Окно повара")
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

        self.create_current_orders_tab()
        self.create_ingredients_tab()
        self.create_history_tab()

        self.logout_button = QPushButton("Выход")
        self.logout_button.clicked.connect(self.logout)
        self.layout.addWidget(self.logout_button)

    def logout(self):
        self.close()
        self.login_window.show()



    def create_current_orders_tab(self):
        current_orders_tab = QWidget()
        current_orders_layout = QVBoxLayout(current_orders_tab)

        current_orders_layout.addWidget(QLabel("Текущие заказы"))
        self.current_orders_table = QTableWidget(0, 8)
        self.current_orders_table.setHorizontalHeaderLabels(["ID", "Столик", "Дата", "Время", "Сумма", "Статус", "Блюдо", "Количество"])
        self.current_orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.current_orders_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.current_orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        current_orders_layout.addWidget(self.current_orders_table)
        self.load_current_orders_data()

        self.update_status_button = QPushButton("Обновить статус")
        self.update_status_button.clicked.connect(self.update_order_status)
        current_orders_layout.addWidget(self.update_status_button)

        self.tab_widget.addTab(current_orders_tab, "Текущие заказы")

    def create_ingredients_tab(self):
        ingredients_tab = QWidget()
        ingredients_layout = QVBoxLayout(ingredients_tab)

        ingredients_layout.addWidget(QLabel("Ингредиенты"))
        self.ingredients_table = QTableWidget(0, 3)
        self.ingredients_table.setHorizontalHeaderLabels(["ID", "Название ингредиента", "Количество"])
        self.ingredients_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.ingredients_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.ingredients_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        ingredients_layout.addWidget(self.ingredients_table)
        self.load_ingredients_data()

        self.add_ingredient_button = QPushButton("Добавить ингредиент")
        self.add_ingredient_button.clicked.connect(self.add_ingredient)
        ingredients_layout.addWidget(self.add_ingredient_button)

        self.update_ingredient_button = QPushButton("Обновить ингредиент")
        self.update_ingredient_button.clicked.connect(self.update_ingredient)
        ingredients_layout.addWidget(self.update_ingredient_button)

        self.tab_widget.addTab(ingredients_tab, "Ингредиенты")

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

    def load_current_orders_data(self):
        self.cursor.execute("""
        SELECT Orders.order_id, Tables.table_number, Orders.order_date,
        Orders.order_time, Orders.total_amount, Orders.status,
        Menu.dish_name, Orders.quantity
        FROM Orders
        JOIN Tables ON Orders.table_id = Tables.table_id
        JOIN Menu ON Orders.dish_id = Menu.dish_id
        WHERE Orders.status IN ('ожидает', 'в процессе')
        """)
        orders = self.cursor.fetchall()
        self.current_orders_table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            for col, data in enumerate(order):
                item = QTableWidgetItem(str(data))
                if order[5] == 'ожидает':
                    item.setBackground(QColor('#FC9063'))
                elif order[5] == 'в процессе':
                    item.setBackground(QColor('#F8F380'))
                self.current_orders_table.setItem(row, col, item)

    def load_ingredients_data(self):
        self.cursor.execute("SELECT * FROM Ingredients")
        ingredients = self.cursor.fetchall()
        self.ingredients_table.setRowCount(len(ingredients))
        for row, ingredient in enumerate(ingredients):
            for col, data in enumerate(ingredient):
                self.ingredients_table.setItem(row, col, QTableWidgetItem(str(data)))

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

    def update_order_status(self):
        selected_items = self.current_orders_table.selectedItems()
        if selected_items:
            order_id = int(selected_items[0].text())
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Обновить статус")
            msg_box.setText("Выберите новый статус заказа:")
            msg_box.addButton("В процессе", QMessageBox.ButtonRole.AcceptRole)
            msg_box.addButton("Готов", QMessageBox.ButtonRole.RejectRole)
            msg_box.exec()

            if msg_box.clickedButton().text() == "В процессе":
                status = "в процессе"
            else:
                status = "готов"

            try:
                self.cursor.execute("UPDATE Orders SET status = ? WHERE order_id = ?", (status, order_id))
                self.connection.commit()
                self.load_current_orders_data()
                self.load_history_data()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить статус заказа: {e}")

    def add_ingredient(self):
        dialog = AddIngredientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            ingredient_name, quantity = dialog.get_ingredient_data()
            try:
                self.cursor.execute("INSERT INTO Ingredients (ingredient_name, quantity) VALUES (?, ?)",
                                    (ingredient_name, quantity))
                self.connection.commit()
                self.load_ingredients_data()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить ингредиент: {e}")

    def update_ingredient(self):
        selected_items = self.ingredients_table.selectedItems()
        if selected_items:
            ingredient_id = int(selected_items[0].text())
            dialog = UpdateIngredientDialog(self, ingredient_id)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                ingredient_name, quantity = dialog.get_ingredient_data()
                try:
                    self.cursor.execute("UPDATE Ingredients SET ingredient_name = ?, quantity = ? WHERE ingredient_id = ?",
                                        (ingredient_name, quantity, ingredient_id))
                    self.connection.commit()
                    self.load_ingredients_data()
                except sqlite3.Error as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось обновить ингредиент: {e}")

class AddIngredientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить ингредиент")
        self.layout = QFormLayout(self)

        self.ingredient_name_input = QLineEdit(self)
        self.quantity_input = QLineEdit(self)

        self.layout.addRow("Название ингредиента", self.ingredient_name_input)
        self.layout.addRow("Количество", self.quantity_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_ingredient_data(self):
        return self.ingredient_name_input.text(), float(self.quantity_input.text())

class UpdateIngredientDialog(QDialog):
    def __init__(self, parent=None, ingredient_id=None):
        super().__init__(parent)
        self.setWindowTitle("Обновить ингредиент")
        self.layout = QFormLayout(self)

        self.ingredient_id = ingredient_id
        self.ingredient_name_input = QLineEdit(self)
        self.quantity_input = QLineEdit(self)

        self.layout.addRow("Название ингредиента", self.ingredient_name_input)
        self.layout.addRow("Количество", self.quantity_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

        self.load_ingredient_data()

    def load_ingredient_data(self):
        connection = sqlite3.connect('restaurant.db')
        cursor = connection.cursor()
        cursor.execute("SELECT ingredient_name, quantity FROM Ingredients WHERE ingredient_id = ?", (self.ingredient_id,))
        ingredient = cursor.fetchone()
        if ingredient:
            self.ingredient_name_input.setText(ingredient[0])
            self.quantity_input.setText(str(ingredient[1]))
        connection.close()

    def get_ingredient_data(self):
        return self.ingredient_name_input.text(), float(self.quantity_input.text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    connection = sqlite3.connect('restaurant.db')
    cursor = connection.cursor()
    window = ChefWindow(connection, cursor)
    window.show()
    sys.exit(app.exec())

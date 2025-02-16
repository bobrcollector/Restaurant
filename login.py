import sys
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QVBoxLayout, QWidget)
from admin import AdminWindow
from ofic import WaiterWindow
from povar import ChefWindow


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 300, 150)
        self.setFixedSize(300, 150)

        # Метки для ввода email и пароля
        self.label_email = QLabel("Email")
        self.input_email = QLineEdit()

        self.label_password = QLabel("Пароль")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.button_login = QPushButton("Войти")
        self.button_login.clicked.connect(self.login)

        layout = QVBoxLayout()
        layout.addWidget(self.label_email)
        layout.addWidget(self.input_email)
        layout.addWidget(self.label_password)
        layout.addWidget(self.input_password)
        layout.addWidget(self.button_login)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.connection = sqlite3.connect('restaurant.db')
        self.cursor = self.connection.cursor()

    def login(self):
        email = self.input_email.text()
        password = self.input_password.text()

        # Проверка пользователя в базе данных
        self.cursor.execute("SELECT * FROM Users WHERE email = ? AND password = ?", (email, password))
        user = self.cursor.fetchone()

        if user:
            role = user[4]
            if role == "Администратор":
                self.open_admin_window()
            elif role == "Официант":
                self.open_waiter_window()
            elif role == "Повар":
                self.open_chef_window()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный email или пароль")

    def open_admin_window(self):
        self.admin_window = AdminWindow(self)
        self.admin_window.show()
        self.close()

    def open_waiter_window(self):
        self.waiter_window = WaiterWindow(self.connection, self.cursor, self)
        self.waiter_window.show()
        self.close()

    def open_chef_window(self):
        self.chef_window = ChefWindow(self.connection, self.cursor, self)
        self.chef_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())

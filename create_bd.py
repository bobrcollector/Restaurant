import sqlite3

connection = sqlite3.connect('restaurant.db')
cursor = connection.cursor()

# Таблица пользователей
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT CHECK(role IN ('Администратор', 'Официант', 'Повар')) NOT NULL,
    created_at TEXT NOT NULL
);
''')

# Таблица столов
cursor.execute('''
CREATE TABLE IF NOT EXISTS Tables (
    table_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_number INTEGER NOT NULL,
    capacity INTEGER NOT NULL,
    status TEXT CHECK(status IN ('свободен', 'занят', 'забронирован')) NOT NULL
);
''')

# Таблица категорий блюд
cursor.execute('''
CREATE TABLE IF NOT EXISTS Categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL
);
''')

# Таблица меню
cursor.execute('''
CREATE TABLE IF NOT EXISTS Menu (
    dish_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dish_name TEXT NOT NULL,
    price REAL NOT NULL,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);
''')

# Таблица заказов
cursor.execute('''
CREATE TABLE IF NOT EXISTS Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    order_time TEXT NOT NULL,
    total_amount REAL NOT NULL,
    status TEXT NOT NULL,
    dish_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (table_id) REFERENCES Tables(table_id),
    FOREIGN KEY (dish_id) REFERENCES Menu(dish_id)
);
''')

# Таблица бронирований
cursor.execute('''
CREATE TABLE IF NOT EXISTS Reservations (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_id INTEGER NOT NULL,
    customer_name TEXT NOT NULL,
    reservation_date TEXT NOT NULL,
    status TEXT CHECK(status IN ('активно', 'отменено')) NOT NULL,
    FOREIGN KEY (table_id) REFERENCES Tables(table_id)
);
''')

# Таблица ингредиентов
cursor.execute('''
CREATE TABLE IF NOT EXISTS Ingredients (
    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT NOT NULL,
    quantity REAL NOT NULL
);
''')

# Таблица смен работников
cursor.execute('''
CREATE TABLE IF NOT EXISTS Shifts (
    shift_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    shift_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
''')


connection.commit()
connection.close()

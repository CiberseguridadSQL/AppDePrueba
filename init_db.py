import sqlite3
import os

DATABASE = 'vulnerable.db'

if os.path.exists(DATABASE):
    os.remove(DATABASE)

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'user',
    bio TEXT
)
''')

cursor.execute('''
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    price REAL
)
''')

cursor.execute('''
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    total REAL
)
''')

cursor.execute("INSERT INTO users (username, password, email, role) VALUES ('admin', 'admin123', 'admin@example.com', 'admin')")
cursor.execute("INSERT INTO users (username, password, email, role) VALUES ('user1', 'pass123', 'user1@example.com', 'user')")
cursor.execute("INSERT INTO users (username, password, email, role) VALUES ('user2', 'mypassword', 'user2@example.com', 'user')")
cursor.execute("INSERT INTO users (username, password, email, role) VALUES ('testuser', 'test456', 'test@example.com', 'user')")

cursor.execute("INSERT INTO products (name, category, price) VALUES ('Laptop', 'electronics', 999.99)")
cursor.execute("INSERT INTO products (name, category, price) VALUES ('Mouse', 'electronics', 29.99)")
cursor.execute("INSERT INTO products (name, category, price) VALUES ('Desk', 'furniture', 299.99)")
cursor.execute("INSERT INTO products (name, category, price) VALUES ('Chair', 'furniture', 199.99)")

cursor.execute("INSERT INTO orders (user_id, product_id, quantity, total) VALUES (1, 1, 1, 999.99)")
cursor.execute("INSERT INTO orders (user_id, product_id, quantity, total) VALUES (2, 2, 2, 59.98)")
cursor.execute("INSERT INTO orders (user_id, product_id, quantity, total) VALUES (3, 3, 1, 299.99)")

conn.commit()
conn.close()

print("Base de datos inicializada correctamente!")
print("Tablas creadas: users, products, orders")
print("\nUsuarios de prueba:")
print("  - admin:admin123 (role: admin)")
print("  - user1:pass123 (role: user)")
print("  - user2:mypassword (role: user)")

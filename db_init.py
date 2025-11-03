import sqlite3
from datetime import date

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    isic_id TEXT UNIQUE
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    meal_type TEXT,
    date TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS served (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    served_time TEXT,
    FOREIGN KEY(order_id) REFERENCES orders(id)
)
""")

# Test data
c.execute("INSERT OR IGNORE INTO users (name, isic_id) VALUES ('Jan Novak', '123456'), ('Petr Svoboda', '654321'), ('Kryštof', '909228709944')")
today = str(date.today())

# Zkontroluj, jestli má Kryštof objednávku
c.execute("SELECT id FROM users WHERE isic_id='909228709944'")
user_id = c.fetchone()[0]
c.execute("INSERT OR IGNORE INTO orders (user_id, meal_type, date) VALUES (?, 'Menu 1', ?)", (user_id, today))

conn.commit()
conn.close()
print("Databáze připravena s uživatelem 909228709944.")

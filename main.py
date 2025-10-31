import sqlite3
import tkinter as tk
from datetime import datetime, date

DB_PATH = "database.db"
queue = []

def scan_isic(isic_id):
    global queue
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, name FROM users WHERE isic_id = ?", (isic_id,))
    user = c.fetchone()
    if not user:
        message = f"Neznámý ISIC: {isic_id}"
    else:
        user_id, name = user
        today = str(date.today())
        c.execute("SELECT id, meal_type FROM orders WHERE user_id = ? AND date = ?", (user_id, today))
        order = c.fetchone()

        if not order:
            message = f"{name} dnes nemá objednáno."
        else:
            order_id, meal = order
            c.execute("SELECT * FROM served WHERE order_id = ?", (order_id,))
            already = c.fetchone()

            if already:
                message = f"{name} ({meal}) – ❌ UŽ VYDÁNO!"
            else:
                c.execute("INSERT INTO served (order_id, served_time) VALUES (?, ?)", (order_id, datetime.now()))
                conn.commit()
                message = f"{name} ({meal}) – ✅ VYDÁNO"

    conn.close()

    queue.insert(0, message)
    queue = queue[:3]  # zobrazí jen 3 poslední
    update_display()

def update_display():
    text.delete(1.0, tk.END)
    for msg in queue:
        text.insert(tk.END, msg + "\n")

def on_submit():
    isic = entry.get().strip()
    if isic:
        scan_isic(isic)
    entry.delete(0, tk.END)

root = tk.Tk()
root.title("Jídelní systém")
root.geometry("500x300")

entry = tk.Entry(root, font=("Arial", 16))
entry.pack(pady=10)
entry.bind("<Return>", lambda e: on_submit())

text = tk.Text(root, height=10, font=("Arial", 14))
text.pack()

root.mainloop()

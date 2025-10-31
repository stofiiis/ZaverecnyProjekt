import sqlite3
import tkinter as tk
from datetime import datetime, date

DB_PATH = "database.db"

def scan_isic(isic_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, name FROM users WHERE isic_id = ?", (isic_id,))
    user = c.fetchone()

    if not user:
        show_result("❌", f"Neznámý ISIC: {isic_id}", "#ff5555")
    else:
        user_id, name = user
        today = str(date.today())

        c.execute("SELECT id, meal_type FROM orders WHERE user_id = ? AND date = ?", (user_id, today))
        order = c.fetchone()

        if not order:
            show_result("⚠️", f"{name} dnes nemá objednáno.", "#ffaa00")
        else:
            order_id, meal = order
            c.execute("SELECT * FROM served WHERE order_id = ?", (order_id,))
            already = c.fetchone()

            if already:
                show_result("🚫", f"{name} ({meal}) – UŽ VYDÁNO!", "#ff3333")
            else:
                c.execute("INSERT INTO served (order_id, served_time) VALUES (?, ?)", (order_id, datetime.now()))
                conn.commit()
                show_result("✅", f"{name} ({meal}) – VYDÁNO", "#44ff88")

    conn.close()


def show_result(symbol, message, color):
    """Zobrazí symbol + text, 2× zapulzuje a zmizí"""
    for widget in frame_result.winfo_children():
        widget.destroy()

    # Symbol
    symbol_label = tk.Label(
        frame_result,
        text=symbol,
        font=("Segoe UI Emoji", 10),  # velikost se přepočítává dynamicky
        fg=color,
        bg="#222"
    )
    symbol_label.pack(pady=10, expand=True)

    # Text
    text_label = tk.Label(
        frame_result,
        text=message,
        fg="white",
        bg="#222",
        font=("Segoe UI", 10, "bold"),
        wraplength=800,
        justify="center"
    )
    text_label.pack(pady=5, expand=True)

    # Spustí animaci
    animate_symbol(symbol_label, color, text_label)


def animate_symbol(widget, color, text_widget):
    """Dvakrát zapulzuje a pak zmizí"""
    scale = 1.0
    direction = 1
    pulses = [0]  # počítadlo uvnitř closure

    def pulse():
        nonlocal scale, direction
        scale += 0.08 * direction

        if scale >= 1.3:
            direction = -1
        elif scale <= 1.0:
            direction = 1
            pulses[0] += 1

        # Velikost fontu podle okna
        size = int(min(root.winfo_width(), root.winfo_height()) * 0.25 * scale)
        widget.config(font=("Segoe UI Emoji", max(size, 20), "bold"))

        # Text font adaptivně
        text_size = int(min(root.winfo_width(), root.winfo_height()) * 0.05)
        text_widget.config(font=("Segoe UI", max(text_size, 14), "bold"), wraplength=root.winfo_width() * 0.8)

        if pulses[0] < 4:  # 2× tam a zpět
            root.after(40, pulse)
        else:
            fade_out(widget, text_widget)

    pulse()


def fade_out(symbol, text):
    """Postupně skryje výsledky"""
    alpha = 1.0

    def step():
        nonlocal alpha
        alpha -= 0.1
        if alpha <= 0:
            for w in (symbol, text):
                w.destroy()
            return
        faded = f"#{int(34 + (255-34)*alpha):02x}{int(34 + (255-34)*alpha):02x}{int(34 + (255-34)*alpha):02x}"
        symbol.config(fg=faded)
        text.config(fg=faded)
        root.after(50, step)

    step()


def on_submit():
    isic = entry.get().strip()
    if isic:
        scan_isic(isic)
    entry.delete(0, tk.END)


# === UI ===
root = tk.Tk()
root.title("🍽️ Jídelní systém")
root.geometry("900x600")
root.configure(bg="#222")

root.rowconfigure(2, weight=1)
root.columnconfigure(0, weight=1)

title = tk.Label(root, text="Jídelní systém", fg="white", bg="#222", font=("Segoe UI", 28, "bold"))
title.grid(row=0, column=0, pady=10)

entry_label = tk.Label(root, text="Načti ISIC kartu:", fg="#aaa", bg="#222", font=("Segoe UI", 16))
entry_label.grid(row=1, column=0)

entry = tk.Entry(root, font=("Segoe UI", 22), justify="center", bg="#333", fg="white", bd=0, relief="flat")
entry.grid(row=2, column=0, ipadx=10, ipady=5, pady=10, sticky="n")
entry.bind("<Return>", lambda e: on_submit())

frame_result = tk.Frame(root, bg="#222")
frame_result.grid(row=3, column=0, pady=30, sticky="nsew")

footer = tk.Label(root, text="© 2025 školní projekt", fg="#555", bg="#222", font=("Segoe UI", 10))
footer.grid(row=4, column=0, pady=5)

root.mainloop()

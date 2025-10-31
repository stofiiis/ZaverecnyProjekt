import sqlite3
import customtkinter as ctk
from datetime import datetime, date

DB_PATH = "database.db"

def update_sizes(event=None):
    """Update sizes of widgets based on window size"""
    width = root.winfo_width()
    height = root.winfo_height()

    # Title font
    title_size = max(int(min(width, height) * 0.08), 20)
    title.configure(font=ctk.CTkFont(size=title_size, weight="bold"))

    # Entry label font
    label_size = max(int(min(width, height) * 0.04), 14)
    entry_label.configure(font=ctk.CTkFont(size=label_size))

    # Entry font and size
    entry_size = max(int(min(width, height) * 0.06), 18)
    entry.configure(font=ctk.CTkFont(size=entry_size))

    # Footer font
    footer_size = max(int(min(width, height) * 0.025), 10)
    footer.configure(font=ctk.CTkFont(size=footer_size))

    # Frame result adjustments
    frame_result.configure(width=width, height=int(height * 0.4))

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
    """Rozsvítí pozadí červeně nebo zeleně bez emoji"""
    for widget in frame_result.winfo_children():
        widget.destroy()

    # Nastav barvu pozadí
    frame_result.configure(fg_color=color)

    # Text
    text_label = ctk.CTkLabel(
        frame_result,
        text=message,
        font=ctk.CTkFont(size=20, weight="bold"),
        wraplength=800,
        justify="center",
        text_color="white"  # Bílý text pro kontrast
    )
    text_label.pack(pady=20, expand=True)

    # Automatické skrytí po 3 sekundách a reset barvy
    root.after(3000, lambda: [text_label.destroy(), frame_result.configure(fg_color="transparent")])


def on_submit():
    isic = entry.get().strip()
    if isic:
        scan_isic(isic)
    entry.delete(0, ctk.END)


# === UI ===
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

root = ctk.CTk()
root.title("🍽️ Jídelní systém")
root.geometry("900x600")

# Bind resize event
root.bind("<Configure>", update_sizes)

# Configure grid weights for responsiveness
root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=0)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=2)
root.rowconfigure(4, weight=0)
root.columnconfigure(0, weight=1)

title = ctk.CTkLabel(root, text="🍽️ Jídelní systém", font=ctk.CTkFont(size=28, weight="bold"))
title.grid(row=0, column=0, pady=(20, 10), sticky="n")

entry_label = ctk.CTkLabel(root, text="Načti ISIC kartu:", font=ctk.CTkFont(size=16))
entry_label.grid(row=1, column=0, pady=(10, 5), sticky="n")

entry = ctk.CTkEntry(root, placeholder_text="Zadej ISIC ID", font=ctk.CTkFont(size=22), justify="center")
entry.grid(row=2, column=0, padx=50, pady=20, sticky="ew")
entry.bind("<Return>", lambda e: on_submit())

frame_result = ctk.CTkFrame(root, fg_color="transparent")
frame_result.grid(row=3, column=0, pady=20, sticky="nsew")

footer = ctk.CTkLabel(root, text="© 2025 školní projekt", font=ctk.CTkFont(size=10))
footer.grid(row=4, column=0, pady=(10, 20), sticky="s")

# Initial size update
root.after(100, update_sizes)

root.mainloop()

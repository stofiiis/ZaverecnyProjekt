import sqlite3
import customtkinter as ctk
from datetime import datetime, date
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import time

DB_PATH = "database.db"
reader = SimpleMFRC522()

COLORS = {
    "bg_primary": "#0f172a",
    "bg_secondary": "#1e293b",
    "accent": "#3b82f6",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8"
}

def scan_isic(isic_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, name FROM users WHERE isic_id = ?", (isic_id,))
    user = c.fetchone()

    if not user:
        show_result("❌", f"Neznámý ISIC: {isic_id}", COLORS["error"], "Karta nenalezena")
    else:
        user_id, name = user
        today = str(date.today())

        c.execute("SELECT id, meal_type FROM orders WHERE user_id = ? AND date = ?", (user_id, today))
        order = c.fetchone()

        if not order:
            show_result("⚠️", f"{name}", COLORS["warning"], "Dnes nemá objednáno")
        else:
            order_id, meal = order
            c.execute("SELECT * FROM served WHERE order_id = ?", (order_id,))
            already = c.fetchone()

            if already:
                show_result("🚫", f"{name}", COLORS["error"], f"{meal} – UŽ VYDÁNO")
            else:
                c.execute("INSERT INTO served (order_id, served_time) VALUES (?, ?)", (order_id, datetime.now()))
                conn.commit()
                show_result("✅", f"{name}", COLORS["success"], f"{meal} – VYDÁNO")

    conn.close()


def show_result(symbol, name, color, status):
    for widget in frame_result.winfo_children():
        widget.destroy()

    result_card = ctk.CTkFrame(frame_result, fg_color=COLORS["bg_secondary"], corner_radius=15)
    result_card.pack(pady=10, padx=20, fill="both", expand=True)

    symbol_frame = ctk.CTkFrame(result_card, fg_color=color, corner_radius=50, width=70, height=70)
    symbol_frame.pack(pady=(15, 10))
    symbol_frame.pack_propagate(False)
    
    symbol_label = ctk.CTkLabel(symbol_frame, text=symbol, font=ctk.CTkFont(size=36), text_color="white")
    symbol_label.place(relx=0.5, rely=0.5, anchor="center")

    name_label = ctk.CTkLabel(result_card, text=name, font=ctk.CTkFont(size=22, weight="bold"), text_color=COLORS["text_primary"])
    name_label.pack(pady=(5, 3))

    status_label = ctk.CTkLabel(result_card, text=status, font=ctk.CTkFont(size=16), text_color=color)
    status_label.pack(pady=(0, 15))

    root.after(3000, lambda: result_card.destroy())


def read_card_loop():
    """Nekonečná smyčka pro čtení karet"""
    while True:
        try:
            id, _ = reader.read()
            isic = str(id)
            scan_isic(isic)
            time.sleep(2)
        except Exception as e:
            print("Chyba čtečky:", e)
            GPIO.cleanup()
            time.sleep(2)


# === UI ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("🍽️ Jídelní systém")
root.geometry("800x480")
root.resizable(False, False)
root.configure(fg_color=COLORS["bg_primary"])

header = ctk.CTkLabel(root, text="🍽️ Jídelní systém", font=ctk.CTkFont(size=28, weight="bold"), text_color=COLORS["text_primary"])
header.pack(pady=(15, 5))

subtitle = ctk.CTkLabel(root, text="Přiložte ISIC kartu pro výdej jídla", font=ctk.CTkFont(size=13), text_color=COLORS["text_secondary"])
subtitle.pack(pady=(0, 15))

frame_result = ctk.CTkFrame(root, fg_color="transparent")
frame_result.pack(fill="both", expand=True, padx=30, pady=10)

footer = ctk.CTkLabel(root, text="© 2025 Školní projekt", font=ctk.CTkFont(size=9), text_color=COLORS["text_secondary"])
footer.pack(pady=(5, 10))

# Spustí čtecí smyčku na pozadí
import threading
threading.Thread(target=read_card_loop, daemon=True).start()

root.mainloop()
# === Konec UI ===
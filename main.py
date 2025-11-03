import sqlite3
import customtkinter as ctk
from datetime import datetime, date

DB_PATH = "database.db"

COLORS = {
    "bg_primary": "#0f172a",      # Dark blue background
    "bg_secondary": "#1e293b",    # Lighter dark blue
    "accent": "#3b82f6",          # Blue accent
    "success": "#10b981",         # Green
    "warning": "#f59e0b",         # Orange
    "error": "#ef4444",           # Red
    "text_primary": "#f1f5f9",    # Light text
    "text_secondary": "#94a3b8"   # Muted text
}

def update_sizes(event=None):
    """Update sizes of widgets based on window size"""
    pass

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
    """Redesigned result display with better visual hierarchy"""
    for widget in frame_result.winfo_children():
        widget.destroy()

    # Main result card
    result_card = ctk.CTkFrame(frame_result, fg_color=COLORS["bg_secondary"], corner_radius=15)
    result_card.pack(pady=10, padx=20, fill="both", expand=True)

    # Symbol with colored background
    symbol_frame = ctk.CTkFrame(result_card, fg_color=color, corner_radius=50, width=70, height=70)
    symbol_frame.pack(pady=(15, 10))
    symbol_frame.pack_propagate(False)
    
    symbol_label = ctk.CTkLabel(
        symbol_frame,
        text=symbol,
        font=ctk.CTkFont(size=36),
        text_color="white"
    )
    symbol_label.place(relx=0.5, rely=0.5, anchor="center")

    # Name
    name_label = ctk.CTkLabel(
        result_card,
        text=name,
        font=ctk.CTkFont(size=22, weight="bold"),
        text_color=COLORS["text_primary"]
    )
    name_label.pack(pady=(5, 3))

    # Status
    status_label = ctk.CTkLabel(
        result_card,
        text=status,
        font=ctk.CTkFont(size=16),
        text_color=color
    )
    status_label.pack(pady=(0, 15))

    # Auto-hide after 3 seconds
    root.after(3000, lambda: result_card.destroy())


def on_submit():
    isic = entry.get().strip()
    if isic:
        scan_isic(isic)
    entry.delete(0, ctk.END)


# === UI ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("🍽️ Jídelní systém")
root.geometry("800x480")
root.resizable(False, False)  # Prevent resizing
root.configure(fg_color=COLORS["bg_primary"])

# root.bind("<Configure>", update_sizes)

root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=0)
root.rowconfigure(2, weight=0)
root.rowconfigure(3, weight=0)
root.rowconfigure(4, weight=1)
root.rowconfigure(5, weight=0)
root.columnconfigure(0, weight=1)

header_frame = ctk.CTkFrame(root, fg_color="transparent")
header_frame.grid(row=0, column=0, pady=(15, 5), sticky="n")

title = ctk.CTkLabel(
    header_frame, 
    text="🍽️ Jídelní systém", 
    font=ctk.CTkFont(size=28, weight="bold"),
    text_color=COLORS["text_primary"]
)
title.pack()

subtitle = ctk.CTkLabel(
    header_frame,
    text="Naskenujte ISIC kartu pro výdej jídla",
    font=ctk.CTkFont(size=11),
    text_color=COLORS["text_secondary"]
)
subtitle.pack(pady=(3, 0))

input_frame = ctk.CTkFrame(root, fg_color=COLORS["bg_secondary"], corner_radius=15)
input_frame.grid(row=2, column=0, padx=40, pady=15, sticky="ew")

entry_label = ctk.CTkLabel(
    input_frame, 
    text="ISIC ID", 
    font=ctk.CTkFont(size=13, weight="bold"),
    text_color=COLORS["text_secondary"]
)
entry_label.pack(pady=(15, 8))

entry = ctk.CTkEntry(
    input_frame, 
    placeholder_text="Načtěte kartu...", 
    font=ctk.CTkFont(size=18),
    justify="center",
    height=50,
    border_width=2,
    border_color=COLORS["accent"],
    fg_color=COLORS["bg_primary"],
    text_color=COLORS["text_primary"]
)
entry.pack(padx=30, pady=(0, 15), fill="x")
entry.bind("<Return>", lambda e: on_submit())

frame_result = ctk.CTkFrame(root, fg_color="transparent")
frame_result.grid(row=4, column=0, pady=10, padx=30, sticky="nsew")

footer = ctk.CTkLabel(
    root, 
    text="© 2025 Školní projekt", 
    font=ctk.CTkFont(size=9),
    text_color=COLORS["text_secondary"]
)
footer.grid(row=5, column=0, pady=(5, 10), sticky="s")

# root.after(100, update_sizes)

# Focus on entry field
entry.focus()

root.mainloop()

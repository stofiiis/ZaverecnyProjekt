#  Jídelní systém (Raspberry Pi + Python + SQL)

Digitální systém pro výdej obědů pomocí ISIC karet.  
Po přiložení karty se zobrazí, jaké jídlo má student objednané, a systém upozorní, pokud už jídlo bylo vydáno.

---

##  Funkce
- Identifikace strávníka podle ISIC karty  
- Zobrazení objednaného jídla  
- Upozornění při opakovaném výdeji  
- Fronta posledních 3 skenů  
- Možnost běhu na Raspberry Pi s displejem  

---

##  Použité technologie
- **Python 3**
- **SQLite** – lokální databáze
- **Tkinter** – GUI pro kuchařky
- *(Volitelně)* **USB čtečka ISIC** – funguje jako klávesnice

---

##  Instalace

### 1️⃣ Klonování projektu
```bash
git clone https://github.com/tvuj-repo/jidelni_system.git
cd jidelni_system

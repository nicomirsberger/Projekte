import customtkinter as ctk

class DashboardView:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.clear_frame()

        ctk.CTkLabel(self.app.main_frame, text="Dashboard & Hauptmenü", font=("Arial", 24, "bold")).pack(pady=10)

        # --- Statistiken abrufen ---
        stats = {"kunden": 0, "artikel": 0, "bestellungen": 0, "umsatz": 0.0, "warnungen": 0}

        row_k = self.app.db.fetch_one("SELECT COUNT(*) FROM kunden")
        if row_k: stats["kunden"] = row_k[0]

        row_a = self.app.db.fetch_one("SELECT COUNT(*) FROM artikel")
        if row_a: stats["artikel"] = row_a[0]

        row_b = self.app.db.fetch_one("SELECT COUNT(*) FROM bestellungen")
        if row_b: stats["bestellungen"] = row_b[0]

        row_w = self.app.db.fetch_one("SELECT COUNT(*) FROM artikel WHERE bestand <= 3")
        if row_w: stats["warnungen"] = row_w[0]

        row_u = self.app.db.fetch_one("""
            SELECT SUM(CAST(b.menge AS NUMERIC) * CAST(a.preis AS NUMERIC))
            FROM bestellungen b
            JOIN artikel a ON b.artikel_id = a.id
        """)
        stats["umsatz"] = float(row_u[0]) if row_u and row_u[0] else 0.0

        # --- Dashboard UI ---
        dash_frame = ctk.CTkFrame(self.app.main_frame, fg_color="transparent")
        dash_frame.pack(pady=10, fill="x", padx=20)
        dash_frame.columnconfigure((0, 1, 2), weight=1)

        def create_card(r, c, title, value, color="#4da6ff"):
            card = ctk.CTkFrame(dash_frame, corner_radius=10)
            card.grid(row=r, column=c, padx=10, pady=10, sticky="ew")
            ctk.CTkLabel(card, text=title, font=("Arial", 12)).pack(pady=5)
            ctk.CTkLabel(card, text=value, font=("Arial", 22, "bold"), text_color=color).pack(pady=5)

        # Karten generieren
        create_card(0, 0, "👥 Kunden", str(stats["kunden"]))
        create_card(0, 1, "📦 Artikel", str(stats["artikel"]))
        create_card(0, 2, "🛒 Bestellungen", str(stats["bestellungen"]))

        umsatz_str = f"{stats['umsatz']:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        create_card(1, 0, "💶 Umsatz", umsatz_str, "#2ecc71")

        warn_color = "#e74c3c" if stats["warnungen"] > 0 else "#2ecc71"
        create_card(1, 1, "⚠️ Bestandswarnung", str(stats["warnungen"]), warn_color)

        # Trennlinie
        ctk.CTkFrame(self.app.main_frame, height=2, fg_color="#333333").pack(fill="x", padx=40, pady=15)

        # --- Navigation ---
        btn_frame = ctk.CTkFrame(self.app.main_frame, fg_color="transparent")
        btn_frame.pack(pady=5)

        ctk.CTkButton(btn_frame, text="Kunden verwalten", command=self.app.show_customers, height=45, width=200).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="Artikel verwalten", command=self.app.show_articles, height=45, width=200).grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="📦 Lagerverwaltung", command=self.app.show_inventory, fg_color="#d35400", hover_color="#e67e22", height=45, width=200).grid(row=0, column=2, padx=10, pady=10)

        ctk.CTkButton(btn_frame, text="Bestellung anlegen", command=self.app.show_create_order, fg_color="#2b719e", height=45, width=200).grid(row=1, column=0, padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="Bestellungen ansehen", command=self.app.show_order_list, fg_color="#1f538d", height=45, width=200).grid(row=1, column=1, padx=10, pady=10)
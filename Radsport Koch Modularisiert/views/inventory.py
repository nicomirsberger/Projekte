import customtkinter as ctk

class InventoryView:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.clear_frame()

        ctk.CTkLabel(self.app.main_frame, text="📦 Lager & Wareneingang", font=("Arial", 20, "bold")).pack(pady=10)

        # --- Wareneingang ---
        einbuch_frame = ctk.CTkFrame(self.app.main_frame)
        einbuch_frame.pack(pady=10, padx=20, fill="x")

        artikel = self.app.db.fetch_all("SELECT id, name, bestand, artikelnummer FROM artikel ORDER BY name ASC")
        artikel_liste = []
        for a in artikel:
            a_id, a_name, a_bestand, a_artnr = a
            disp_artnr = a_artnr if a_artnr else "-"
            artikel_liste.append(f"[{disp_artnr}] {a_name} (Lager: {a_bestand} | ID: {a_id})")

        if artikel_liste:
            dropdown_artikel = ctk.CTkOptionMenu(einbuch_frame, values=artikel_liste, width=250)
            dropdown_artikel.pack(side="left", padx=10, pady=10)

            entry_menge = ctk.CTkEntry(einbuch_frame, placeholder_text="Menge", width=80)
            entry_menge.pack(side="left", padx=10)

            def buchen():
                a_id = dropdown_artikel.get().split("ID: ")[1].replace(")", "")
                menge = entry_menge.get()

                if menge.isdigit():
                    if self.app.db.execute("UPDATE artikel SET bestand = bestand + %s WHERE id = %s", (menge, a_id)):
                        self.show()

            ctk.CTkButton(einbuch_frame, text="Zubuchen", command=buchen, fg_color="green", width=100).pack(side="left", padx=10)

        # --- Bestandsliste ---
        scroll_frame = ctk.CTkScrollableFrame(self.app.main_frame, height=350)
        scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        bestand_artikel = self.app.db.fetch_all("SELECT name, bestand, artikelnummer FROM artikel ORDER BY bestand ASC")
        for a in bestand_artikel:
            a_name, a_bestand, a_artnr = a

            row = ctk.CTkFrame(scroll_frame)
            row.pack(fill="x", pady=2, padx=5)

            disp_artnr = a_artnr if a_artnr else "-"
            warn_color = "#ff4d4d" if a_bestand <= 3 else "white"

            ctk.CTkLabel(row, text=f"[{disp_artnr}] {a_name}", font=("Arial", 13, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"Bestand: {a_bestand}", text_color=warn_color).pack(side="right", padx=10)

        ctk.CTkButton(self.app.main_frame, text="Zurück", command=self.app.show_dashboard, fg_color="gray").pack(pady=10)
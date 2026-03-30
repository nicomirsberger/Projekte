import customtkinter as ctk
from invoice import generate_html_invoice

class OrderView:
    def __init__(self, app):
        self.app = app

    def show_create(self):
        """View zum Anlegen neuer Bestellungen."""
        self.app.clear_frame()

        ctk.CTkLabel(self.app.main_frame, text="🛒 Neue Bestellung", font=("Arial", 20, "bold")).pack(pady=20)

        kunden = self.app.db.fetch_all("SELECT id, name FROM kunden ORDER BY name ASC")
        kunden_liste = [f"{k[1]} (ID: {k[0]})" for k in kunden]

        artikel = self.app.db.fetch_all("SELECT id, name, bestand, artikelnummer FROM artikel ORDER BY name ASC")
        artikel_liste = [f"[{a[3] if a[3] else '-'}] {a[1]} (Lager: {a[2]} | ID: {a[0]})" for a in artikel]

        if not kunden_liste or not artikel_liste:
            ctk.CTkLabel(self.app.main_frame, text="Kunden oder Artikel fehlen in der Datenbank!").pack(pady=20)
            ctk.CTkButton(self.app.main_frame, text="Zurück", command=self.app.show_dashboard).pack()
            return

        dropdown_kunden = ctk.CTkOptionMenu(self.app.main_frame, values=kunden_liste, width=350)
        dropdown_kunden.pack(pady=5)

        dropdown_artikel = ctk.CTkOptionMenu(self.app.main_frame, values=artikel_liste, width=350)
        dropdown_artikel.pack(pady=5)

        entry_menge = ctk.CTkEntry(self.app.main_frame, placeholder_text="Menge", width=100)
        entry_menge.pack(pady=5)

        label_error = ctk.CTkLabel(self.app.main_frame, text="", text_color="red")
        label_error.pack()

        def kauf_abschliessen():
            k_id = dropdown_kunden.get().split("ID: ")[1].replace(")", "")
            a_id = dropdown_artikel.get().split("ID: ")[1].replace(")", "")
            menge_str = entry_menge.get()

            if menge_str.isdigit():
                menge = int(menge_str)
                # Eigene Verbindung für Transaktionssicherheit holen
                conn = self.app.db.get_connection()
                if conn:
                    try:
                        cur = conn.cursor()
                        # Bestand prüfen
                        cur.execute("SELECT bestand FROM artikel WHERE id=%s", (a_id,))
                        aktueller_bestand = cur.fetchone()[0]

                        if menge > aktueller_bestand:
                            label_error.configure(text=f"Nicht genug Lagerbestand! Nur noch {aktueller_bestand} verfügbar.")
                            return

                        # Bestellen und Bestand abziehen
                        cur.execute("INSERT INTO bestellungen (kunde_id, artikel_id, menge) VALUES (%s,%s,%s)", (k_id, a_id, menge))
                        cur.execute("UPDATE artikel SET bestand = bestand - %s WHERE id=%s", (menge, a_id))

                        conn.commit()
                        self.app.show_dashboard()
                    except Exception as e:
                        print(f"Fehler bei Bestellung: {e}")
                    finally:
                        cur.close()
                        conn.close()
            else:
                label_error.configure(text="Bitte eine gültige Zahl eingeben.")

        ctk.CTkButton(self.app.main_frame, text="Kauf abschließen", command=kauf_abschliessen, fg_color="green", height=40).pack(pady=20)
        ctk.CTkButton(self.app.main_frame, text="Abbrechen", command=self.app.show_dashboard, fg_color="gray").pack()


    def show_list(self):
        """View zur Übersicht und Verwaltung der Bestellungen."""
        self.app.clear_frame()

        ctk.CTkLabel(self.app.main_frame, text="📋 Alle Bestellungen", font=("Arial", 20, "bold")).pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(self.app.main_frame, height=450)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        def stornieren(b_id, a_id, menge):
            # Bestand zurückbuchen
            if self.app.db.execute("UPDATE artikel SET bestand = bestand + %s WHERE id = %s", (menge, a_id)):
                # Bestellung löschen
                if self.app.db.execute("DELETE FROM bestellungen WHERE id = %s", (b_id,)):
                    lade_liste()

        def lade_liste():
            for w in scroll_frame.winfo_children():
                w.destroy()

            query = """
                SELECT b.id, k.name, a.name, b.menge, b.datum, a.id, a.preis
                FROM bestellungen b
                JOIN kunden k ON b.kunde_id = k.id
                JOIN artikel a ON b.artikel_id = a.id
                ORDER BY b.datum DESC
            """
            bestellungen = self.app.db.fetch_all(query)

            for b in bestellungen:
                b_id, k_name, a_name, b_menge, b_datum, a_id, a_preis = b

                row = ctk.CTkFrame(scroll_frame)
                row.pack(fill="x", pady=5, padx=5)

                datum_format = b_datum.strftime('%d.%m.%Y %H:%M') if b_datum else "Unbekannt"
                anzeige = f"[{datum_format}] {k_name}: {b_menge}x {a_name}"

                ctk.CTkLabel(row, text=anzeige, font=("Arial", 13)).pack(side="left", padx=10)

                btn_storno = ctk.CTkButton(row, text="Storno", width=60, fg_color="red",
                                           command=lambda bid=b_id, aid=a_id, m=b_menge: stornieren(bid, aid, m))
                btn_storno.pack(side="right", padx=5)

                btn_rechnung = ctk.CTkButton(row, text="📄 Rechnung", width=80, fg_color="#f39c12",
                                             text_color="black", hover_color="#d68910",
                                             command=lambda bid=b_id, kn=k_name, an=a_name, bm=b_menge, bd=b_datum, ap=a_preis:
                                             generate_html_invoice(bid, kn, an, bm, bd, ap))
                btn_rechnung.pack(side="right", padx=5)

        lade_liste()
        ctk.CTkButton(self.app.main_frame, text="Zurück", command=self.app.show_dashboard, fg_color="gray").pack(pady=10)
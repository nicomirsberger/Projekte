import customtkinter as ctk
import psycopg2
from datetime import datetime

# Datenbank-URL von Render.com
DB_URL = "postgresql://projekt_database_user:7ju3C7cEL8O2abhZXF1xTOeK0y9M1EsF@dpg-d6t6lu7diees73couqdg-a.frankfurt-postgres.render.com/projekt_database"


class RadsportApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Radsport Koch GmbH - Verwaltung")
        self.geometry("750x800")
        ctk.set_appearance_mode("dark")

        # Zentrales Lade-Label für Benutzerfeedback
        self.loading_label = ctk.CTkLabel(
            self,
            text="⏳ VERBINDUNG ZUR CLOUD... BITTE WARTEN",
            fg_color="#f39c12",
            text_color="black",
            font=("Arial", 12, "bold")
        )

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Datenbank-Schema beim Start prüfen/erweitern
        self._ensure_db_schema()
        self.show_main_menu()

    def set_loading(self, is_loading):
        """Zeigt oder versteckt den Lade-Balken und erzwingt UI-Update."""
        if is_loading:
            self.loading_label.pack(side="top", fill="x")
            self.update()  # Wichtig, um UI-Freeze optisch zu überbrücken
        else:
            self.loading_label.pack_forget()

    def get_db_connection(self):
        """Erstellt Verbindung mit 5 Sek. Timeout gegen langes Einfrieren."""
        self.set_loading(True)
        try:
            return psycopg2.connect(DB_URL, connect_timeout=5)
        except Exception as e:
            print(f"Verbindungsfehler: {e}")
            return None
        finally:
            self.set_loading(False)

    def save_to_db(self, query, params):
        """Zentrale Funktion für INSERT/UPDATE/DELETE mit Ladestatus."""
        self.set_loading(True)
        conn = None
        try:
            conn = psycopg2.connect(DB_URL, connect_timeout=5)
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"Datenbankfehler: {e}")
            return False
        finally:
            if conn:
                conn.close()
            self.set_loading(False)

    def _ensure_db_schema(self):
        """Stellt sicher, dass alle benötigten Spalten in der Cloud existieren."""
        queries = [
            "ALTER TABLE artikel ADD COLUMN IF NOT EXISTS bestand INTEGER DEFAULT 0;",
            "ALTER TABLE artikel ADD COLUMN IF NOT EXISTS artikelnummer VARCHAR(50);",
            "ALTER TABLE artikel ADD COLUMN IF NOT EXISTS modell VARCHAR(100);"
        ]
        for q in queries:
            self.save_to_db(q, ())

    def clear_frame(self):
        """Löscht alle Elemente im Frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ==========================================
    # HAUPTMENÜ & DASHBOARD
    # ==========================================
    def show_main_menu(self):
        self.clear_frame()

        ctk.CTkLabel(self.main_frame, text="Dashboard & Hauptmenü", font=("Arial", 24, "bold")).pack(pady=10)

        # --- Statistiken abrufen ---
        stats = {"kunden": 0, "artikel": 0, "bestellungen": 0, "umsatz": 0.0, "warnungen": 0}
        conn = self.get_db_connection()

        if conn:
            try:
                cur = conn.cursor()

                cur.execute("SELECT COUNT(*) FROM kunden")
                stats["kunden"] = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM artikel")
                stats["artikel"] = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM bestellungen")
                stats["bestellungen"] = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM artikel WHERE bestand <= 3")
                stats["warnungen"] = cur.fetchone()[0]

                cur.execute("""
                            SELECT SUM(CAST(b.menge AS NUMERIC) * CAST(a.preis AS NUMERIC))
                            FROM bestellungen b
                                     JOIN artikel a ON b.artikel_id = a.id
                            """)
                val = cur.fetchone()[0]
                stats["umsatz"] = float(val) if val else 0.0

                cur.close()
                conn.close()
            except Exception as e:
                print(f"Fehler beim Laden des Dashboards: {e}")

        # --- Dashboard UI ---
        dash_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
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
        ctk.CTkFrame(self.main_frame, height=2, fg_color="#333333").pack(fill="x", padx=40, pady=15)

        # --- Navigation ---
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(pady=5)

        ctk.CTkButton(btn_frame, text="Kunden verwalten", command=self.show_kunde_anlegen, height=45, width=200).grid(
            row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="Artikel verwalten", command=self.show_artikel_anlegen, height=45,
                      width=200).grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="📦 Lagerverwaltung", command=self.show_lager_verwaltung, fg_color="#d35400",
                      hover_color="#e67e22", height=45, width=200).grid(row=0, column=2, padx=10, pady=10)

        ctk.CTkButton(btn_frame, text="Bestellung anlegen", command=self.show_bestellung_anlegen, fg_color="#2b719e",
                      height=45, width=200).grid(row=1, column=0, padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="Bestellungen ansehen", command=self.show_bestellungen_liste, fg_color="#1f538d",
                      height=45, width=200).grid(row=1, column=1, padx=10, pady=10)

    # ==========================================
    # KUNDENVERWALTUNG
    # ==========================================
    def show_kunde_anlegen(self):
        self.clear_frame()
        self.edit_kunde_id = None

        ctk.CTkLabel(self.main_frame, text="Kundenverwaltung", font=("Arial", 20, "bold")).pack(pady=10)

        # --- Formular ---
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(pady=5, padx=10, fill="x")

        entry_name = ctk.CTkEntry(form_frame, placeholder_text="Name", width=200)
        entry_name.grid(row=0, column=0, padx=10, pady=10)

        entry_email = ctk.CTkEntry(form_frame, placeholder_text="E-Mail", width=200)
        entry_email.grid(row=0, column=1, padx=10, pady=10)

        def speichern():
            name = entry_name.get()
            email = entry_email.get()

            if name:
                btn_save.configure(text="Speichert...", state="disabled")
                self.update()

                if self.edit_kunde_id is None:
                    erfolg = self.save_to_db("INSERT INTO kunden (name, email) VALUES (%s, %s)", (name, email))
                else:
                    erfolg = self.save_to_db("UPDATE kunden SET name=%s, email=%s WHERE id=%s",
                                             (name, email, self.edit_kunde_id))

                if erfolg:
                    abbrechen_bearbeiten()
                    lade_liste()
                else:
                    btn_save.configure(text="Speichern", state="normal")

        btn_save = ctk.CTkButton(form_frame, text="Speichern", command=speichern, fg_color="green", width=100)
        btn_save.grid(row=0, column=2, padx=10)

        def abbrechen_bearbeiten():
            self.edit_kunde_id = None
            entry_name.delete(0, 'end')
            entry_email.delete(0, 'end')
            btn_save.configure(text="Speichern", state="normal")
            btn_cancel_edit.grid_remove()

        btn_cancel_edit = ctk.CTkButton(form_frame, text="X", command=abbrechen_bearbeiten, fg_color="gray", width=30)

        # --- Liste laden ---
        scroll_frame = ctk.CTkScrollableFrame(self.main_frame, height=350)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        def loeschen(k_id):
            if self.save_to_db("DELETE FROM kunden WHERE id=%s", (k_id,)):
                lade_liste()

        def bearbeiten(k_id, k_name, k_email):
            self.edit_kunde_id = k_id
            entry_name.delete(0, 'end')
            entry_name.insert(0, k_name)
            entry_email.delete(0, 'end')
            if k_email:
                entry_email.insert(0, k_email)

            btn_save.configure(text="Aktualisieren")
            btn_cancel_edit.grid(row=0, column=3, padx=5, pady=10)

        def lade_liste():
            for w in scroll_frame.winfo_children():
                w.destroy()

            conn = self.get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT id, name, email FROM kunden ORDER BY name ASC")
                    for k in cur.fetchall():
                        k_id, k_name, k_email = k

                        row = ctk.CTkFrame(scroll_frame)
                        row.pack(fill="x", pady=2, padx=5)

                        ctk.CTkLabel(row, text=f"#{k_id} | {k_name}").pack(side="left", padx=10)

                        btn_del = ctk.CTkButton(row, text="X", width=30, fg_color="red",
                                                command=lambda id=k_id: loeschen(id))
                        btn_del.pack(side="right", padx=5)

                        btn_edit = ctk.CTkButton(row, text="✏️", width=30, fg_color="#1f538d",
                                                 command=lambda id=k_id, n=k_name, e=k_email: bearbeiten(id, n, e))
                        btn_edit.pack(side="right", padx=5)

                    cur.close()
                    conn.close()
                except Exception as e:
                    print(e)

        lade_liste()
        ctk.CTkButton(self.main_frame, text="Zurück", command=self.show_main_menu, fg_color="gray").pack(pady=10)

    # ==========================================
    # ARTIKELVERWALTUNG
    # ==========================================
    def show_artikel_anlegen(self):
        self.clear_frame()
        self.edit_artikel_id = None

        ctk.CTkLabel(self.main_frame, text="Artikelverwaltung", font=("Arial", 20, "bold")).pack(pady=10)

        # --- Formular ---
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(pady=5, padx=10, fill="x")

        entry_artnr = ctk.CTkEntry(form_frame, placeholder_text="ArtNr", width=120)
        entry_artnr.grid(row=0, column=0, padx=5, pady=5)

        entry_name = ctk.CTkEntry(form_frame, placeholder_text="Bezeichnung", width=180)
        entry_name.grid(row=0, column=1, padx=5, pady=5)

        entry_modell = ctk.CTkEntry(form_frame, placeholder_text="Modell", width=120)
        entry_modell.grid(row=1, column=0, padx=5, pady=5)

        entry_preis = ctk.CTkEntry(form_frame, placeholder_text="Preis", width=180)
        entry_preis.grid(row=1, column=1, padx=5, pady=5)

        def speichern():
            artnr = entry_artnr.get()
            name = entry_name.get()
            modell = entry_modell.get()
            preis_str = entry_preis.get().replace(",", ".")

            if name and preis_str:
                btn_save.configure(text="Speichert...", state="disabled")
                self.update()

                if self.edit_artikel_id is None:
                    q = "INSERT INTO artikel (name, preis, bestand, artikelnummer, modell) VALUES (%s,%s,0,%s,%s)"
                    p = (name, preis_str, artnr, modell)
                else:
                    q = "UPDATE artikel SET name=%s, preis=%s, artikelnummer=%s, modell=%s WHERE id=%s"
                    p = (name, preis_str, artnr, modell, self.edit_artikel_id)

                if self.save_to_db(q, p):
                    abbrechen_bearbeiten()
                    lade_liste()
                else:
                    btn_save.configure(text="Speichern", state="normal")

        btn_save = ctk.CTkButton(form_frame, text="Speichern", command=speichern, fg_color="green", width=100)
        btn_save.grid(row=0, column=2, rowspan=2, padx=10)

        def abbrechen_bearbeiten():
            self.edit_artikel_id = None
            entry_name.delete(0, 'end')
            entry_preis.delete(0, 'end')
            entry_artnr.delete(0, 'end')
            entry_modell.delete(0, 'end')
            btn_save.configure(text="Speichern", state="normal")
            btn_cancel_edit.grid_remove()

        btn_cancel_edit = ctk.CTkButton(form_frame, text="X", command=abbrechen_bearbeiten, fg_color="gray", width=30)

        # --- Liste laden ---
        scroll_frame = ctk.CTkScrollableFrame(self.main_frame, height=300)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        def loeschen(a_id):
            if self.save_to_db("DELETE FROM artikel WHERE id=%s", (a_id,)):
                lade_liste()

        def bearbeiten(a_id, a_artnr, a_name, a_modell, a_preis):
            self.edit_artikel_id = a_id

            entry_artnr.delete(0, 'end')
            if a_artnr: entry_artnr.insert(0, a_artnr)

            entry_name.delete(0, 'end')
            entry_name.insert(0, a_name)

            entry_modell.delete(0, 'end')
            if a_modell: entry_modell.insert(0, a_modell)

            entry_preis.delete(0, 'end')
            entry_preis.insert(0, str(a_preis))

            btn_save.configure(text="Aktualisieren")
            btn_cancel_edit.grid(row=0, column=3, rowspan=2, padx=5, pady=10)

        def lade_liste():
            for w in scroll_frame.winfo_children():
                w.destroy()

            conn = self.get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT id, artikelnummer, name, modell, preis, bestand FROM artikel ORDER BY name ASC")
                    for a in cur.fetchall():
                        a_id, a_artnr, a_name, a_modell, a_preis, a_bestand = a

                        row = ctk.CTkFrame(scroll_frame)
                        row.pack(fill="x", pady=2, padx=5)

                        disp_artnr = a_artnr if a_artnr else "-"
                        ctk.CTkLabel(row, text=f"[{disp_artnr}] {a_name} | {a_preis}€").pack(side="left", padx=10)

                        btn_del = ctk.CTkButton(row, text="X", width=30, fg_color="red",
                                                command=lambda id=a_id: loeschen(id))
                        btn_del.pack(side="right", padx=5)

                        btn_edit = ctk.CTkButton(row, text="✏️", width=30, fg_color="#1f538d",
                                                 command=lambda id=a_id, art=a_artnr, n=a_name, m=a_modell,
                                                                p=a_preis: bearbeiten(id, art, n, m, p))
                        btn_edit.pack(side="right", padx=5)

                    cur.close()
                    conn.close()
                except Exception as e:
                    print(e)

        lade_liste()
        ctk.CTkButton(self.main_frame, text="Zurück", command=self.show_main_menu, fg_color="gray").pack(pady=10)

    # ==========================================
    # LAGERVERWALTUNG
    # ==========================================
    def show_lager_verwaltung(self):
        self.clear_frame()

        ctk.CTkLabel(self.main_frame, text="📦 Lager & Wareneingang", font=("Arial", 20, "bold")).pack(pady=10)

        # --- Wareneingang ---
        einbuch_frame = ctk.CTkFrame(self.main_frame)
        einbuch_frame.pack(pady=10, padx=20, fill="x")

        artikel_liste = []
        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, name, bestand, artikelnummer FROM artikel ORDER BY name ASC")
                for a in cur.fetchall():
                    a_id, a_name, a_bestand, a_artnr = a
                    disp_artnr = a_artnr if a_artnr else "-"
                    artikel_liste.append(f"[{disp_artnr}] {a_name} (Lager: {a_bestand} | ID: {a_id})")
                cur.close()
                conn.close()
            except Exception as e:
                print(e)

        if artikel_liste:
            dropdown_artikel = ctk.CTkOptionMenu(einbuch_frame, values=artikel_liste, width=250)
            dropdown_artikel.pack(side="left", padx=10, pady=10)

            entry_menge = ctk.CTkEntry(einbuch_frame, placeholder_text="Menge", width=80)
            entry_menge.pack(side="left", padx=10)

            def buchen():
                a_id = dropdown_artikel.get().split("ID: ")[1].replace(")", "")
                menge = entry_menge.get()

                if menge.isdigit():
                    if self.save_to_db("UPDATE artikel SET bestand = bestand + %s WHERE id = %s", (menge, a_id)):
                        self.show_lager_verwaltung()

            ctk.CTkButton(einbuch_frame, text="Zubuchen", command=buchen, fg_color="green", width=100).pack(side="left",
                                                                                                            padx=10)

        # --- Bestandsliste ---
        scroll_frame = ctk.CTkScrollableFrame(self.main_frame, height=350)
        scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT name, bestand, artikelnummer FROM artikel ORDER BY bestand ASC")
                for a in cur.fetchall():
                    a_name, a_bestand, a_artnr = a

                    row = ctk.CTkFrame(scroll_frame)
                    row.pack(fill="x", pady=2, padx=5)

                    disp_artnr = a_artnr if a_artnr else "-"
                    warn_color = "#ff4d4d" if a_bestand <= 3 else "white"

                    ctk.CTkLabel(row, text=f"[{disp_artnr}] {a_name}", font=("Arial", 13, "bold")).pack(side="left",
                                                                                                        padx=10)
                    ctk.CTkLabel(row, text=f"Bestand: {a_bestand}", text_color=warn_color).pack(side="right", padx=10)

                cur.close()
                conn.close()
            except Exception as e:
                print(e)

        ctk.CTkButton(self.main_frame, text="Zurück", command=self.show_main_menu, fg_color="gray").pack(pady=10)

    # ==========================================
    # BESTELLUNG ANLEGEN
    # ==========================================
    def show_bestellung_anlegen(self):
        self.clear_frame()

        ctk.CTkLabel(self.main_frame, text="🛒 Neue Bestellung", font=("Arial", 20, "bold")).pack(pady=20)

        kunden_liste = []
        artikel_liste = []

        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, name FROM kunden ORDER BY name ASC")
                for k in cur.fetchall():
                    kunden_liste.append(f"{k[1]} (ID: {k[0]})")

                cur.execute("SELECT id, name, bestand, artikelnummer FROM artikel ORDER BY name ASC")
                for a in cur.fetchall():
                    disp_artnr = a[3] if a[3] else "-"
                    artikel_liste.append(f"[{disp_artnr}] {a[1]} (Lager: {a[2]} | ID: {a[0]})")

                cur.close()
                conn.close()
            except Exception as e:
                print(e)

        if not kunden_liste or not artikel_liste:
            ctk.CTkLabel(self.main_frame, text="Kunden oder Artikel fehlen in der Datenbank!").pack(pady=20)
            ctk.CTkButton(self.main_frame, text="Zurück", command=self.show_main_menu).pack()
            return

        dropdown_kunden = ctk.CTkOptionMenu(self.main_frame, values=kunden_liste, width=350)
        dropdown_kunden.pack(pady=5)

        dropdown_artikel = ctk.CTkOptionMenu(self.main_frame, values=artikel_liste, width=350)
        dropdown_artikel.pack(pady=5)

        entry_menge = ctk.CTkEntry(self.main_frame, placeholder_text="Menge", width=100)
        entry_menge.pack(pady=5)

        label_error = ctk.CTkLabel(self.main_frame, text="", text_color="red")
        label_error.pack()

        def kauf_abschliessen():
            k_id = dropdown_kunden.get().split("ID: ")[1].replace(")", "")
            a_id = dropdown_artikel.get().split("ID: ")[1].replace(")", "")
            menge_str = entry_menge.get()

            if menge_str.isdigit():
                menge = int(menge_str)
                conn = self.get_db_connection()
                if conn:
                    try:
                        cur = conn.cursor()
                        # Bestand prüfen
                        cur.execute("SELECT bestand FROM artikel WHERE id=%s", (a_id,))
                        aktueller_bestand = cur.fetchone()[0]

                        if menge > aktueller_bestand:
                            label_error.configure(
                                text=f"Nicht genug Lagerbestand! Nur noch {aktueller_bestand} verfügbar.")
                            cur.close()
                            conn.close()
                            return

                        # Bestellen und Bestand abziehen
                        cur.execute("INSERT INTO bestellungen (kunde_id, artikel_id, menge) VALUES (%s,%s,%s)",
                                    (k_id, a_id, menge))
                        cur.execute("UPDATE artikel SET bestand = bestand - %s WHERE id=%s", (menge, a_id))

                        conn.commit()
                        cur.close()
                        conn.close()

                        self.show_main_menu()
                    except Exception as e:
                        print(f"Fehler bei Bestellung: {e}")
            else:
                label_error.configure(text="Bitte eine gültige Zahl eingeben.")

        ctk.CTkButton(self.main_frame, text="Kauf abschließen", command=kauf_abschliessen, fg_color="green",
                      height=40).pack(pady=20)
        ctk.CTkButton(self.main_frame, text="Abbrechen", command=self.show_main_menu, fg_color="gray").pack()

    # ==========================================
    # BESTELLUNGEN ANSEHEN
    # ==========================================
    def show_bestellungen_liste(self):
        self.clear_frame()

        ctk.CTkLabel(self.main_frame, text="📋 Alle Bestellungen", font=("Arial", 20, "bold")).pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(self.main_frame, height=450)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        def stornieren(b_id, a_id, menge):
            # Bestand zurückbuchen
            if self.save_to_db("UPDATE artikel SET bestand = bestand + %s WHERE id = %s", (menge, a_id)):
                # Bestellung löschen
                if self.save_to_db("DELETE FROM bestellungen WHERE id = %s", (b_id,)):
                    lade_liste()

        def lade_liste():
            for w in scroll_frame.winfo_children():
                w.destroy()

            conn = self.get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("""
                                SELECT b.id, k.name, a.name, b.menge, b.datum, a.id
                                FROM bestellungen b
                                         JOIN kunden k ON b.kunde_id = k.id
                                         JOIN artikel a ON b.artikel_id = a.id
                                ORDER BY b.datum DESC
                                """)

                    for b in cur.fetchall():
                        b_id, k_name, a_name, b_menge, b_datum, a_id = b

                        row = ctk.CTkFrame(scroll_frame)
                        row.pack(fill="x", pady=5, padx=5)

                        datum_format = b_datum.strftime('%d.%m.%Y %H:%M') if b_datum else "Unbekannt"
                        anzeige = f"[{datum_format}] {k_name}: {b_menge}x {a_name}"

                        ctk.CTkLabel(row, text=anzeige, font=("Arial", 13)).pack(side="left", padx=10)

                        btn_storno = ctk.CTkButton(row, text="Storno", width=60, fg_color="red",
                                                   command=lambda bid=b_id, aid=a_id, m=b_menge: stornieren(bid, aid,
                                                                                                            m))
                        btn_storno.pack(side="right", padx=5)

                    cur.close()
                    conn.close()
                except Exception as e:
                    print(e)

        lade_liste()
        ctk.CTkButton(self.main_frame, text="Zurück", command=self.show_main_menu, fg_color="gray").pack(pady=10)


if __name__ == "__main__":
    app = RadsportApp()
    app.mainloop()
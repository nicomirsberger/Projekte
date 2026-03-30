import customtkinter as ctk


class ArticleView:
    def __init__(self, app):
        self.app = app
        self.edit_artikel_id = None

    def show(self):
        self.app.clear_frame()
        self.edit_artikel_id = None

        ctk.CTkLabel(self.app.main_frame, text="Artikelverwaltung", font=("Arial", 20, "bold")).pack(pady=10)

        # --- Formular ---
        form_frame = ctk.CTkFrame(self.app.main_frame)
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
                self.app.update()

                if self.edit_artikel_id is None:
                    q = "INSERT INTO artikel (name, preis, bestand, artikelnummer, modell) VALUES (%s,%s,0,%s,%s)"
                    p = (name, preis_str, artnr, modell)
                else:
                    q = "UPDATE artikel SET name=%s, preis=%s, artikelnummer=%s, modell=%s WHERE id=%s"
                    p = (name, preis_str, artnr, modell, self.edit_artikel_id)

                if self.app.db.execute(q, p):
                    abbrechen_bearbeiten()
                    lade_liste()
                else:
                    btn_save.configure(text="Speichern", state="normal")

        btn_save = ctk.CTkButton(form_frame, text="Speichern", command=speichern, fg_color="green", width=100)
        btn_save.grid(row=0, column=2, rowspan=2, padx=10)

        btn_cancel_edit = ctk.CTkButton(form_frame, text="X", fg_color="gray", width=30)

        def abbrechen_bearbeiten():
            self.edit_artikel_id = None
            entry_name.delete(0, 'end')
            entry_preis.delete(0, 'end')
            entry_artnr.delete(0, 'end')
            entry_modell.delete(0, 'end')
            btn_save.configure(text="Speichern", state="normal")
            btn_cancel_edit.grid_remove()

        btn_cancel_edit.configure(command=abbrechen_bearbeiten)

        # --- Liste laden ---
        scroll_frame = ctk.CTkScrollableFrame(self.app.main_frame, height=300)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        def loeschen(a_id):
            if self.app.db.execute("DELETE FROM artikel WHERE id=%s", (a_id,)):
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

            artikel = self.app.db.fetch_all(
                "SELECT id, artikelnummer, name, modell, preis, bestand FROM artikel ORDER BY name ASC")
            for a in artikel:
                a_id, a_artnr, a_name, a_modell, a_preis, a_bestand = a

                row = ctk.CTkFrame(scroll_frame)
                row.pack(fill="x", pady=2, padx=5)

                disp_artnr = a_artnr if a_artnr else "-"
                ctk.CTkLabel(row, text=f"[{disp_artnr}] {a_name} | {a_preis}€").pack(side="left", padx=10)

                btn_del = ctk.CTkButton(row, text="X", width=30, fg_color="red", command=lambda id=a_id: loeschen(id))
                btn_del.pack(side="right", padx=5)

                btn_edit = ctk.CTkButton(row, text="✏️", width=30, fg_color="#1f538d",
                                         command=lambda id=a_id, art=a_artnr, n=a_name, m=a_modell,
                                                        p=a_preis: bearbeiten(id, art, n, m, p))
                btn_edit.pack(side="right", padx=5)

        lade_liste()
        ctk.CTkButton(self.app.main_frame, text="Zurück", command=self.app.show_dashboard, fg_color="gray").pack(
            pady=10)
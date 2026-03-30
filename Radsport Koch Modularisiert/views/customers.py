import customtkinter as ctk

class CustomerView:
    def __init__(self, app):
        self.app = app
        self.edit_kunde_id = None

    def show(self):
        self.app.clear_frame()
        self.edit_kunde_id = None

        ctk.CTkLabel(self.app.main_frame, text="Kundenverwaltung", font=("Arial", 20, "bold")).pack(pady=10)

        # --- Formular ---
        form_frame = ctk.CTkFrame(self.app.main_frame)
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
                self.app.update()

                if self.edit_kunde_id is None:
                    erfolg = self.app.db.execute("INSERT INTO kunden (name, email) VALUES (%s, %s)", (name, email))
                else:
                    erfolg = self.app.db.execute("UPDATE kunden SET name=%s, email=%s WHERE id=%s", (name, email, self.edit_kunde_id))

                if erfolg:
                    abbrechen_bearbeiten()
                    lade_liste()
                else:
                    btn_save.configure(text="Speichern", state="normal")

        btn_save = ctk.CTkButton(form_frame, text="Speichern", command=speichern, fg_color="green", width=100)
        btn_save.grid(row=0, column=2, padx=10)

        btn_cancel_edit = ctk.CTkButton(form_frame, text="X", fg_color="gray", width=30)

        def abbrechen_bearbeiten():
            self.edit_kunde_id = None
            entry_name.delete(0, 'end')
            entry_email.delete(0, 'end')
            btn_save.configure(text="Speichern", state="normal")
            btn_cancel_edit.grid_remove()

        btn_cancel_edit.configure(command=abbrechen_bearbeiten)

        # --- Liste laden ---
        scroll_frame = ctk.CTkScrollableFrame(self.app.main_frame, height=350)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        def loeschen(k_id):
            if self.app.db.execute("DELETE FROM kunden WHERE id=%s", (k_id,)):
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

            kunden = self.app.db.fetch_all("SELECT id, name, email FROM kunden ORDER BY name ASC")
            for k_id, k_name, k_email in kunden:
                row = ctk.CTkFrame(scroll_frame)
                row.pack(fill="x", pady=2, padx=5)

                ctk.CTkLabel(row, text=f"#{k_id} | {k_name}").pack(side="left", padx=10)

                btn_del = ctk.CTkButton(row, text="X", width=30, fg_color="red", command=lambda id=k_id: loeschen(id))
                btn_del.pack(side="right", padx=5)

                btn_edit = ctk.CTkButton(row, text="✏️", width=30, fg_color="#1f538d",
                                         command=lambda id=k_id, n=k_name, e=k_email: bearbeiten(id, n, e))
                btn_edit.pack(side="right", padx=5)

        lade_liste()
        ctk.CTkButton(self.app.main_frame, text="Zurück", command=self.app.show_dashboard, fg_color="gray").pack(pady=10)
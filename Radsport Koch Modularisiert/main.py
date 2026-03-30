import customtkinter as ctk

# Lokale Module importieren
from database import Database
from views.dashboard import DashboardView
from views.customers import CustomerView
from views.articles import ArticleView
from views.inventory import InventoryView
from views.orders import OrderView

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

        # Initialisiere Datenbank-Verbindung (App-weit)
        self.db = Database(loading_callback=self.set_loading)

        # Initialisiere die verschiedenen Views (App wird übergeben)
        self.dashboard_view = DashboardView(self)
        self.customer_view = CustomerView(self)
        self.article_view = ArticleView(self)
        self.inventory_view = InventoryView(self)
        self.order_view = OrderView(self)

        # Startbildschirm laden
        self.show_dashboard()

    def set_loading(self, is_loading):
        """Wird aufgerufen, wenn Datenbankverbindungen laden."""
        if is_loading:
            self.loading_label.pack(side="top", fill="x")
            self.update()  # UI sofort aktualisieren
        else:
            self.loading_label.pack_forget()
            self.update()

    def clear_frame(self):
        """Löscht alle aktuell im Main Frame angezeigten Widgets."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ====================================================
    # UI ROUTING (Navigation zwischen den Modulen)
    # ====================================================
    def show_dashboard(self):
        self.dashboard_view.show()

    def show_customers(self):
        self.customer_view.show()

    def show_articles(self):
        self.article_view.show()

    def show_inventory(self):
        self.inventory_view.show()

    def show_create_order(self):
        self.order_view.show_create()

    def show_order_list(self):
        self.order_view.show_list()


if __name__ == "__main__":
    app = RadsportApp()
    app.mainloop()
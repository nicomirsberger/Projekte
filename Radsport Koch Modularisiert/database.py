import psycopg2
from config import DB_URL

class Database:
    def __init__(self, loading_callback=None):
        self.loading_callback = loading_callback
        self._ensure_db_schema()

    def _set_loading(self, state):
        """Aktiviert oder deaktiviert die Lade-UI in der Hauptanwendung."""
        if self.loading_callback:
            self.loading_callback(state)

    def get_connection(self):
        """Erstellt eine rohe Verbindung, z.B. für mehrstufige Transaktionen."""
        self._set_loading(True)
        try:
            return psycopg2.connect(DB_URL, connect_timeout=5)
        except Exception as e:
            print(f"Verbindungsfehler: {e}")
            return None
        finally:
            self._set_loading(False)

    def execute(self, query, params=()):
        """Führt INSERT, UPDATE oder DELETE Befehle aus."""
        self._set_loading(True)
        conn = None
        try:
            conn = psycopg2.connect(DB_URL, connect_timeout=5)
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"Datenbankfehler (execute): {e}")
            return False
        finally:
            if conn:
                conn.close()
            self._set_loading(False)

    def fetch_one(self, query, params=()):
        """Führt SELECT aus und gibt genau EINEN Datensatz zurück."""
        self._set_loading(True)
        conn = None
        try:
            conn = psycopg2.connect(DB_URL, connect_timeout=5)
            cur = conn.cursor()
            cur.execute(query, params)
            result = cur.fetchone()
            cur.close()
            return result
        except Exception as e:
            print(f"Datenbankfehler (fetch_one): {e}")
            return None
        finally:
            if conn:
                conn.close()
            self._set_loading(False)

    def fetch_all(self, query, params=()):
        """Führt SELECT aus und gibt ALLE passenden Datensätze als Liste zurück."""
        self._set_loading(True)
        conn = None
        try:
            conn = psycopg2.connect(DB_URL, connect_timeout=5)
            cur = conn.cursor()
            cur.execute(query, params)
            results = cur.fetchall()
            cur.close()
            return results
        except Exception as e:
            print(f"Datenbankfehler (fetch_all): {e}")
            return []
        finally:
            if conn:
                conn.close()
            self._set_loading(False)

    def _ensure_db_schema(self):
        """Stellt sicher, dass alle benötigten Spalten in der Cloud existieren."""
        queries = [
            "ALTER TABLE artikel ADD COLUMN IF NOT EXISTS bestand INTEGER DEFAULT 0;",
            "ALTER TABLE artikel ADD COLUMN IF NOT EXISTS artikelnummer VARCHAR(50);",
            "ALTER TABLE artikel ADD COLUMN IF NOT EXISTS modell VARCHAR(100);"
        ]
        for q in queries:
            self.execute(q)
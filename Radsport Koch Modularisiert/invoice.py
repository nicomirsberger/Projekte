import os
import webbrowser
from datetime import datetime

def generate_html_invoice(b_id, k_name, a_name, b_menge, b_datum, a_preis):
    """Generiert eine professionelle HTML-Rechnung und öffnet sie im Browser."""
    # Ordner erstellen, falls nicht vorhanden
    os.makedirs("rechnungen", exist_ok=True)

    # Dateipfad
    filepath = os.path.abspath(f"rechnungen/Rechnung_{b_id}.html")

    # Berechnungen & Formatierungen
    datum_str = b_datum.strftime('%d.%m.%Y') if b_datum else datetime.now().strftime('%d.%m.%Y')
    gesamtpreis = b_menge * a_preis

    preis_str = f"{a_preis:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    gesamt_str = f"{gesamtpreis:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # Das HTML & CSS Design der Rechnung
    html_content = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>Rechnung #{b_id} - Radsport Koch</title>
        <style>
            body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #333; margin: 40px auto; max-width: 800px; }}
            .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #e74c3c; padding-bottom: 20px; }}
            .company-info {{ text-align: right; }}
            .company-info h2 {{ color: #e74c3c; margin-bottom: 5px; }}
            .invoice-details {{ margin-top: 40px; background-color: #f8f9fa; padding: 20px; border-radius: 8px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 40px; }}
            th, td {{ border-bottom: 1px solid #ddd; padding: 15px 10px; text-align: left; }}
            th {{ background-color: #2c3e50; color: white; }}
            .total-row {{ font-weight: bold; font-size: 1.3em; background-color: #f8f9fa; }}
            .footer {{ margin-top: 80px; font-size: 0.85em; color: #777; border-top: 1px solid #ddd; padding-top: 20px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1 style="color: #2c3e50; margin-bottom: 0;">RECHNUNG</h1>
                <p>Rechnungsnummer: <strong>#{b_id}</strong><br>
                Datum: {datum_str}</p>
            </div>
            <div class="company-info">
                <h2>Radsport Koch GmbH</h2>
                <p>Friedrich-Weilerplatz 2<br>91074 Herzogenaurach<br>mail@radsportkoch.de</p>
            </div>
        </div>

        <div class="invoice-details">
            <h3 style="margin-top: 0; color: #7f8c8d;">Rechnung an:</h3>
            <p style="font-size: 1.2em; margin-bottom: 0;"><strong>{k_name}</strong></p>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Pos.</th>
                    <th>Artikelbeschreibung</th>
                    <th>Menge</th>
                    <th>Einzelpreis</th>
                    <th>Gesamtpreis</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>{a_name}</td>
                    <td>{b_menge}</td>
                    <td>{preis_str} €</td>
                    <td>{gesamt_str} €</td>
                </tr>
                <tr class="total-row">
                    <td colspan="4" style="text-align: right;">Rechnungsbetrag:</td>
                    <td style="color: #993c31;">{gesamt_str} €</td>
                </tr>
            </tbody>
        </table>

        <div class="footer">
            <p>Vielen Dank für Ihren Einkauf bei der Radsport Koch GmbH!<br>
            Bitte überweisen Sie den Rechnungsbetrag innerhalb von 14 Tagen auf folgendes Konto.</p>
            <p><strong>IBAN:</strong> DE13 3546 4130 0012 89 | <strong>BIC:</strong> GENO DE F1 N02</p>
        </div>
    </body>
    </html>
    """

    # Datei schreiben
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Im Standard-Browser öffnen
    webbrowser.open(f"file://{filepath}")
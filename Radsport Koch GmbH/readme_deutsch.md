🚲 Radsport Koch GmbH - Desktop App

📖 Projektbeschreibung & Methodik

Dieses Projekt ist eine Desktop-Anwendung für die Radsport Koch GmbH, entwickelt in Python.

Das Hauptziel war es, eine grafische Benutzeroberfläche (GUI) zu entwerfen, die sowohl hochfunktional als auch optisch ansprechend ist. Für die Implementierung habe ich gezielt die Bibliothek CustomTkinter ausgewählt. Im Gegensatz zum Standard-Tkinter bietet CustomTkinter ein modernes Erscheinungsbild mit abgerundeten Ecken und nativer Unterstützung für Dark- und Light-Modes, was die User Experience (UX) insgesamt deutlich verbessert.

🛠 Meine schrittweise Vorgehensweise:

Projekt-Setup & Isolierung: Anfänglich gab es Herausforderungen bezüglich globaler Python-Installationen unter macOS (System-Python vs. Projekt-Python). Ich habe dies gelöst, indem ich eine virtuelle Umgebung (.venv) innerhalb der IDE (PyCharm) korrekt konfiguriert habe. Dies stellt sicher, dass alle Abhängigkeiten sicher isoliert sind.

UI/UX Design: Die grafische Oberfläche wurde iterativ aufgebaut. Elemente wie Buttons und Eingabefelder wurden logisch angeordnet, um den Arbeitsablauf für das Fahrradgeschäft so intuitiv wie möglich zu gestalten.

Logik-Implementierung: Verknüpfung der visuellen Schnittstellenelemente mit der zugrundeliegenden Python-Logik im Skript Radsport_Koch_fertig.py.

Deployment: Um die Anwendung einfach teilen und bewerten zu können, wurden der finale Code und die notwendigen Ressourcen in einem .zip-Archiv verpackt und über GitHub Releases veröffentlicht.

🚀 Installation & Nutzung

Um die Anwendung reibungslos auszuführen, folge bitte diesen Schritten:

1. Download:

Lade die .zip-Datei aus dem GitHub-Repository herunter und entpacke sie an einem bevorzugten Ort auf deinem Computer.

2. Voraussetzungen prüfen:

Stelle sicher, dass Python 3 auf deinem System installiert ist.

3. Abhängigkeiten installieren:

Öffne ein Terminal (oder die Eingabeaufforderung) innerhalb des entpackten Ordners und installiere die benötigte externe Bibliothek mit folgendem Befehl:

pip install customtkinter

4. Das Programm starten!